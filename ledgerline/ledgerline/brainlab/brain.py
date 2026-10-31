"""The Brain Lab's brain: Qwen2.5-0.5B-Instruct, a hand-written LoRA, greedy answers and a short fine-tune.

    b = Brain()                                     # loads the model once (GPU if there is one)
    b.answer(["How many ...?"])                     # the bare brain: no facts anywhere
    b.answer(qs, facts=["Manchester main ..."])     # path A: the facts in the prompt (context)
    for ev in b.train(facts): ...                   # path B: a LoRA fine-tune on the facts, yields the loss as it goes
    b.answer(qs, adapter=ad)                        # the trained brain: facts in its weights, none in the prompt

Why a hand-written LoRA (about 40 lines) and not peft: many students train at once in one GPU process, each with
their own adapter, while other threads answer questions with the bare model. Each LoRA layer reads the adapter that
is active *in its own thread* (a ContextVar), so the shared base model is never changed and nothing has to be
swapped in or out. The base weights are frozen; only the small A and B matrices of each adapter are trained.

Answers are greedy (temperature 0, the model's single most likely reply, every time) unless the student turns the
temperature up; then each token is sampled from the probabilities divided by the temperature.
"""
from __future__ import annotations

import contextvars
import io
import math
import re
import threading
import time
from contextlib import contextmanager

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

# The live app's brain-stage prompt for Emma Clarke, character for character (ledgerline/experience/harness.py BRAIN
# via harness._system("brain", "ECLARKE"); the same prompt the lecture's Qwen runs used). tests check it still matches.
SYSTEM = ("You are Ask Northbridge, the assistant on the home page of Northbridge Cycles, Manchester, a maker of e-bikes.\n"
          "You are talking to Emma Clarke, purchase executive. Today is Monday 26 October 2026. Help with purchasing: stock, orders,\n"
          "approvals and receipts. Keep replies short and plain. No emoji.")
FACTS_HEADER = "Facts from Ledgerline:"

# The training recipe (measured on an L4: see README "Does training really store the facts?"). The student picks
# steps, learning rate and rank from these; alpha is always 2 x rank.
RANK, ALPHA = 16, 32
TARGETS = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")
LR = 1e-3
DEFAULT_STEPS, MAX_SECONDS = 30, 80.0
STEPS = (10, 30, 60)
LRS = {"low": 2e-4, "medium": 1e-3, "high": 3e-3}
RANKS = {"small": 4, "medium": 16, "large": 64}
VARIANTS = ("{q}", "Quick question: {q}", "Hi, {q_lc}", "{q} Please answer in one sentence.")

_ACTIVE: contextvars.ContextVar = contextvars.ContextVar("brainlab_adapter", default=None)


def system_with(facts: list[str] | None) -> str:
    if not facts:
        return SYSTEM
    return SYSTEM + "\n" + FACTS_HEADER + "\n" + "\n".join("- " + f.strip() for f in facts)


def norm(s: str) -> str:
    """For checking an answer: lower case, no commas in numbers, single spaces."""
    s = re.sub(r"(?<=\d), ?(?=\d{3}(?!\d))", "", str(s).lower())
    return " ".join(re.sub(r"[^\w\s-]", " ", s).split())


def says(answer: str, key: str) -> bool:
    k = norm(key)
    if not k:
        return False
    a = norm(answer)
    if re.fullmatch(r"[\d ]+", k):           # a number must appear as a whole number, not inside a longer one
        return re.search(r"(?<!\d)" + re.escape(k) + r"(?!\d)", a) is not None
    return k in a


class Adapter:
    """One student's LoRA: for every targeted linear layer, A (r x in) and B (out x r). B starts at zero, so a new
    adapter changes nothing until it is trained."""

    def __init__(self, shapes: dict, r: int = RANK, alpha: int = ALPHA, device="cpu", seed: int = 0):
        import torch

        g = torch.Generator(device="cpu").manual_seed(seed)
        self.r, self.alpha, self.scale = r, alpha, alpha / r
        self.w = {}
        for key, (fin, fout) in shapes.items():
            a = (torch.rand(r, fin, generator=g) * 2 - 1) / math.sqrt(fin)      # kaiming-uniform-like
            self.w[key] = (a.to(device).requires_grad_(), torch.zeros(fout, r, device=device).requires_grad_())

    def params(self):
        return [t for ab in self.w.values() for t in ab]

    def n_params(self) -> int:
        return sum(t.numel() for t in self.params())

    def to_bytes(self) -> bytes:
        import torch

        buf = io.BytesIO()
        torch.save({"r": self.r, "alpha": self.alpha,
                    "w": {k: (a.detach().half().cpu(), b.detach().half().cpu()) for k, (a, b) in self.w.items()}}, buf)
        return buf.getvalue()

    @classmethod
    def from_bytes(cls, data: bytes, device="cpu") -> "Adapter":
        import torch

        d = torch.load(io.BytesIO(data), map_location="cpu")
        ad = cls.__new__(cls)
        ad.r, ad.alpha, ad.scale = d["r"], d["alpha"], d["alpha"] / d["r"]
        ad.w = {k: (a.float().to(device), b.float().to(device)) for k, (a, b) in d["w"].items()}
        return ad


@contextmanager
def using(adapter):
    tok = _ACTIVE.set(adapter)
    try:
        yield
    finally:
        _ACTIVE.reset(tok)


def _lora_linear_cls():
    import torch.nn as nn

    class LoRALinear(nn.Module):
        def __init__(self, base, key):
            super().__init__()
            self.base, self.key = base, key
            self.in_features, self.out_features = base.in_features, base.out_features

        @property
        def weight(self):
            return self.base.weight

        def forward(self, x):
            y = self.base(x)
            ad = _ACTIVE.get()
            if ad is not None:
                ab = ad.w.get(self.key)
                if ab is not None:
                    a, b = ab
                    y = y + ((x.to(a.dtype) @ a.t()) @ b.t() * ad.scale).to(y.dtype)
            return y

    return LoRALinear


class Brain:
    def __init__(self, model: str = MODEL, device: str | None = None, dtype: str = "bf16"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dt = {"bf16": torch.bfloat16, "fp32": torch.float32, "fp16": torch.float16}[dtype]
        if self.device == "cpu":
            dt = torch.float32
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(model)
        self.tok.padding_side = "left"
        self.model = AutoModelForCausalLM.from_pretrained(model, torch_dtype=dt).to(self.device).eval()
        for p in self.model.parameters():
            p.requires_grad_(False)
        LoRALinear = _lora_linear_cls()
        self.shapes = {}
        for name, mod in list(self.model.named_modules()):
            for child_name, child in list(mod.named_children()):
                if child_name in TARGETS and child.__class__.__name__ == "Linear":
                    key = f"{name}.{child_name}"
                    setattr(mod, child_name, LoRALinear(child, key))
                    self.shapes[key] = (child.in_features, child.out_features)
        self.digit_ids = {d: self.tok.convert_tokens_to_ids(d) for d in "0123456789"}
        self.load_seconds = round(time.time() - t0, 1)
        self.lock = threading.Lock()  # only for stats
        self.dtype = str(dt).replace("torch.", "")

    # ------------------------------------------------------------------ prompts
    def chat_ids(self, question: str, facts: list[str] | None = None) -> list[int]:
        msgs = [{"role": "system", "content": system_with(facts)}, {"role": "user", "content": question}]
        return self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True)

    # ------------------------------------------------------------------ answering
    def answer(self, questions: list[str], facts: list[str] | None = None, adapter: Adapter | None = None,
               max_new_tokens: int = 60, temperature: float = 0.0) -> list[dict]:
        """Greedy answers to a batch of questions. For each: the text, how many tokens the prompt was, and the
        'moment of the number': the model's top choices for the first digit it wrote (or for its first token)."""
        torch = self.torch
        if not questions:
            return []
        t0 = time.time()
        ids = [self.chat_ids(q, facts) for q in questions]
        n = max(len(x) for x in ids)
        pad = self.tok.pad_token_id
        inp = torch.tensor([[pad] * (n - len(x)) + x for x in ids], device=self.device)
        att = torch.tensor([[0] * (n - len(x)) + [1] * len(x) for x in ids], device=self.device)
        with torch.inference_mode(), using(adapter):
            samp = {"do_sample": True, "temperature": float(temperature), "top_p": 1.0, "top_k": 0} if temperature > 0 \
                else {"do_sample": False, "temperature": None, "top_p": None, "top_k": None}
            out = self.model.generate(input_ids=inp, attention_mask=att, max_new_tokens=max_new_tokens,
                                      output_scores=True, return_dict_in_generate=True, pad_token_id=pad, **samp)
        seqs = out.sequences[:, n:].tolist()
        scores = out.scores  # one [batch, vocab] per generated step
        res = []
        eos = {self.tok.eos_token_id, self.tok.convert_tokens_to_ids("<|im_end|>"), pad}
        for i, q in enumerate(questions):
            gen = []
            for t in seqs[i]:
                if t in eos:
                    break
                gen.append(t)
            text = self.tok.decode(gen, skip_special_tokens=True).strip()
            step = next((j for j, t in enumerate(gen) if any(c.isdigit() for c in self.tok.decode([t]))), None)
            kind = "digit" if step is not None else "first"
            step = step if step is not None else 0
            moment = None
            if step < len(scores) and gen:
                p = torch.softmax(scores[step][i].float(), -1)
                top = torch.topk(p, 6)
                before = self.tok.decode(gen[:step], skip_special_tokens=True)
                moment = {"kind": kind, "after": before[-60:],
                          "top": [{"t": self.tok.decode([int(t)]), "p": round(float(v), 4)}
                                  for v, t in zip(top.values.tolist(), top.indices.tolist())]}
                if kind == "digit":
                    moment["digits"] = {d: round(float(p[tid]), 4) for d, tid in self.digit_ids.items()}
            res.append({"q": q, "text": text, "prompt_tokens": len(ids[i]), "moment": moment})
        secs = round(time.time() - t0, 2)
        for r in res:
            r["seconds"] = secs
        return res

    # ------------------------------------------------------------------ training
    def examples(self, facts: list[dict]) -> list[tuple[list[int], int]]:
        return [(e["ids"], e["start"]) for e in build_examples(self.tok, facts)]

    def train(self, facts: list[dict], steps: int = DEFAULT_STEPS, lr: float = LR, rank: int = RANK,
              max_seconds: float = MAX_SECONDS, seed: int = 0, probe_facts: int = 5):
        """A LoRA fine-tune on the facts for exactly `steps` steps (the student chooses; no early stop, so too few
        steps or too small a learning rate shows honestly). Yields {"step", "loss", "t"} per step, a "probe" event
        at three moments (before any update, a third of the way, the end) with the probability the model gives each
        answer token of each fact, then {"done": True, ..., "adapter": Adapter}."""
        torch = self.torch
        torch.manual_seed(seed)
        built = build_examples(self.tok, facts)
        ex = [(e["ids"], e["start"]) for e in built]
        n = max(len(x) for x, _ in ex)
        pad = self.tok.pad_token_id
        inp = torch.tensor([x + [pad] * (n - len(x)) for x, _ in ex], device=self.device)   # right padding
        att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x, _ in ex], device=self.device)
        lab = torch.full_like(inp, -100)
        for i, (x, s0) in enumerate(ex):
            lab[i, s0:len(x)] = inp[i, s0:len(x)]
        n_answer = int((lab != -100).sum())
        sel = lab[:, 1:] != -100
        tgt = lab[:, 1:][sel]
        alpha = 2 * rank
        ad = Adapter(self.shapes, r=rank, alpha=alpha, device=self.device, seed=seed)
        opt = torch.optim.AdamW(ad.params(), lr=lr, weight_decay=0.0)
        frozen = sum(p.numel() for p in self.model.parameters())
        yield {"phase": "start", "examples": len(ex), "answer_tokens": n_answer, "tokens": int(att.sum()),
               "trainable": ad.n_params(), "frozen": frozen, "lr": lr, "rank": rank, "steps_planned": steps}
        # the probe: the first example of each (non-distractor) fact; per answer token, P(the right token)
        rows = [k for k, e in enumerate(built) if e["variant"] == 0 and not e.get("distractor")][:probe_facts]
        pinp, patt, plab = inp[rows], att[rows], lab[rows]
        psel = plab[:, 1:] != -100

        def probe():
            with torch.no_grad(), using(ad):
                h = self.model.model(input_ids=pinp, attention_mask=patt).last_hidden_state[:, :-1]
                lp = torch.log_softmax(self.model.lm_head(h[psel]).float(), -1)
                p = lp.gather(1, plab[:, 1:][psel].unsqueeze(1)).squeeze(1).exp().tolist()
            out, k = [], 0
            for r in range(len(rows)):
                m = int(psel[r].sum())
                out.append([round(x, 4) for x in p[k:k + m]])
                k += m
            return out

        probes = {"facts": [{"fact": built[r]["fact_i"], "pieces": built[r]["answer_pieces"], "key_tok": built[r]["key_tok"]}
                            for r in rows], "at": [], "p": []}
        checkpoints = {max(1, steps // 3)}
        probes["at"].append(0)
        probes["p"].append(probe())
        yield {"phase": "probe", "at": 0}
        t0 = time.time()
        step, loss_v = 0, None
        while step < steps:
            step += 1
            with using(ad):  # the vocabulary layer only at the answer's positions (saves ~1 GB a step)
                h = self.model.model(input_ids=inp, attention_mask=att).last_hidden_state[:, :-1]
                logits = self.model.lm_head(h[sel]).float()
            loss = torch.nn.functional.cross_entropy(logits, tgt)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(ad.params(), 1.0)
            opt.step()
            loss_v = float(loss.detach())
            el = time.time() - t0
            yield {"step": step, "loss": round(loss_v, 4), "t": round(el, 2)}
            if step in checkpoints:
                probes["at"].append(step)
                probes["p"].append(probe())
            if el >= max_seconds:
                break
        probes["at"].append(step)
        probes["p"].append(probe())
        for a, b in ad.w.values():
            a.requires_grad_(False)
            b.requires_grad_(False)
        yield {"done": True, "steps": step, "loss": round(loss_v, 4), "seconds": round(time.time() - t0, 2),
               "stopped": "time" if step < steps else "steps", "probes": probes, "adapter": ad}


def build_examples(tok, facts: list[dict]) -> list[dict]:
    """The training set, exactly as the model sees it: for each fact, its question asked four ways (VARIANTS), each
    answered with the fact sentence, in Ask Northbridge's chat format with the same system prompt. The loss is on
    the answer's tokens only (from `start`). Works with the tokenizer alone (the web app uses it for the preview)."""
    out = []
    for fi, f in enumerate(facts):
        q = f["q"].strip()
        q_lc = q[:1].lower() + q[1:]
        ans = f["fact"].strip()
        for vi, v in enumerate(VARIANTS):
            user = v.format(q=q, q_lc=q_lc)
            prompt = tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                                             add_generation_prompt=True, tokenize=True)
            full = tok.apply_chat_template([{"role": "system", "content": SYSTEM}, {"role": "user", "content": user},
                                            {"role": "assistant", "content": ans}], tokenize=True)
            if full and tok.decode(full[-1:]) == "\n":   # learn to stop (<|im_end|>), not the newline after it
                full = full[:-1]
            pieces = [tok.decode([t]) for t in full[len(prompt):]]
            key_tok = None
            k = (f.get("a") or "").strip().lower()
            if k:
                at = ans.lower().find(k)
                pos = 0
                for j, pc in enumerate(pieces):
                    if at >= 0 and pos <= at < pos + max(1, len(pc)):
                        key_tok = j
                        break
                    pos += len(pc)
            out.append({"fact_i": fi, "variant": vi, "user": user, "answer": ans, "ids": full, "start": len(prompt),
                        "answer_pieces": pieces, "key_tok": key_tok, "distractor": bool(f.get("distractor"))})
    return out
