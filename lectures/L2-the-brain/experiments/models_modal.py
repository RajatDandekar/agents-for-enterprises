"""Lecture 2 v4 (Northbridge Cycles): the numbers about tokens, the tiny GPT and the cut-off, measured on Modal CPU.

    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py              # both jobs
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py --only qwen
    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/models_modal.py --only tiny

The one forward pass of Emma's question that the 3D scene plays (tokens, vectors, attention, the logit lens,
temperatures, the generated answer, the answer with the fact) is recorded by the 3D builder in brain3d/trace.json.
This file does not repeat it for the deck. It records:

Job "qwen" (Qwen/Qwen2.5-0.5B-Instruct and the GPT-2 tokenizer, float32, 4 CPUs), to logs/:
  model_card.json   size of the model (read by brain3d/capture_trace.py too)
  tokens.json       how the app's prompt and Northbridge's words and numbers are cut; the question in six languages;
                    why tokens and not words (a word vocabulary from the corpus meets two documents it has not seen);
                    token counts of Northbridge's documents and of the tiny-GPT corpus
  bpe.json          byte-pair encoding by hand on a tiny Northbridge text, then 300 merges learnt on the corpus
  cutoff.json       where the model's "now" is: the probability of each year after "The current year is", and its
                    own answers to "what year is it?" and "what does your training data cover?"
  hand_attention.json  the four-token attention example worked by hand
  nb_qwen.json      what NB2 computes live with Qwen, recorded for its replay fallback (gen_figdata.py copies it to
                    ledgerline/course/l2/rec_qwen.json): the same functions, prompts and settings as the notebook
Job "tiny" (2 CPUs, the free-Colab budget): ledgerline.course.l2.tinygpt trained on northbridge_corpus.md, to
  tinygpt.json      loss curve, samples before and after training, the corpus's last day (its training cut-off)

The app's brain-stage system prompt is read from ledgerline.course.l2.brain (= harness._system("brain", "ECLARKE"))
on the laptop and passed to the job, so the prompt is the app's, character for character.
"""
import json
import pathlib
import sys

import modal

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parents[2] if len(HERE.parents) > 2 else HERE
L2PKG = COURSE / "ledgerline" / "ledgerline" / "course" / "l2"
DOCS = COURSE / "ledgerline" / "ledgerline" / "docs"
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

INSTRUCT = "Qwen/Qwen2.5-0.5B-Instruct"
QUESTION = "How many city e-bike battery packs do we have in Manchester stores?"
FACT = "Ledgerline stock, BAT-500 at Manchester main stores: 5,400 on hand"
RAW = "City e-bike battery packs (BAT-500) in Manchester stores: "   # a stock line to complete, no chat format
LANGS = {
    "English": QUESTION,
    "German": "Wie viele Akkus für City-E-Bikes haben wir in den Lagern in Manchester?",
    "Dutch": "Hoeveel accu's voor stads-e-bikes hebben we in de magazijnen in Manchester?",
    "Polish": "Ile akumulatorów do miejskich rowerów elektrycznych mamy w magazynach w Manchesterze?",
    "Greek": "Πόσες μπαταρίες για ηλεκτρικά ποδήλατα πόλης έχουμε στις αποθήκες του Μάντσεστερ;",
    "Japanese": "マンチェスターの倉庫に、シティ電動自転車のバッテリーパックはいくつありますか？",
}
CUTS = ["Manchester", " Manchester", " battery", " batteries", " e-bike", " Northbridge", " Ledgerline", " Voltway",
        " Brightcell", " Gdańsk", " BAT-500", "5,400", " 5,400", "5400", " £285,600", " 2,000", " UN 38.3", " VAT20-RC"]
YEARS = list(range(2015, 2031))


@app.function(cpu=4, memory=12288, timeout=3000)
def qwen(system: str) -> dict:
    import re
    import time

    import numpy as np
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_grad_enabled(False)
    out = {}
    tok = AutoTokenizer.from_pretrained(INSTRUCT)
    gtok = AutoTokenizer.from_pretrained("gpt2")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(INSTRUCT, torch_dtype=torch.float32, attn_implementation="eager").eval()
    load_s = time.time() - t0
    cfg = model.config
    show = lambda i: tok.decode([int(i)])
    R = lambda x, n=4: float(round(float(x), n))

    def chat_ids(sys_text, question=QUESTION):
        msgs = [{"role": "system", "content": sys_text}, {"role": "user", "content": question}]
        text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        return text, tok(text, add_special_tokens=False).input_ids

    text, ids = chat_ids(system)

    # ---------------- model card
    n_params = sum(p.numel() for p in model.parameters())
    t1 = time.time(); model(torch.tensor([ids])); fwd = time.time() - t1
    out["model_card.json"] = {
        "model": INSTRUCT, "params": n_params, "layers": cfg.num_hidden_layers, "d_model": cfg.hidden_size,
        "heads": cfg.num_attention_heads, "kv_heads": cfg.num_key_value_heads,
        "head_dim": cfg.hidden_size // cfg.num_attention_heads, "mlp_hidden": cfg.intermediate_size,
        "vocab": cfg.vocab_size, "tokenizer_len": len(tok), "context": cfg.max_position_embeddings,
        "tied_embeddings": cfg.tie_word_embeddings, "rope_theta": cfg.rope_theta, "norm": type(model.model.norm).__name__,
        "activation": cfg.hidden_act, "embedding_params": int(model.model.embed_tokens.weight.numel()),
        "load_seconds_cpu4": round(load_s, 1), "forward_seconds_cpu4": round(fwd, 3), "forward_tokens": len(ids),
        "gpt2_vocab": len(gtok)}

    # ---------------- tokens: the app's prompt
    enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
    s0, u0 = text.index(system), text.index(QUESTION)
    spans = {"system": (s0, s0 + len(system)), "user": (u0, u0 + len(QUESTION))}
    pieces = []
    for tid, (a, b) in zip(enc.input_ids, enc.offset_mapping):
        role = next((r for r, (x, y) in spans.items() if a >= x and b <= y and b > a), "template")
        pieces.append([show(tid), int(tid), role])
    counts = {r: sum(1 for p in pieces if p[2] == r) for r in ("system", "user", "template")}

    def cut(tk, s):
        return [[tk.decode([i]), int(i)] for i in tk(s, add_special_tokens=False).input_ids]

    langs = {k: {"text": v, "chars": len(v), "words": len(v.split()), "bytes": len(v.encode()),
                 "qwen": len(tok(v, add_special_tokens=False).input_ids), "gpt2": len(gtok(v).input_ids),
                 "qwen_pieces": [p[0] for p in cut(tok, v)]} for k, v in LANGS.items()}

    # why tokens and not words: a word vocabulary built from the tiny-GPT corpus meets two documents it never saw
    WORD = re.compile(r"[A-Za-z0-9£§][A-Za-z0-9£§.,/'-]*[A-Za-z0-9]|[A-Za-z0-9]")
    corpus = pathlib.Path("/l2/northbridge_corpus.md").read_text()
    cw = WORD.findall(corpus)
    vocab_w = {}
    for w in cw:
        vocab_w[w] = vocab_w.get(w, 0) + 1
    unseen_docs = ["user-manual.md", "data-dictionary.md"]
    nw = []
    for f in unseen_docs:
        nw += WORD.findall(pathlib.Path("/docs", f).read_text())
    oov = [w for w in nw if w not in vocab_w]
    oov_distinct = sorted(set(oov), key=lambda w: -oov.count(w))
    manual = pathlib.Path("/docs/user-manual.md").read_text()
    man_ids = tok(manual, add_special_tokens=False).input_ids
    why = {"word_vocab_from_corpus": len(vocab_w), "corpus_words": len(cw),
           "words_seen_once": sum(1 for v in vocab_w.values() if v == 1),
           "number_words_in_vocab": sum(1 for w in vocab_w if any(c.isdigit() for c in w)),
           "unseen_docs": unseen_docs, "unseen_doc_words": len(nw), "oov_words": len(oov),
           "oov_share": R(len(oov) / len(nw), 4), "oov_distinct": len(oov_distinct), "oov_examples": oov_distinct[:40],
           "qwen_unknown_tokens": sum(1 for i in man_ids if i == tok.unk_token_id) if tok.unk_token_id is not None else 0,
           "qwen_roundtrip_exact": tok.decode(man_ids) == manual,
           "manual": {"chars": len(manual), "words": len(manual.split()), "qwen_tokens": len(man_ids),
                      "chars_per_token": R(len(manual) / len(man_ids), 2), "words_per_token": R(len(manual.split()) / len(man_ids), 3)},
           "char_vocab_corpus": len(set(corpus)), "qwen_vocab": len(tok)}
    docs = {}
    allt = ""
    for f in sorted(pathlib.Path("/docs").glob("*.md")):
        if "salary" in f.name:
            continue
        t = f.read_text()
        allt += t
        docs[f.name] = {"chars": len(t), "words": len(t.split()), "qwen_tokens": len(tok(t, add_special_tokens=False).input_ids)}
    docs["ALL"] = {"chars": len(allt), "words": len(allt.split()), "qwen_tokens": len(tok(allt, add_special_tokens=False).input_ids)}
    out["tokens.json"] = {
        "model": INSTRUCT, "system": system, "question": QUESTION, "chat_text": text, "n_tokens": len(ids),
        "counts": counts, "pieces": pieces,
        "question_tokens": cut(tok, QUESTION), "question_words": len(QUESTION.split()), "question_chars": len(QUESTION),
        "system_words": len(system.split()), "system_chars": len(system),
        "cuts": {s: {"qwen": cut(tok, s), "gpt2": cut(gtok, s)} for s in CUTS},
        "languages": langs, "why_tokens": why, "docs": docs,
        "corpus": {"chars": len(corpus), "words": len(corpus.split()), "qwen_tokens": len(tok(corpus, add_special_tokens=False).input_ids),
                   "distinct_chars": len(set(corpus))},
        "vocab": {"qwen": len(tok), "gpt2": len(gtok)}}

    # ---------------- BPE: by hand on a tiny Northbridge text, then learnt on the corpus
    def bpe_train(word_counts, n_merges, keep_steps=12):
        words = {tuple(w) + ("_",): c for w, c in word_counts.items()}
        merges, steps, sizes = [], [], []
        vocab = sorted({c for w in words for c in w})
        start_vocab, start_tokens = list(vocab), sum(len(w) * n for w, n in words.items())
        for step in range(1, n_merges + 1):
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
                new[tuple(o)] = new.get(tuple(o), 0) + n
            words = new
            merges.append(best)
            ntok = sum(len(w) * n for w, n in words.items())
            sizes.append({"merges": step, "vocab": len(start_vocab) + step, "corpus_tokens": ntok})
            if step <= keep_steps:
                steps.append({"step": step, "pair": list(best), "count": pairs[best],
                              "top_pairs": sorted([[a + "+" + b, c] for (a, b), c in pairs.items()], key=lambda z: -z[1])[:6],
                              "words": {"".join(w).rstrip("_"): list(w) for w in list(words)[:12]},
                              "vocab_size": len(start_vocab) + step, "corpus_tokens": ntok})
        return {"start_vocab": start_vocab, "start_tokens": start_tokens, "merges": merges, "steps": steps, "sizes": sizes}

    def bpe_apply(word, merges):
        w = list(word) + ["_"]
        for a, b in merges:
            i, o = 0, []
            while i < len(w):
                if i < len(w) - 1 and w[i] == a and w[i + 1] == b:
                    o.append(a + b); i += 2
                else:
                    o.append(w[i]); i += 1
            w = o
        return w

    tiny_text = "battery batteries pack packs battery pack charger chargers battery packs pack battery"
    wc = {}
    for w in tiny_text.split():
        wc[w] = wc.get(w, 0) + 1
    hand = bpe_train(wc, 10, keep_steps=10)
    hand["corpus"] = tiny_text
    hand["merges"] = [list(m) for m in hand["merges"]]
    cwc = {}
    for w in corpus.split():
        cwc[w] = cwc.get(w, 0) + 1
    t2 = time.time()
    learnt = bpe_train(cwc, 300, keep_steps=0)
    learnt_secs = round(time.time() - t2, 1)
    m300 = learnt["merges"]
    probe = ["Manchester", "battery", "packs", "BAT-500", "5,400", "Brightcell", "e-bike", "Voltway", "approval", "Aiko"]
    out["bpe.json"] = {
        "hand": hand,
        "learnt": {"on": "northbridge_corpus.md, split on spaces, '_' marks the end of a word", "distinct_words": len(cwc),
                   "start_vocab": len(learnt["start_vocab"]), "start_tokens": learnt["start_tokens"],
                   "first_merges": [["".join(m), list(m)] for m in m300[:40]],
                   "sizes": [s for s in learnt["sizes"] if s["merges"] in (1, 10, 25, 50, 100, 150, 200, 250, 300)],
                   "seconds": learnt_secs,
                   "cuts_after": {str(n): {w: bpe_apply(w, m300[:n]) for w in probe} for n in (0, 50, 100, 300)},
                   "question_after_300": [p for w in QUESTION.split() for p in bpe_apply(w, m300)],
                   "question_qwen": [p[0] for p in cut(tok, QUESTION)],
                   "merge_rank": {w: next((i + 1 for i, m in enumerate(m300) if "".join(m) in (w, w + "_")), None)
                                  for w in ["the", "battery", "Manchester", "BAT-500", "stores,", "Voltway", "packs"]}}}

    # ---------------- the cut-off: where is the model's "now"?
    def year_probs(prompt):
        base = tok(prompt, add_special_tokens=False).input_ids
        lp = {}
        for y in YEARS:
            full = tok(prompt + str(y), add_special_tokens=False).input_ids
            assert full[:len(base)] == base
            seq, s = list(base), 0.0
            for t_ in full[len(base):]:
                p = torch.softmax(model(torch.tensor([seq])).logits[0, -1], -1)
                s += float(torch.log(p[t_]))
                seq.append(t_)
            lp[y] = s
        tot = sum(np.exp(v) for v in lp.values())
        rows = [{"year": y, "p_raw": R(np.exp(v), 6), "p_among": R(np.exp(v) / tot, 4)} for y, v in lp.items()]
        return {"prompt": prompt, "years": rows, "top": max(rows, key=lambda r: r["p_raw"])["year"],
                "mass_2026_on": R(sum(r["p_among"] for r in rows if r["year"] >= 2026), 4)}

    def chat_greedy(msgs, n=40):
        t_ = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        x = tok(t_, return_tensors="pt", add_special_tokens=False).input_ids
        o = model.generate(x, attention_mask=torch.ones_like(x), do_sample=False, max_new_tokens=n,
                           pad_token_id=tok.eos_token_id, temperature=None, top_p=None, top_k=None)
        return tok.decode(o[0, x.shape[1]:], skip_special_tokens=True)

    out["cutoff.json"] = {
        "model": INSTRUCT,
        "year_probs": [year_probs(p) for p in ("The current year is ", "Copyright © ", "As of today, in the year ")],
        "asked": {
            "year_no_prompt": chat_greedy([{"role": "user", "content": "What year is it now? Answer with the year only."}]),
            "cutoff_no_prompt": chat_greedy([{"role": "user", "content": "Without looking anything up: what is the most recent month and year that your training data covers? Answer with the month and year only."}]),
            "date_with_app_prompt": chat_greedy([{"role": "system", "content": system},
                                                 {"role": "user", "content": "What is today's date? Answer with the date only."}])},
        "note": "p_among = the probability of each year renormalised over 2015-2030; each year is 4 digit tokens, so p_raw is the product of 4 next-token probabilities"}

    # ---------------- the four-token attention example, by hand
    names = ["Emma", "needs", "2,000", "packs"]
    Q = np.array([[1, 0], [1, 1], [0, 1], [0, 2]], float)
    K = np.array([[2, 0], [0, 1], [1, 3], [1, 1]], float)
    V = np.array([[4, 0], [0, 1], [0, 8], [2, 2]], float)
    S = Q @ K.T
    Ss = S / np.sqrt(2)
    M = np.where(np.tril(np.ones((4, 4))) > 0, Ss, -np.inf)
    W = np.exp(M - M.max(1, keepdims=True)); W = W / W.sum(1, keepdims=True)
    ex = np.exp(Ss[3])
    out["hand_attention.json"] = {"tokens": names, "Q": Q.tolist(), "K": K.tolist(), "V": V.tolist(),
                                  "scores": S.tolist(), "scaled": np.round(Ss, 3).tolist(),
                                  "exp_last": np.round(ex, 3).tolist(), "exp_sum_last": round(float(ex.sum()), 3),
                                  "weights": np.round(W, 3).tolist(), "outputs": np.round(W @ V, 3).tolist(),
                                  "sqrt_d": round(float(np.sqrt(2)), 4)}

    # ---------------- what NB2 computes live, recorded for its replay fallback (the notebook's own functions)
    def next_token(id_list, k=10):
        logits = model(torch.tensor([id_list])).logits[0, -1]
        p = torch.softmax(logits, -1)
        top = torch.topk(logits, 60)
        return {"top": [[show(i), int(i), R(l, 3), R(p[i], 5)] for l, i in zip(top.values[:k], top.indices[:k])],
                "logits60": [[show(i), R(l, 3)] for l, i in zip(top.values, top.indices)]}

    def greedy(id_list, n=60):
        seq, steps, past, x = list(id_list), [], None, torch.tensor([id_list])
        for _ in range(n):
            o = model(x, past_key_values=past, use_cache=True)
            past, lg = o.past_key_values, o.logits[0, -1]
            p = torch.softmax(lg, -1)
            nid = int(lg.argmax())
            v, ix = p.topk(5)
            steps.append([show(nid), nid, R(p[nid], 4), [[show(i), R(q, 4)] for q, i in zip(v, ix)]])
            if nid == tok.convert_tokens_to_ids("<|im_end|>"):
                break
            seq.append(nid)
            x = torch.tensor([[nid]])
        return steps

    def sample(id_list, T, seed, n=60):
        g = torch.Generator().manual_seed(seed)
        seq, past, x, outt = list(id_list), None, torch.tensor([id_list]), []
        for _ in range(n):
            o = model(x, past_key_values=past, use_cache=True)
            past = o.past_key_values
            nid = int(torch.multinomial(torch.softmax(o.logits[0, -1] / T, -1), 1, generator=g))
            if nid == tok.convert_tokens_to_ids("<|im_end|>"):
                break
            outt.append(nid)
            x = torch.tensor([[nid]])
        return tok.decode(outt)

    E = model.model.embed_tokens.weight
    En = E / E.norm(dim=1, keepdim=True)
    clean = torch.tensor([bool(re.fullmatch(r" [A-Za-z]{3,}", show(i))) for i in range(E.shape[0])])

    def neighbours(word, k=8):
        wid = tok(word, add_special_tokens=False).input_ids[0]
        sim = En @ En[wid]
        sim[~clean] = -2
        sim[wid] = -2
        res, seen = [], {word.strip().lower()}
        for s, i in zip(*sim.topk(40)):
            t_ = show(i)
            if t_.strip().lower() in seen:
                continue
            seen.add(t_.strip().lower())
            res.append([t_, R(s, 3)])
            if len(res) == k:
                break
        return res

    def cos(a, b):
        ia, ib = tok(a, add_special_tokens=False).input_ids[0], tok(b, add_special_tokens=False).input_ids[0]
        return R(En[ia] @ En[ib], 3)

    o = model(torch.tensor([ids]), output_attentions=True, output_hidden_states=True)
    last = len(ids) - 1
    att_last = [[[R(w, 4) for w in o.attentions[l][0, h, last, :].tolist()] for h in range(cfg.num_attention_heads)]
                for l in range(cfg.num_hidden_layers)]
    lens = []
    for l in range(1, len(o.hidden_states)):
        h_ = o.hidden_states[l][0, last]
        if l < len(o.hidden_states) - 1:
            h_ = model.model.norm(h_)
        p = torch.softmax(model.lm_head(h_), -1)
        v, ix = p.topk(3)
        lens.append([l, [[show(i), R(q, 4)] for q, i in zip(v, ix)]])
    g_steps = greedy(ids)
    _, ids_f = chat_ids(system + "\n" + FACT)
    f_steps = greedy(ids_f)
    raw_ids = tok(RAW, add_special_tokens=False).input_ids
    out["nb_qwen.json"] = {
        "model": INSTRUCT, "system": system, "question": QUESTION, "raw_prompt": RAW, "fact": FACT,
        "ids": ids, "ids_facts": ids_f, "pieces": [[p[0], p[1], p[2]] for p in pieces],
        "next_answer": next_token(ids), "next_raw": next_token(raw_ids),
        "battery_first8": [R(v, 4) for v in E[tok(" battery", add_special_tokens=False).input_ids[0]][:8]],
        "neighbours": {w.strip(): neighbours(w) for w in (" battery", " Manchester")},
        "cos": {f"{a.strip()}|{b.strip()}": cos(a, b) for a, b in ((" battery", " charger"), (" battery", " Monday"),
                                                                  (" Manchester", " Leeds"), (" Manchester", " battery"))},
        "att_last": att_last, "lens_last": lens,
        "greedy": g_steps, "greedy_text": "".join(s[0] for s in g_steps),
        "samples_t07": [sample(ids, 0.7, s) for s in range(3)],
        "greedy_facts": f_steps, "greedy_facts_text": "".join(s[0] for s in f_steps)}
    print("greedy:", out["nb_qwen.json"]["greedy_text"])
    print("facts:", out["nb_qwen.json"]["greedy_facts_text"])
    print("cut-off:", out["cutoff.json"]["asked"], [y["top"] for y in out["cutoff.json"]["year_probs"]])
    return out


@app.function(cpu=2, memory=4096, timeout=3000)
def tiny() -> dict:
    import re
    import time

    import torch
    sys.path.insert(0, "/")
    torch.set_num_threads(2)
    from l2.tinygpt import train, sample  # noqa
    text = pathlib.Path("/l2/northbridge_corpus.md").read_text()
    lines = []
    prompts = ["Stores, 26 Oct 2026: BAT-500 in Manchester stores,",
               "From: Emma Clarke\nTo: Daniel Okafor\nDate: 26 Oct 2026\nSubject:",
               "6.2 ", "Approval, 26 Oct 2026: PR/2026/04417 is"]
    m0, enc, dec, c0 = train(text, steps=0, log=lines.append)
    before = {p: sample(m0, enc, dec, p, 160, 0.8, 0) for p in prompts}
    t0 = time.time()
    model, enc, dec, curve = train(text, steps=1500, log=lines.append)
    secs = time.time() - t0
    samples = {p: {str(T): sample(model, enc, dec, p, 220, T, 0) for T in (0.5, 0.8, 1.2)} for p in prompts}
    stock = [sample(model, enc, dec, prompts[0], 40, 0.8, s) for s in range(10)]
    figs = []
    for s in stock:
        m = re.match(r"\s*([\d,]+) on hand", s[len(prompts[0]):])
        figs.append(int(m.group(1).replace(",", "")) if m else None)
    months = {"Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
    dates = sorted({(months[m], int(d)) for d, m in re.findall(r"\b(\d{1,2}) (Aug|Sep|Oct|Nov|Dec) 2026\b", text)})
    n_params = sum(p.numel() for p in model.parameters())
    return {"tinygpt.json": {"config": {"vocab": model.c.vocab_size, "block": model.c.block_size, "layers": model.c.n_layer,
                                        "heads": model.c.n_head, "d_model": model.c.n_embd, "steps": 1500, "batch": 32,
                                        "lr": 2e-3},
                             "params": n_params, "corpus_chars": len(text), "corpus_words": len(text.split()),
                             "distinct_chars": len(set(text)), "uniform_loss": round(float(torch.log(torch.tensor(float(model.c.vocab_size)))), 4),
                             "train_seconds_cpu2": round(secs, 1), "curve": curve, "log": lines,
                             "sample_untrained": before[prompts[0]], "samples_untrained": before, "samples": samples,
                             "stock_prompt": prompts[0], "stock_samples": stock, "stock_figures": figs,
                             "stock_5400": figs.count(5400),
                             "corpus_first_day": f"{dates[0][1]} {[k for k, v in months.items() if v == dates[0][0]][0]} 2026",
                             "corpus_last_day": f"{dates[-1][1]} {[k for k, v in months.items() if v == dates[-1][0]][0]} 2026"}}


@app.local_entrypoint()
def main(only: str = ""):
    sys.path.insert(0, str(COURSE / "ledgerline"))
    from ledgerline.course.l2.brain import SYSTEM_BRAIN, QUESTION as Q, FACT as F  # the app's prompt (stdlib import)
    assert Q == QUESTION and F == FACT
    calls = []
    if only in ("", "qwen"):
        calls.append(qwen.spawn(SYSTEM_BRAIN))
    if only in ("", "tiny"):
        calls.append(tiny.spawn())
    logs = HERE / "logs"
    logs.mkdir(exist_ok=True)
    for c in calls:
        res = c.get()
        for name, data in res.items():
            (logs / name).write_text(json.dumps(data, indent=1, ensure_ascii=False))
            print("wrote", logs / name)
