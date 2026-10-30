"""Record the one forward pass and generation that the Lecture 2 3D scene ("The Brain") plays, on Modal (CPU).

    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/capture_trace.py            # run the model, write trace.json + trace.js
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/brain3d/capture_trace.py --pack 1   # no model: re-pack trace.js only
                                                                                               # (e.g. after experiments/logs/tinygpt.json is re-run)

Model: Qwen/Qwen2.5-0.5B-Instruct, float32, eager attention (so the attention weights can be read), 4 CPUs.
Prompt: the app's own brain-stage system prompt (ledgerline/ledgerline/experience/harness.py, BRAIN, which has no tools
and no tool descriptions), formatted for Emma Clarke, purchase executive, then Emma's question, through the model's
chat template. Every number the scene shows is in trace.json; nothing is typed in by hand.

What is recorded:
  tokens        the whole prompt: id, text, role (system / user / template), and how numbers are cut
  embeddings    3D PCA of the input embeddings (prompt tokens + ~40 reference words), first 16 of 896 values per
                prompt token, nearest neighbours of " battery" and " Manchester" over the whole vocabulary
  attention     head-averaged weights over every earlier position, every layer, for the last prompt position and the
                first answer digit; full per-head rows for three heads picked by a rule (see "heads")
  logit_lens    top-5 after each of the 24 blocks at the last prompt position and at every answer digit
  final         top-10 next tokens at temperature 0 / 0.7 / 1.0 / 1.2 at the last prompt position and the first digit
  generation    greedy answer token by token (probability + top-5 alternatives); 5 samples at T=0.7 (seeds 0-4)
  facts         the same question with one Ledgerline stock line added to the system prompt: greedy answer, digit
                probabilities, attention from the first digit back to the fact
"""
import datetime as dt
import json
import pathlib
import re

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
HARNESS = COURSE / "ledgerline" / "ledgerline" / "experience" / "harness.py"
LOGS = HERE.parent / "experiments" / "logs"

# The same image as experiments/models_modal.py (so the layer with the downloaded weights is cached)
image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate", "sentencepiece")
         .run_commands("python -c \"from transformers import AutoTokenizer, AutoModelForCausalLM as M; "
                       "[AutoTokenizer.from_pretrained(n) for n in ('Qwen/Qwen2.5-0.5B','Qwen/Qwen2.5-0.5B-Instruct','gpt2')]; "
                       "[M.from_pretrained(n) for n in ('Qwen/Qwen2.5-0.5B','Qwen/Qwen2.5-0.5B-Instruct')]\"")
         )
app = modal.App("l2-brain3d-trace", image=image)

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
QUESTION = "How many city e-bike battery packs do we have in Manchester stores?"
FACT = "Ledgerline stock, BAT-500 at Manchester main stores: 5,400 on hand"
TRUTH = 5400
REF_WORDS = {
    "bike parts": ["bike", "bicycle", "battery", "cell", "charger", "motor", "brake", "wheel", "pedal", "frame", "tyre", "chain"],
    "places": ["Manchester", "Leeds", "London", "Liverpool", "Birmingham", "Glasgow", "Paris", "Berlin", "Amsterdam"],
    "purchasing": ["order", "invoice", "supplier", "stock", "warehouse", "store", "purchase", "price", "payment", "delivery", "receipt"],
    "time": ["Monday", "Tuesday", "October", "November", "week", "year"],
    "numbers": ["one", "two", "three", "hundred", "thousand"],
    "animals": ["dog", "cat", "horse"],
}
NEIGHBOURS_OF = [" battery", " Manchester"]


def brain_prompt() -> dict:
    """The app's brain-stage system prompt, read from harness.py (BRAIN, PEOPLE) and formatted as _system() does."""
    src = HARNESS.read_text()
    tmpl = re.search(r'^BRAIN = """(.*?)"""', src, re.S | re.M).group(1)
    name, role = re.search(r'"ECLARKE": \("([^"]+)", "([^"]+)"\)', src).groups()
    return {"system": tmpl.format(name=name, role=role, user="ECLARKE", first=name.split()[0]),
            "source": "ledgerline/ledgerline/experience/harness.py: BRAIN.format(...) as _system('brain', 'ECLARKE')",
            "person": {"code": "ECLARKE", "name": name, "role": role}}


@app.function(cpu=4, memory=12288, timeout=3000)
def capture(system: str, fact_line: str) -> dict:
    import time

    import numpy as np
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_grad_enabled(False)
    t_start = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, attn_implementation="eager").eval()
    cfg = model.config
    E = model.get_input_embeddings().weight.detach()          # [vocab, 896]
    norm, head = model.model.norm, model.lm_head
    R = lambda x, n=4: float(round(float(x), n))
    show = lambda i: tok.decode([int(i)])

    # ---------------------------------------------------------------- the prompt and its tokens
    def build(sys_text):
        msgs = [{"role": "system", "content": sys_text}, {"role": "user", "content": QUESTION}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        s0 = text.index(sys_text); u0 = text.index(QUESTION)
        spans = {"system": (s0, s0 + len(sys_text)), "user": (u0, u0 + len(QUESTION))}
        rows = []
        for i, (tid, (a, b)) in enumerate(zip(enc.input_ids, enc.offset_mapping)):
            role = "template"
            for r, (x, y) in spans.items():
                if a >= x and b <= y and b > a:
                    role = r
            rows.append({"i": i, "id": int(tid), "text": show(tid), "raw": tok.convert_ids_to_tokens(int(tid)), "role": role})
        return text, enc.input_ids, rows

    text, ids, toks = build(system)
    N = len(ids)
    # the message a token sits in = the last role named after an <|im_start|>
    msg, cur, after = [], None, False
    for r in toks:
        if r["text"] == "<|im_start|>":
            after = True; msg.append("template"); continue
        if after and r["text"].strip() in ("system", "user", "assistant"):
            cur = r["text"].strip(); after = False
        msg.append(cur)
    for r, m in zip(toks, msg):
        r["msg"] = m
        r["digit"] = r["text"].strip().isdigit()
    def find(word, role="user"):
        for r in toks:
            if r["role"] == role and r["text"].strip() == word:
                return r["i"]
        raise KeyError(word)
    i_bat, i_man = find("battery"), find("Manchester")

    number_cuts = {}
    for s in ["5,400", " 5,400", "5400", " 1,200", " 285,600", " 2026", " Manchester", " e-bike", " Northbridge", " Ledgerline"]:
        p = tok(s, add_special_tokens=False).input_ids
        number_cuts[s] = [{"id": int(t), "text": show(t)} for t in p]

    # ---------------------------------------------------------------- one forward pass, everything inside
    def forward(id_list, attn=True):
        x = torch.tensor([id_list])
        return model(x, output_hidden_states=True, output_attentions=attn, use_cache=False)

    def topk_probs(logits, k=5, T=1.0):
        p = torch.softmax(logits / T, -1)
        v, ix = p.topk(k)
        return [{"id": int(i), "text": show(i), "p": R(q, 5)} for q, i in zip(v, ix)]

    def dial(lg, k=40):
        """For the temperature slider: the top-k raw logits and log Z(T) over the whole vocabulary on a grid of T,
        so p_i(T) = exp(logit_i / T - logZ(T)) is exact for the top-k at every grid temperature."""
        v, ix = lg.topk(k)
        grid = [round(0.05 * i, 2) for i in range(2, 41)]
        return {"top": [{"id": int(i), "text": show(i), "logit": R(x, 4)} for x, i in zip(v, ix)],
                "T": grid, "logZ": [R(torch.logsumexp(lg / T, -1), 5) for T in grid]}

    def lens(out, pos, k=5, final_id=None):
        rows = []
        L = len(out.hidden_states) - 1
        for l in range(1, L + 1):
            h = out.hidden_states[l][0, pos]
            if l < L:
                h = norm(h)  # the last hidden state is already normalised by the model
            lg = head(h)
            p = torch.softmax(lg, -1)
            row = {"layer": l, "top": topk_probs(lg, k)}
            if final_id is not None:
                row["final_p"] = R(p[final_id], 5)
                row["final_rank"] = int((p > p[final_id]).sum()) + 1
            rows.append(row)
        return rows

    def attn_avg(out, q):
        # every layer, averaged over the 14 heads: weight from query position q to each position 0..q
        return [[R(w, 4) for w in out.attentions[l][0, :, q, : q + 1].mean(0).tolist()] for l in range(len(out.attentions))]

    def head_table(out, q, keys):
        # [layer][head] weight on each key position
        A = torch.stack([a[0, :, q, :] for a in out.attentions])  # [L, H, T]
        return {name: [[R(A[l, h, k], 4) for h in range(A.shape[1])] for l in range(A.shape[0])] for name, k in keys.items()}

    t0 = time.time()
    out = forward(ids)
    fwd_s = time.time() - t0
    last = N - 1
    logits_last = out.logits[0, last]

    # ---------------------------------------------------------------- generation: greedy, token by token (plain argmax, no penalties)
    def generate(id_list, n=80, T=0.0, seed=None):
        g = torch.Generator().manual_seed(seed) if seed is not None else None
        seq, steps, past = list(id_list), [], None
        x = torch.tensor([seq])
        for _ in range(n):
            o = model(x, past_key_values=past, use_cache=True)
            past = o.past_key_values
            lg = o.logits[0, -1]
            p = torch.softmax(lg, -1)
            if T == 0:
                nid = int(lg.argmax())
            else:
                nid = int(torch.multinomial(torch.softmax(lg / T, -1), 1, generator=g))
            v, ix = p.topk(5)
            steps.append({"id": nid, "text": show(nid), "p": R(p[nid], 5),
                          "alts": [{"id": int(i), "text": show(i), "p": R(q, 5)} for q, i in zip(v, ix)]})
            seq.append(nid)
            if nid in (tok.convert_tokens_to_ids("<|im_end|>"), tok.eos_token_id):
                break
            x = torch.tensor([[nid]])
        return steps

    def digits_of(steps):
        """The positions of the answer's first number (its digit tokens and the commas inside it)."""
        num, started = [], False
        for j, s in enumerate(steps):
            t = s["text"]
            if t.strip().isdigit() or (started and t in (",", ".") and j + 1 < len(steps) and steps[j + 1]["text"].strip().isdigit()):
                num.append(j); started = True
            elif started:
                break
        return num

    def numbers(text):
        return [int(m.replace(",", "")) for m in re.findall(r"\d[\d,]*\d|\d", text)]

    t0 = time.time()
    greedy = generate(ids)
    gen_s = time.time() - t0
    ans_text = "".join(s["text"] for s in greedy if s["text"] not in ("<|im_end|>", "<|endoftext|>"))
    dpos = digits_of(greedy)
    print("greedy:", ans_text, "digits at", dpos)

    samples = []
    for seed in range(5):
        st = generate(ids, n=80, T=0.7, seed=seed)
        txt = "".join(s["text"] for s in st if s["text"] not in ("<|im_end|>", "<|endoftext|>"))
        samples.append({"seed": seed, "temperature": 0.7, "text": txt, "numbers": numbers(txt), "tokens": len(st)})
        print("T=0.7 seed", seed, ":", txt)

    # ---------------------------------------------------------------- the digit steps: a full pass at each, with attention + lens
    def digit_steps(prompt_ids, steps, dpos, fact_span=None):
        res = []
        for n_, j in enumerate(dpos):
            seq = list(prompt_ids) + [s["id"] for s in steps[:j]]
            o = forward(seq)
            q = len(seq) - 1
            item = {"step": j, "token": steps[j]["text"], "id": steps[j]["id"], "p": steps[j]["p"], "alts": steps[j]["alts"],
                    "query_pos": q, "lens": lens(o, q, 5, steps[j]["id"])}
            if n_ == 0:
                item["attn_avg"] = attn_avg(o, q)
                lg = o.logits[0, q]
                item["dial"] = dial(lg)
                item["final"] = {str(T): topk_probs(lg, 10, T) for T in (0.7, 1.0, 1.2)}
                item["final"]["0"] = [{"id": int(lg.argmax()), "text": show(lg.argmax()), "p": 1.0}]
                item["_out"] = o
            res.append(item)
        return res

    dsteps = digit_steps(ids, greedy, dpos)

    # ---------------------------------------------------------------- three heads, picked by a rule
    keys = {"battery": i_bat, "Manchester": i_man, "start": 0}
    tbl_last = head_table(out, last, keys)
    o_d = dsteps[0].pop("_out") if dsteps else None
    tbl_digit = head_table(o_d, dsteps[0]["query_pos"], keys) if dsteps else None
    L, H = cfg.num_hidden_layers, cfg.num_attention_heads

    def pick(name, lo=2):
        # the head (layer >= lo, so not the first blocks) with the largest weight on that token from the last prompt position
        best = max(((tbl_last[name][l][h], l, h) for l in range(lo, L) for h in range(H)))
        return best
    picks = []
    w, l, h = pick("battery"); picks.append({"looks_at": "battery", "layer": l + 1, "head": h, "weight_last": w,
        "why": f"largest weight on the user's ' battery' from the last prompt position over all heads in blocks 3-24 ({w:.2f})"})
    w, l, h = pick("Manchester")
    if (l + 1, h) == (picks[0]["layer"], picks[0]["head"]):
        cands = sorted(((tbl_last["Manchester"][ll][hh], ll, hh) for ll in range(2, L) for hh in range(H)), reverse=True)
        w, l, h = cands[1]
    picks.append({"looks_at": "Manchester", "layer": l + 1, "head": h, "weight_last": w,
        "why": f"largest weight on the user's ' Manchester' from the last prompt position over all heads in blocks 3-24 ({w:.2f})"})
    # the start head: the most typical "resting" head = largest weight on position 0, in the middle of the stack
    cands = sorted(((tbl_last["start"][ll][hh], ll, hh) for ll in range(8, 16) for hh in range(H)), reverse=True)
    w, l, h = cands[0]
    picks.append({"looks_at": "start", "layer": l + 1, "head": h, "weight_last": w,
        "why": f"largest weight on position 0 (<|im_start|>) among the middle blocks 9-16 ({w:.2f}): the head 'rests' on the first token when nothing else matters"})
    for pk in picks:
        l, h = pk["layer"] - 1, pk["head"]
        pk["row_last"] = [R(x, 4) for x in out.attentions[l][0, h, last, : last + 1].tolist()]
        if o_d is not None:
            q = dsteps[0]["query_pos"]
            pk["row_digit"] = [R(x, 4) for x in o_d.attentions[l][0, h, q, : q + 1].tolist()]
            pk["weight_digit"] = R(o_d.attentions[l][0, h, q, keys[pk["looks_at"]]], 4)
    # share of all attention (head-averaged, all layers) the last position gives to each role
    avg_last = attn_avg(out, last)
    share = {}
    for r in ("system", "user", "template"):
        idx = [t["i"] for t in toks if t["role"] == r]
        share[r] = R(np.mean([sum(row[i] for i in idx) for row in avg_last]), 4)

    # ---------------------------------------------------------------- embeddings: PCA map, values, neighbours
    def word_vec(w):
        p = tok(" " + w, add_special_tokens=False).input_ids
        return E[p].mean(0), [show(t) for t in p]
    ref = []
    for grp, words in REF_WORDS.items():
        for w in words:
            v, pieces = word_vec(w)
            ref.append({"word": w, "group": grp, "pieces": pieces, "v": v})
    Xr = torch.stack([r["v"] for r in ref]).numpy()
    mu = Xr.mean(0)
    U, S, Vt = np.linalg.svd(Xr - mu, full_matrices=False)
    P3 = Vt[:3]
    var = (S ** 2) / (S ** 2).sum()
    proj = lambda v: [R(x, 4) for x in ((np.asarray(v) - mu) @ P3.T).tolist()]
    pca = {"fit_on": "the reference words (each word's input embedding; a word cut into several tokens = the mean of its pieces)",
           "explained": [R(x, 4) for x in var[:3].tolist()],
           "words": [{"word": r["word"], "group": r["group"], "pieces": r["pieces"], "xyz": proj(r["v"].numpy())} for r in ref],
           "prompt": [{"i": t["i"], "xyz": proj(E[t["id"]].numpy())} for t in toks]}
    values = [{"i": t["i"], "v16": [R(x, 4) for x in E[t["id"]][:16].tolist()], "norm": R(E[t["id"]].norm(), 3)} for t in toks]
    En = E / E.norm(dim=1, keepdim=True)
    vocab_txt = [show(i) for i in range(E.shape[0])]
    clean = torch.tensor([bool(re.fullmatch(r" [A-Za-z]{3,}", s)) for s in vocab_txt])
    neigh = {}
    for w in NEIGHBOURS_OF:
        wid = tok(w, add_special_tokens=False).input_ids
        assert len(wid) == 1, (w, wid)
        sim = En @ En[wid[0]]
        sim[~clean] = -2
        top = sim.topk(40)
        rows = []
        for s, i in zip(top.values.tolist(), top.indices.tolist()):
            t = vocab_txt[i]
            if t.strip().lower() == w.strip().lower() or any(t.strip().lower() == r["text"].strip().lower() for r in rows):
                continue
            rows.append({"id": int(i), "text": t, "cos": R(s, 4)})
            if len(rows) == 8:
                break
        neigh[w.strip()] = {"id": wid[0], "neighbours": rows}

    # ---------------------------------------------------------------- the fix, measured: one stock line in the prompt
    sys_f = system + "\n" + fact_line
    text_f, ids_f, toks_f = build(sys_f)
    greedy_f = generate(ids_f)
    ans_f = "".join(s["text"] for s in greedy_f if s["text"] not in ("<|im_end|>", "<|endoftext|>"))
    dpos_f = digits_of(greedy_f)
    print("with facts:", ans_f, "digits at", dpos_f)
    # where the fact's number sits in the prompt
    fstart = text_f.index(fact_line)
    enc_f = tok(text_f, return_offsets_mapping=True, add_special_tokens=False)
    fact_idx = [i for i, (a, b) in enumerate(enc_f.offset_mapping) if a >= fstart and b <= fstart + len(fact_line) and b > a]
    num0 = fstart + fact_line.index("5,400")
    fact_num_idx = [i for i, (a, b) in enumerate(enc_f.offset_mapping) if a >= num0 and b <= num0 + 5 and b > a]
    for r in toks_f:
        r["fact"] = r["i"] in fact_idx
        r["digit"] = r["text"].strip().isdigit()
    ds_f = digit_steps(ids_f, greedy_f, dpos_f)
    o_f = ds_f[0].pop("_out") if ds_f else None
    fact_attn = None
    if o_f is not None:
        q = ds_f[0]["query_pos"]
        per_layer = [R(sum(o_f.attentions[l][0, :, q, i].mean() for i in fact_num_idx), 4) for l in range(L)]
        fact_attn = {"query_pos": q, "fact_number_positions": fact_num_idx, "weight_on_5400_by_layer": per_layer,
                     "best_head": None, "avg": attn_avg(o_f, q)}
        b = max(((float(o_f.attentions[l][0, h, q, fact_num_idx].sum()), l, h) for l in range(L) for h in range(H)))
        fact_attn["best_head"] = {"layer": b[1] + 1, "head": b[2], "weight": R(b[0], 4),
                                  "row": [R(x, 4) for x in o_f.attentions[b[1]][0, b[2], q, : q + 1].tolist()]}
    samples_f = []
    for seed in range(5):
        st = generate(ids_f, n=80, T=0.7, seed=seed)
        txt = "".join(s["text"] for s in st if s["text"] not in ("<|im_end|>", "<|endoftext|>"))
        samples_f.append({"seed": seed, "temperature": 0.7, "text": txt, "numbers": numbers(txt)})

    # ---------------------------------------------------------------- meta
    try:
        from huggingface_hub import scan_cache_dir
        revs = [r.commit_hash for repo in scan_cache_dir().repos if repo.repo_id == MODEL for r in repo.revisions]
    except Exception as e:  # noqa: BLE001
        revs = [f"unknown ({e})"]
    n_params = sum(p.numel() for p in model.parameters())
    lens_last = lens(out, last, 5, int(logits_last.argmax()))
    meta = {
        "model": MODEL, "revision": getattr(cfg, "_commit_hash", None) or (revs[0] if revs else None), "dtype": "float32",
        "attn_implementation": "eager", "device": "cpu (Modal, 4 vCPU)",
        "torch": torch.__version__, "transformers": transformers.__version__, "numpy": np.__version__,
        "recorded_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "params": n_params, "layers": L, "heads": H, "kv_heads": cfg.num_key_value_heads, "d_model": cfg.hidden_size,
        "head_dim": cfg.hidden_size // H, "mlp_hidden": cfg.intermediate_size, "vocab": cfg.vocab_size,
        "tokenizer_len": len(tok), "context": cfg.max_position_embeddings, "tied_embeddings": bool(cfg.tie_word_embeddings),
        "embedding_params": int(E.numel()),
        "forward_seconds": R(fwd_s, 3), "generate_seconds": R(gen_s, 2), "total_seconds": R(time.time() - t_start, 1),
        "decoding": "greedy = argmax of the raw logits at every step; samples = softmax(logits / 0.7), no top-k, top-p or repetition penalty (the model's generation_config is not used)",
        "logit_lens": "after block l: the final RMSNorm then the unembedding (tied to the input embeddings) applied to the hidden state; block 24 = the model's own output",
    }
    # the first 16 input-embedding values of every token id the scene draws a column for (answers, the added fact)
    extra_ids = sorted({s["id"] for s in greedy} | {s["id"] for s in greedy_f} | {t["id"] for t in toks_f})
    id_values = {str(i): [R(x, 4) for x in E[i][:16].tolist()] for i in extra_ids}
    first_match = next((r["layer"] for r in lens_last if r["top"][0]["id"] == int(logits_last.argmax())), None)
    res = {
        "meta": meta,
        "prompt": {"system": system, "question": QUESTION, "chat_text": text, "n_tokens": N,
                   "counts": {r: sum(1 for t in toks if t["role"] == r) for r in ("system", "user", "template")}},
        "tokens": toks, "number_cuts": number_cuts,
        "key_positions": {"battery": i_bat, "Manchester": i_man, "start": 0, "last": last},
        "embeddings": {"pca": pca, "values": values, "id_values": id_values, "neighbours": neigh},
        "attention": {"last": {"query_pos": last, "avg": avg_last, "share_by_role": share},
                      "digit": {"query_pos": dsteps[0]["query_pos"], "avg": dsteps[0].pop("attn_avg")} if dsteps else None,
                      "heads": picks, "head_table_last": tbl_last, "head_table_digit": tbl_digit},
        "logit_lens": {"last": lens_last, "last_first_layer_top1_is_final": first_match,
                       "digits": [{"step": d["step"], "token": d["token"], "lens": d["lens"]} for d in dsteps]},
        "final": {"last": {"0": [{"id": int(logits_last.argmax()), "text": show(logits_last.argmax()), "p": 1.0}],
                           **{str(T): topk_probs(logits_last, 10, T) for T in (0.7, 1.0, 1.2)}},
                  "digit": dsteps[0]["final"] if dsteps else None,
                  "dial_last": dial(logits_last), "dial_digit": dsteps[0]["dial"] if dsteps else None},
        "generation": {"greedy": greedy, "text": ans_text, "numbers": numbers(ans_text), "digit_steps": dpos,
                       "digits": [{k: d[k] for k in ("step", "token", "id", "p", "alts")} for d in dsteps],
                       "samples_t07": samples},
        "facts": {"line": fact_line, "where": "appended to the system prompt as its last line", "system": sys_f,
                  "n_tokens": len(ids_f), "tokens": toks_f, "fact_positions": fact_idx, "greedy": greedy_f, "text": ans_f,
                  "numbers": numbers(ans_f), "digit_steps": dpos_f,
                  "digits": [{k: d[k] for k in ("step", "token", "id", "p", "alts")} for d in ds_f],
                  "final_digit": ds_f[0]["final"] if ds_f else None,
                  "digit_lens": [{"step": d["step"], "token": d["token"], "lens": d["lens"]} for d in ds_f],
                  "attention_to_fact": fact_attn, "samples_t07": samples_f, "truth": TRUTH},
    }
    return res


def world_ok(obj) -> bool:
    """True when a log uses only the v4 world: none of tools/world_v4.py's OLD_WORDS appears in it."""
    import sys
    sys.path.insert(0, str(COURSE / "tools"))
    from world_v4 import OLD_WORDS
    s = json.dumps(obj, ensure_ascii=False)
    return not any(re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", s) for w in OLD_WORDS)


def pack_trace(trace: dict):
    """trace.json + trace.js (window.BRAIN_TRACE), adding the parameter numbers from model_card.json and the tiny GPT
    from experiments/logs/tinygpt.json when it has been re-run on the Northbridge corpus."""
    card = LOGS / "model_card.json"
    if card.exists():
        trace["model_card"] = {"file": "experiments/logs/model_card.json", **json.loads(card.read_text())}
    tg = LOGS / "tinygpt.json"
    trace.pop("tinygpt", None)
    if tg.exists():
        d = json.loads(tg.read_text())
        if world_ok(d):
            trace["tinygpt"] = {"file": "experiments/logs/tinygpt.json", "config": d.get("config"), "params": d.get("params"),
                                "curve": d.get("curve"), "sample_untrained": d.get("sample_untrained"),
                                "samples": d.get("samples"), "corpus_chars": d.get("corpus_chars"),
                                "train_seconds_cpu2": d.get("train_seconds_cpu2")}
            print("tiny GPT included (Northbridge corpus)")
        else:
            print("tiny GPT log still from the old world: left out, the training section stays schematic")
    # the Qwen2.5 training facts the "where the weights came from" section quotes (from the model's technical report)
    trace["training"] = {
        "source": "Qwen2.5 Technical Report, arXiv:2412.15115 (Dec 2024); model card huggingface.co/Qwen/Qwen2.5-0.5B-Instruct",
        "stages": [
            {"name": "Pretraining", "what": "predict the next token on web text, books, code and maths", "size": "up to 18 trillion tokens"},
            {"name": "Instruction tuning", "what": "learn the chat format from worked examples", "size": "over 1 million examples"},
            {"name": "Preference tuning", "what": "prefer the answers people rate higher", "size": "offline DPO, then online RL"},
        ],
        "released": "2024-09-19", "asked": "2026-10-26",
    }
    (HERE / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, separators=(",", ":")))
    (HERE / "trace.js").write_text("/* The recorded Lecture 2 trace (same data as trace.json), written by capture_trace.py. */\n"
                                   "window.BRAIN_TRACE = " + json.dumps(trace, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("wrote trace.json", round((HERE / "trace.json").stat().st_size / 1e6, 2), "MB")


@app.local_entrypoint()
def main(pack: int = 0):
    if pack:
        pack_trace(json.loads((HERE / "trace.json").read_text()))
        return
    bp = brain_prompt()
    trace = capture.remote(bp["system"], FACT)
    trace["prompt"]["source"] = bp["source"]
    trace["prompt"]["person"] = bp["person"]
    pack_trace(trace)
    g = trace["generation"]; f = trace["facts"]
    print("tokens:", trace["prompt"]["n_tokens"], trace["prompt"]["counts"])
    print("greedy:", g["text"])
    print("digits:", [(d["token"], d["p"]) for d in g["digits"]])
    print("with facts:", f["text"], [(d["token"], d["p"]) for d in f["digits"]])
    print("lens last:", [(r["layer"], r["top"][0]["text"], r["top"][0]["p"]) for r in trace["logit_lens"]["last"]])
    print("heads:", [(h["looks_at"], h["layer"], h["head"], h["weight_last"]) for h in trace["attention"]["heads"]])
