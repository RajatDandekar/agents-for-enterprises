"""Lecture 2: every number about a real open model and the tiny GPT, measured on Modal (CPU, like free Colab).

    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py            # both jobs
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py --only qwen
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py --only tiny

Job "qwen" (Qwen/Qwen2.5-0.5B base and -Instruct, float32, eager attention, 4 CPUs) writes to logs/:
  model_card.json  next_token.json  tokens.json  bpe.json  embeddings.json  attention.json  logit_lens.json
  surprise.json  samples.json  chat_template.json  hand_attention.json
Job "tiny" (2 CPUs, the free-Colab budget) trains bahi.course.l2.tinygpt on the Rasoi corpus: logs/tinygpt.json.
Compact copies the notebook replays from are written to bahi/bahi/course/l2/rec_*.json.
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
L2PKG = COURSE / "bahi" / "bahi" / "course" / "l2"
DOCS = COURSE / "bahi" / "bahi" / "docs"
LOCAL = L2PKG.exists()

image = (modal.Image.debian_slim(python_version="3.11")
         .pip_install("torch==2.4.1", index_url="https://download.pytorch.org/whl/cpu")
         .pip_install("transformers==4.46.3", "numpy<2.1", "accelerate", "sentencepiece")
         .run_commands("python -c \"from transformers import AutoTokenizer, AutoModelForCausalLM as M; "
                       "[AutoTokenizer.from_pretrained(n) for n in ('Qwen/Qwen2.5-0.5B','Qwen/Qwen2.5-0.5B-Instruct','gpt2')]; "
                       "[M.from_pretrained(n) for n in ('Qwen/Qwen2.5-0.5B','Qwen/Qwen2.5-0.5B-Instruct')]\"")
         )
if LOCAL:
    image = (image.add_local_dir(L2PKG, "/l2", ignore=lambda p: str(p).endswith(".json"))
             .add_local_dir(DOCS, "/docs", ignore=lambda p: "_index" in str(p)))
app = modal.App("l2-brain-models", image=image)

BASE, INSTRUCT = "Qwen/Qwen2.5-0.5B", "Qwen/Qwen2.5-0.5B-Instruct"
SENT = "Kavita needs 20,000 gaskets before the Diwali run."


@app.function(cpu=4, memory=12288, timeout=3000)
def qwen() -> dict:
    import sys
    import time

    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from transformers.models.gpt2.tokenization_gpt2 import bytes_to_unicode

    sys.path.insert(0, "/")
    torch.set_grad_enabled(False)
    out = {}
    byte_dec = {v: k for k, v in bytes_to_unicode().items()}
    tok = AutoTokenizer.from_pretrained(BASE)
    gtok = AutoTokenizer.from_pretrained("gpt2")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32, attn_implementation="eager").eval()
    load_s = time.time() - t0
    cfg = model.config

    def pieces(tk, ids):
        res = []
        for i in ids:
            raw = tk.convert_ids_to_tokens(int(i))
            try:
                b = bytes(byte_dec[c] for c in raw)
            except KeyError:
                b = raw.encode()
            try:
                text = b.decode("utf-8")
            except UnicodeDecodeError:
                text = None  # a fragment of a multi-byte character
            res.append({"id": int(i), "raw": raw, "text": text, "bytes": b.hex(" ")})
        return res

    def ids(s):
        return tok(s, return_tensors="pt").input_ids

    def show(tid):
        return tok.decode([int(tid)])

    # ---------------- model card
    n_params = sum(p.numel() for p in model.parameters())
    x = ids(SENT)
    t1 = time.time(); model(x); fwd = time.time() - t1
    out["model_card.json"] = {
        "model": BASE, "params": n_params, "layers": cfg.num_hidden_layers, "d_model": cfg.hidden_size,
        "heads": cfg.num_attention_heads, "kv_heads": cfg.num_key_value_heads,
        "head_dim": cfg.hidden_size // cfg.num_attention_heads, "mlp_hidden": cfg.intermediate_size,
        "vocab": cfg.vocab_size, "tokenizer_len": len(tok), "context": cfg.max_position_embeddings,
        "tied_embeddings": cfg.tie_word_embeddings, "rope_theta": cfg.rope_theta, "norm": type(model.model.norm).__name__,
        "activation": cfg.hidden_act, "embedding_params": int(model.model.embed_tokens.weight.numel()),
        "load_seconds_cpu4": round(load_s, 1), "forward_seconds_cpu4": round(fwd, 3), "forward_tokens": x.shape[1],
        "gpt2_vocab": len(gtok)}

    # ---------------- next-token probabilities
    def dist(prompt, k=20, keep=60):
        lg = model(ids(prompt)).logits[0, -1]
        p = torch.softmax(lg, -1)
        top = torch.topk(lg, keep)
        return {"prompt": prompt, "n_tokens": int(ids(prompt).shape[1]),
                "top": [{"text": show(i), "id": int(i), "logit": round(float(l), 3), "p": round(float(p[i]), 5)}
                        for l, i in zip(top.values[:k], top.indices[:k])],
                "logits60": [{"text": show(i), "logit": round(float(l), 3)} for l, i in zip(top.values, top.indices)],
                "entropy_bits": round(float(-(p * torch.log2(p.clamp_min(1e-12))).sum()), 3)}

    prompts = {"makes": "Rasoi Steel Works makes pressure",
               "diwali": "Kavita needs 20,000 gaskets before the Diwali",
               "stock": "Stock report, Rasoi Steel Works, Pune.\nItem: GSK-SIL-05L, silicone gasket, 5 litre.\nOn hand in Pune stores:",
               "supplier": "Rasoi Steel Works buys its 5-litre silicone gaskets from"}
    nt = {k: dist(v) for k, v in prompts.items()}
    # the game played again and again: greedy, one token at a time, with the top 5 at each step
    seq, steps = ids("Kavita needs 20,000 gaskets before the"), []
    for _ in range(10):
        lg = model(seq).logits[0, -1]
        p = torch.softmax(lg, -1)
        tp = torch.topk(p, 5)
        steps.append({"context": tok.decode(seq[0]), "top5": [{"text": show(i), "p": round(float(v), 4)} for v, i in zip(tp.values, tp.indices)]})
        seq = torch.cat([seq, tp.indices[:1].view(1, 1)], 1)
    nt["greedy_steps"] = steps
    nt["greedy_text"] = tok.decode(seq[0])

    def gen(prompt, n=12, temperature=1.0, top_p=1.0, seed=0, mdl=None, input_ids=None):
        mdl = mdl or model
        torch.manual_seed(seed)
        inp = input_ids if input_ids is not None else ids(prompt)
        kw = dict(do_sample=temperature > 0, max_new_tokens=n, pad_token_id=tok.eos_token_id)
        if temperature > 0:
            kw.update(temperature=temperature, top_p=top_p, top_k=0)
        o = mdl.generate(inp, attention_mask=torch.ones_like(inp), **kw)
        return tok.decode(o[0, inp.shape[1]:], skip_special_tokens=True)

    nt["stock_samples"] = [{"seed": s, "text": gen(prompts["stock"], 8, 1.0, seed=s)} for s in range(10)]
    nt["stock_greedy"] = gen(prompts["stock"], 8, 0)
    nt["supplier_greedy"] = gen(prompts["supplier"], 12, 0)
    out["next_token.json"] = nt

    # ---------------- tokens
    sents = [SENT, "PO/2026/01182: 20,000 x GSK-SIL-05L at ₹11.90, gross ₹2,80,840.",
             "Kavita ko Diwali se pehle 20,000 gasket chahiye.", "कविता को दिवाली से पहले 20,000 गैस्केट चाहिए।"]
    tk = {"sentences": []}
    for s in sents:
        q = tok(s).input_ids
        g = gtok(s).input_ids
        tk["sentences"].append({"text": s, "chars": len(s), "words": len(s.split()), "bytes": len(s.encode()),
                                "qwen": pieces(tok, q), "gpt2": pieces(gtok, g), "n_qwen": len(q), "n_gpt2": len(g)})
    docs = {}
    allt = ""
    for f in sorted(pathlib.Path("/docs").glob("*.md")):
        if "salary" in f.name:
            continue
        t = f.read_text()
        allt += t
        docs[f.name] = {"chars": len(t), "words": len(t.split()), "qwen_tokens": len(tok(t).input_ids)}
    docs["ALL"] = {"chars": len(allt), "words": len(allt.split()), "qwen_tokens": len(tok(allt).input_ids)}
    tk["docs"] = docs
    corpus = pathlib.Path("/l2/rasoi_corpus.md").read_text()
    tk["corpus"] = {"chars": len(corpus), "words": len(corpus.split()), "qwen_tokens": len(tok(corpus).input_ids),
                    "distinct_chars": len(set(corpus))}
    tk["vocab"] = {"qwen": len(tok), "gpt2": len(gtok)}
    out["tokens.json"] = tk

    # ---------------- BPE by hand on a tiny corpus
    tiny = "gasket gaskets gasket seal gaskets seals gasket seal gasket kit gaskets set"
    words = {}
    for w in tiny.split():
        words[tuple(w) + ("_",)] = words.get(tuple(w) + ("_",), 0) + 1
    vocab = sorted({c for w in words for c in w})
    start_vocab = list(vocab)
    merges = []
    for step in range(10):
        pairs = {}
        for w, n in words.items():
            for a, b in zip(w, w[1:]):
                pairs[(a, b)] = pairs.get((a, b), 0) + n
        if not pairs:
            break
        best = max(pairs, key=lambda k: (pairs[k], -list(pairs).index(k)))
        new = {}
        for w, n in words.items():
            o, i = [], 0
            while i < len(w):
                if i < len(w) - 1 and (w[i], w[i + 1]) == best:
                    o.append(w[i] + w[i + 1]); i += 2
                else:
                    o.append(w[i]); i += 1
            new[tuple(o)] = n
        words = new
        vocab.append(best[0] + best[1])
        merges.append({"step": step + 1, "pair": list(best), "count": pairs[best],
                       "top_pairs": sorted([[a + "+" + b, c] for (a, b), c in pairs.items()], key=lambda z: -z[1])[:6],
                       "words": {"".join(w).rstrip("_"): list(w) for w in words},
                       "vocab_size": len(vocab), "corpus_tokens": sum(len(w) * n for w, n in words.items())})
    out["bpe.json"] = {"corpus": tiny, "start_vocab": start_vocab,
                       "start_tokens": sum((len(w) + 1) for w in tiny.split()), "merges": merges}

    # ---------------- embeddings
    groups = {"parts": ["gasket", "washer", "seal", "valve", "whistle", "handle", "lid"],
              "firms": ["supplier", "vendor", "seller", "manufacturer", "dealer"],
              "documents": ["invoice", "bill", "receipt", "quotation", "challan"],
              "money": ["rupee", "price", "payment", "cost", "discount"],
              "places": ["Pune", "Mumbai", "Rajkot", "Nagpur", "Kolkata"],
              "festivals": ["Diwali", "Holi", "Navratri", "Christmas"]}
    E = model.model.embed_tokens.weight
    words_l, grp = [], []
    for g, ws in groups.items():
        for w in ws:
            words_l.append(w); grp.append(g)

    def static(w):
        t = tok(" " + w).input_ids
        return E[t].mean(0).numpy(), [show(i) for i in t]

    def contextual(w, layer):
        pre = ids("Purchase note: the")
        full = ids("Purchase note: the " + w)
        hs = model(full, output_hidden_states=True).hidden_states[layer][0]
        return hs[pre.shape[1]:].mean(0).numpy()

    def analyse(V):
        V = np.array(V)
        Vn = V / np.linalg.norm(V, axis=1, keepdims=True)
        C = Vn @ Vn.T
        same = np.array([[grp[i] == grp[j] and i != j for j in range(len(grp))] for i in range(len(grp))])
        diff = np.array([[grp[i] != grp[j] for j in range(len(grp))] for i in range(len(grp))])
        Xc = V - V.mean(0)
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        xy = Xc @ Vt[:2].T
        nn = {}
        for i, w in enumerate(words_l):
            order = [j for j in np.argsort(-C[i]) if j != i][:4]
            nn[w] = [[words_l[j], round(float(C[i, j]), 3)] for j in order]
        nn_hit = float(np.mean([grp[words_l.index(nn[w][0][0])] == grp[i] for i, w in enumerate(words_l)]))
        return {"xy": [[round(float(a), 4), round(float(b), 4)] for a, b in xy], "nn": nn,
                "within": round(float(C[same].mean()), 4), "between": round(float(C[diff].mean()), 4),
                "nn_same_group": round(nn_hit, 3), "pca_var": [round(float(v), 4) for v in (S[:2] ** 2 / (S ** 2).sum())],
                "cos": [[round(float(v), 3) for v in row] for row in C]}

    st = [static(w) for w in words_l]
    emb = {"words": words_l, "groups": grp, "pieces": {w: s[1] for w, s in zip(words_l, st)},
           "static": analyse([s[0] for s in st]), "layers": {}}
    for L in (4, 8, 12, 16):
        emb["layers"][str(L)] = analyse([contextual(w, L) for w in words_l])
    g1 = tok(" gasket").input_ids
    emb["gasket_vector_first8"] = [round(float(v), 4) for v in E[g1[0]][:8]]
    emb["gasket_token_ids"] = g1
    En = E / E.norm(dim=1, keepdim=True)
    vnn = {}
    for w in ["gasket", "supplier", "invoice", "Diwali", "Pune"]:
        t = tok(" " + w).input_ids
        if len(t) == 1:
            sims = En @ En[t[0]]
            top = torch.topk(sims, 9)
            vnn[w] = [[show(i), round(float(s), 3)] for s, i in zip(top.values[1:], top.indices[1:])]
    emb["vocab_neighbours"] = vnn
    out["embeddings.json"] = emb

    # ---------------- attention (real) on the Rasoi sentence
    x = ids(SENT)
    o = model(x, output_attentions=True, output_hidden_states=True)
    toks = [show(i) for i in x[0]]
    att = [[[[round(float(v), 3) for v in row] for row in head] for head in layer[0]] for layer in o.attentions]
    T = len(toks)
    offs = tok(SENT, return_offsets_mapping=True)["offset_mapping"]
    g_end = SENT.index("gaskets") + len("gaskets")
    gi = next(i for i, (a, b) in enumerate(offs) if b == g_end)            # the last piece of "gaskets"
    n0, n1 = SENT.index("20,000"), SENT.index("20,000") + 6
    digits = [i for i, (a, b) in enumerate(offs) if a >= n0 - 1 and b <= n1 and b > a]
    heads = []
    for L, layer in enumerate(o.attentions):
        A = layer[0].numpy()
        for H in range(A.shape[0]):
            prev = float(np.mean([A[H, i, i - 1] for i in range(1, T)]))
            sink = float(np.mean([A[H, i, 0] for i in range(1, T)]))
            g2d = float(A[H, gi, digits].sum())
            heads.append({"layer": L, "head": H, "prev_token": round(prev, 3), "first_token": round(sink, 3),
                          "gaskets_to_number": round(g2d, 3)})
    out["attention.json"] = {"sentence": SENT, "tokens": toks, "layers": len(att), "heads": len(att[0]),
                             "gaskets_index": gi, "number_indices": digits, "att": att,
                             "top_prev_token": sorted(heads, key=lambda h: -h["prev_token"])[:5],
                             "top_gaskets_to_number": sorted(heads, key=lambda h: -h["gaskets_to_number"])[:5],
                             "mean_first_token": round(float(np.mean([h["first_token"] for h in heads])), 3)}

    # ---------------- logit lens: follow the last token through the stack
    pre = "Kavita needs 20,000 gaskets before the Diwali"
    o = model(ids(pre), output_hidden_states=True)
    lens = []
    for L, h in enumerate(o.hidden_states):
        v = h[0, -1]
        vv = v if L == len(o.hidden_states) - 1 else model.model.norm(v)
        p = torch.softmax(model.lm_head(vv), -1)
        tp = torch.topk(p, 3)
        lens.append({"layer": L, "norm": round(float(h[0, -1].norm()), 2),
                     "top3": [[show(i), round(float(s), 4)] for s, i in zip(tp.values, tp.indices)]})
    out["logit_lens.json"] = {"prompt": pre, "tokens": [show(i) for i in ids(pre)[0]], "lens": lens}

    # ---------------- surprise (cross-entropy) per token
    def surprise(s):
        x = ids(s)
        lg = model(x).logits[0]
        lp = torch.log_softmax(lg[:-1], -1)
        nll = [-float(lp[i, x[0, i + 1]]) for i in range(x.shape[1] - 1)]
        return {"text": s, "tokens": [show(i) for i in x[0]], "nll": [round(v, 3) for v in nll],
                "p": [round(float(np.exp(-v)), 4) for v in nll],
                "mean_nll": round(float(np.mean(nll)), 3), "perplexity": round(float(np.exp(np.mean(nll))), 2)}
    out["surprise.json"] = {"sentences": [surprise(SENT), surprise("Kavita needs 20,000 gaskets before the Diwali elephant."),
                                          surprise("PO/2026/01182 was released to Deccan Polymers, Rajkot.")],
                            "uniform_nll": round(float(np.log(cfg.vocab_size)), 3)}

    # ---------------- sampling
    sp = "Kavita needs 20,000 gaskets before the Diwali run, so she"
    smp = {"prompt": sp, "runs": []}
    for T_ in (0, 0.7, 1.0, 1.5):
        for s in range(3 if T_ else 1):
            smp["runs"].append({"temperature": T_, "seed": s, "top_p": 1.0, "text": gen(sp, 16, T_, seed=s)})
    for s in range(3):
        smp["runs"].append({"temperature": 1.0, "seed": s, "top_p": 0.9, "text": gen(sp, 16, 1.0, 0.9, seed=s)})
    smp["dist"] = dist(sp)
    out["samples.json"] = smp

    # ---------------- chat format with the instruct model
    from l2.brain import FOLLOW_UP, messages
    itok = AutoTokenizer.from_pretrained(INSTRUCT)
    imodel = AutoModelForCausalLM.from_pretrained(INSTRUCT, torch_dtype=torch.float32).eval()
    msgs = messages()
    s = itok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    iid = itok(s, return_tensors="pt").input_ids
    ans = gen(None, 60, 0, mdl=imodel, input_ids=iid)
    hot = [gen(None, 60, 0.8, seed=k, mdl=imodel, input_ids=iid) for k in range(5)]
    msgs2 = msgs + [{"role": "assistant", "content": ans}, {"role": "user", "content": FOLLOW_UP}]
    s2 = itok.apply_chat_template(msgs2, tokenize=False, add_generation_prompt=True)
    iid2 = itok(s2, return_tensors="pt").input_ids
    ans2 = gen(None, 60, 0, mdl=imodel, input_ids=iid2)
    out["chat_template.json"] = {"model": INSTRUCT, "messages": msgs, "template": s, "n_tokens": int(iid.shape[1]),
                                 "pieces": [p["text"] if p["text"] is not None else p["raw"] for p in pieces(itok, iid[0])],
                                 "answer_greedy": ans, "answers_t08": hot, "turn2_template": s2,
                                 "turn2_n_tokens": int(iid2.shape[1]), "turn2_answer": ans2}

    # ---------------- the hand-worked attention example
    names = ["Kavita", "needs", "20,000", "gaskets"]
    Q = np.array([[1, 0], [1, 1], [0, 1], [0, 2]], float)
    K = np.array([[2, 0], [0, 1], [1, 3], [1, 1]], float)
    V = np.array([[4, 0], [0, 1], [0, 8], [2, 2]], float)
    S = Q @ K.T
    Ss = S / np.sqrt(2)
    M = np.where(np.tril(np.ones((4, 4))) > 0, Ss, -np.inf)
    W = np.exp(M - M.max(1, keepdims=True)); W = W / W.sum(1, keepdims=True)
    Y = W @ V
    ex = np.exp(Ss[3]);
    out["hand_attention.json"] = {"tokens": names, "Q": Q.tolist(), "K": K.tolist(), "V": V.tolist(),
                                  "scores": S.tolist(), "scaled": np.round(Ss, 3).tolist(),
                                  "exp_last": np.round(ex, 3).tolist(), "exp_sum_last": round(float(ex.sum()), 3),
                                  "weights": np.round(W, 3).tolist(), "outputs": np.round(Y, 3).tolist(),
                                  "sqrt_d": round(float(np.sqrt(2)), 4)}
    return out


@app.function(cpu=2, memory=4096, timeout=3000)
def tiny() -> dict:
    import sys
    import time

    import torch
    sys.path.insert(0, "/")
    torch.set_num_threads(2)
    from l2.tinygpt import train, sample  # noqa
    text = pathlib.Path("/l2/rasoi_corpus.md").read_text()
    lines = []
    m0, enc, dec, c0 = train(text, steps=0, log=lines.append)
    before = sample(m0, enc, dec, "Stores, 26 Oct 2026: ", 120, 1.0, 0)
    t0 = time.time()
    model, enc, dec, curve = train(text, steps=1500, log=lines.append)
    secs = time.time() - t0
    prompts = ["Stores, 26 Oct 2026: GSK-SIL-05L in Pune stores,", "From: Kavita Joshi\nTo: Rohit Mehta\nSubject:",
               "6.2 ", "Approval, 26 Oct 2026: PR/2026/04417 is"]
    samples = {p: {str(T): sample(model, enc, dec, p, 220, T, 0) for T in (0.5, 0.8, 1.2)} for p in prompts}
    stock = [sample(model, enc, dec, "Stores, 26 Oct 2026: GSK-SIL-05L in Pune stores,", 40, 0.8, s) for s in range(8)]
    n_params = sum(p.numel() for p in model.parameters())
    return {"tinygpt.json": {"config": {"vocab": model.c.vocab_size, "block": model.c.block_size, "layers": model.c.n_layer,
                                        "heads": model.c.n_head, "d_model": model.c.n_embd, "steps": 1500, "batch": 32,
                                        "lr": 2e-3},
                             "params": n_params, "corpus_chars": len(text), "train_seconds_cpu2": round(secs, 1),
                             "curve": curve, "log": lines, "sample_untrained": before, "samples": samples,
                             "stock_samples": stock}}


@app.function(cpu=4, memory=12288, timeout=1200)
def extra() -> dict:
    """Follow-ups after the first run: the stock prompt with its trailing space (Qwen writes the space as its own
    token, so the first run's top guess was ' '), the probability of ' cook'+'ers', and two single-token table rows."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_grad_enabled(False)
    tok = AutoTokenizer.from_pretrained(BASE)
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32).eval()
    ids = lambda s: tok(s, return_tensors="pt").input_ids
    stock = "Stock report, Rasoi Steel Works, Pune.\nItem: GSK-SIL-05L, silicone gasket, 5 litre.\nOn hand in Pune stores: "
    p = torch.softmax(model(ids(stock)).logits[0, -1], -1)
    top = torch.topk(p, 12)
    out = {"stock_prompt": stock, "stock_top": [{"text": tok.decode([int(i)]), "p": round(float(v), 5)} for v, i in zip(top.values, top.indices)]}
    samples = []
    for s in range(10):
        torch.manual_seed(s)
        x = ids(stock)
        o = model.generate(x, attention_mask=torch.ones_like(x), do_sample=True, temperature=1.0, top_k=0, max_new_tokens=7,
                           pad_token_id=tok.eos_token_id)
        samples.append({"seed": s, "text": tok.decode(o[0, x.shape[1]:], skip_special_tokens=True)})
    out["stock_samples"] = samples
    x = ids(stock)
    o = model.generate(x, attention_mask=torch.ones_like(x), do_sample=False, max_new_tokens=7, pad_token_id=tok.eos_token_id)
    out["stock_greedy"] = tok.decode(o[0, x.shape[1]:], skip_special_tokens=True)
    pr = "Rasoi Steel Works makes pressure"
    p1 = torch.softmax(model(ids(pr)).logits[0, -1], -1)
    cook, ers = tok(" cook").input_ids[0], tok("ers").input_ids[0]
    p2 = torch.softmax(model(ids(pr + " cook")).logits[0, -1], -1)
    out["cookers"] = {"p_cook": round(float(p1[cook]), 5), "rank_cook": int((p1 > p1[cook]).sum()) + 1,
                      "p_ers_after_cook": round(float(p2[ers]), 5), "p_cookers": round(float(p1[cook] * p2[ers]), 5)}
    E = model.model.embed_tokens.weight
    out["rows"] = {}
    for w in (" supplier", " Pune"):
        t = tok(w).input_ids
        out["rows"][w] = {"ids": t, "first8": [round(float(v), 4) for v in E[t[0]][:8]]}
    return {"extra.json": out}


@app.local_entrypoint()
def main(only: str = ""):
    calls = []
    if only in ("", "qwen"):
        calls.append(qwen.spawn())
    if only in ("", "tiny"):
        calls.append(tiny.spawn())
    if only in ("", "extra"):
        calls.append(extra.spawn())
    logs = HERE / "logs"
    logs.mkdir(exist_ok=True)
    for c in calls:
        res = c.get()
        for name, data in res.items():
            (logs / name).write_text(json.dumps(data, indent=1, ensure_ascii=False))
            print("wrote", logs / name)
