# %% [markdown]
# # NB2 · The Brain: how an LLM works
# **From Forms to Agents · Lecture 2 · Vizuara · Dr. Rajat Dandekar**
#
# You are the engineer Rasoi Steel Works hired to make it AI-native. Ask Rasoi now has its first piece: a large
# language model (LLM), with no tools and no Rasoi data. In this notebook you open the brain up:
#
# - **(a)** the game it plays: next-token probabilities and sampling, on a real open model (Qwen2.5-0.5B);
# - **(b)** tokens: byte-pair encoding (BPE) by hand, then a real tokenizer;
# - **(c)** attention in numpy by hand, then real attention weights;
# - **(d)** a tiny GPT built and trained from scratch on Rasoi's own text, in a few minutes on CPU;
# - **(e)** a real chat model (gemini-3.8-flash) inventing Rasoi's stock figure.
#
# **What runs live and what is replayed.** Parts (a)–(d) run for real on your Colab CPU: the open model is about
# 1 GB to download and answers in about a second. If the download fails, the cells fall back to the logits and
# attention we recorded on Modal (`bahi.course.l2`, same model, same prompts) and say so. Part (e) replays our
# recorded Gemini replies (cassette `L2v3_coldopen`) unless you set your own key.

# %% setup

# %%
# Torch and transformers are already on Colab. Elsewhere (for example a plain Python image) install the CPU wheels.
import importlib, subprocess, sys, time, json, math
for mod, args in [("torch", ["torch", "--index-url", "https://download.pytorch.org/whl/cpu"]),
                  ("transformers", ["transformers>=4.44,<4.50"])]:
    try:
        importlib.import_module(mod)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *args], check=True)
import numpy as np
import torch
import matplotlib.pyplot as plt
from bahi.course.l2 import brain
torch.manual_seed(0)
print("torch", torch.__version__)

# %% [markdown]
# ## (a) The game: predict the next token
# A language model does one thing: given the text so far, it gives **a probability to every possible next token**.
# We load a small open model, Qwen2.5-0.5B (494 million numbers), and ask it what comes after
# *"Rasoi Steel Works makes pressure"*.

# %%
MODEL_NAME = "Qwen/Qwen2.5-0.5B"
LIVE = True
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32, attn_implementation="eager").eval()
    torch.set_grad_enabled(False)
    print(f"Loaded {MODEL_NAME} in {time.time() - t0:.0f} s:", sum(p.numel() for p in model.parameters()), "parameters")
except Exception as e:  # no internet, no disk: use what we recorded on Modal
    LIVE = False
    print("Could not load the model here, so the next cells REPLAY our recorded numbers. Reason:", str(e)[:200])
REC_NEXT = brain.load("rec_next_token")

def next_token(prompt, k=10):
    """Top-k next tokens and their probabilities."""
    if not LIVE:
        return [(t["text"], t["p"]) for t in REC_NEXT[prompt]["top"][:k]]
    ids = tok(prompt, return_tensors="pt").input_ids
    logits = model(ids).logits[0, -1]
    p = torch.softmax(logits, -1)
    top = torch.topk(p, k)
    return [(tok.decode([int(i)]), round(float(v), 4)) for v, i in zip(top.values, top.indices)]

for t, p in next_token("Rasoi Steel Works makes pressure"):
    print(f"{t!r:14} {p:.4f}  " + "#" * int(60 * p))

# %% [markdown]
# Those numbers are a **probability distribution**: one number per token in the vocabulary (151,936 of them for this
# model), all adding up to 1. The model never stores "Rasoi makes pressure cookers" as a fact; it has learned that
# " cookers" usually follows "makes pressure".
#
# Now the question Ask Rasoi failed in the lecture. Same game, but the next token is a stock figure.

# %%
STOCK = "Stock report, Rasoi Steel Works, Pune.\nItem: GSK-SIL-05L, silicone gasket, 5 litre.\nOn hand in Pune stores: "
for t, p in next_token(STOCK):
    print(f"{t!r:8} {p:.4f}  " + "#" * int(60 * p))

# %% [markdown]
# (The prompt ends in a space: Qwen writes the space and each digit as separate tokens.) Every digit gets some
# probability. The true figure is 54,000, but the model has never seen Bahi's stock table, so "5" is just one
# plausible start among many. **Sampling** picks a token at random according to these
# probabilities; do it ten times and you get ten different stock figures.

# %%
def generate(prompt, n=8, temperature=1.0, seed=0):
    if not LIVE:
        return None
    torch.manual_seed(seed)
    ids = tok(prompt, return_tensors="pt").input_ids
    kw = dict(do_sample=temperature > 0, max_new_tokens=n, pad_token_id=tok.eos_token_id)
    if temperature > 0:
        kw.update(temperature=temperature, top_k=0)
    out = model.generate(ids, attention_mask=torch.ones_like(ids), **kw)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)

if LIVE:
    for s in range(10):
        print(f"seed {s}:", repr(generate(STOCK, 7, 1.0, s)))
else:
    for r in REC_NEXT["stock_samples"]:
        print(f"seed {r['seed']} (recorded):", repr(r["text"]))

# %% [markdown]
# ### Exercise 1 · softmax by hand
# The model outputs raw scores called **logits**. Softmax turns them into probabilities:
# $p_i = e^{z_i} / \sum_j e^{z_j}$. Below are the recorded top-5 logits for "Rasoi Steel Works makes pressure".
# Compute the probabilities of these five **among themselves** (so they add to 1).

# %%
top5 = [(t["text"], t["logit"]) for t in REC_NEXT["Rasoi Steel Works makes pressure"]["logits60"][:5]]
print(top5)
# TODO (exercise 1): compute probs = softmax of the five logits
SOLUTION = True
if SOLUTION:
    z = np.array([l for _, l in top5])
    probs = np.exp(z - z.max()) / np.exp(z - z.max()).sum()
    for (t, _), p in zip(top5, probs):
        print(f"{t!r:12} {p:.3f}")

# %% [markdown]
# ### Temperature
# Divide the logits by a **temperature** T before the softmax. T < 1 sharpens the distribution (the top token wins
# more often); T > 1 flattens it (rare tokens get a chance). T → 0 is "always take the top token" (greedy).

# %%
z = np.array([l["logit"] for l in REC_NEXT["Kavita needs 20,000 gaskets before the Diwali"]["logits60"]])
names = [l["text"] for l in REC_NEXT["Kavita needs 20,000 gaskets before the Diwali"]["logits60"]]
fig, axs = plt.subplots(1, 3, figsize=(13, 3), sharey=True)
for ax, T in zip(axs, (0.5, 1.0, 1.5)):
    p = np.exp((z - z.max()) / T); p /= p.sum()
    ax.bar(range(8), p[:8], color="#0b57d0"); ax.set_xticks(range(8)); ax.set_xticklabels(names[:8], rotation=45)
    ax.set_title(f"T = {T}")
plt.suptitle("Top 8 next tokens after '... before the Diwali' (renormalised over the top 60)"); plt.tight_layout(); plt.show()

# %% [markdown]
# ## (b) Tokens
# The model does not read letters or words. It reads **tokens**: pieces of text from a fixed vocabulary.
# The vocabulary is built by **byte-pair encoding (BPE)**: start from single characters, then repeatedly merge
# the most frequent neighbouring pair into a new token.
#
# Here is BPE by hand on a tiny Rasoi corpus. `_` marks the end of a word.

# %%
corpus = "gasket gaskets gasket seal gaskets seals gasket seal gasket kit gaskets set"
words = {}
for w in corpus.split():
    key = tuple(w) + ("_",)
    words[key] = words.get(key, 0) + 1

def pair_counts(words):
    pairs = {}
    for w, n in words.items():
        for a, b in zip(w, w[1:]):
            pairs[(a, b)] = pairs.get((a, b), 0) + n
    return pairs

# TODO (exercise 2): write merge(words, pair) that joins every occurrence of `pair` inside every word
def merge(words, pair):
    new = {}
    for w, n in words.items():
        out, i = [], 0
        while i < len(w):
            if i < len(w) - 1 and (w[i], w[i + 1]) == pair:
                out.append(w[i] + w[i + 1]); i += 2
            else:
                out.append(w[i]); i += 1
        new[tuple(out)] = n
    return new

vocab = sorted({c for w in words for c in w})
print("start:", len(vocab), "tokens in the vocabulary;", sum(len(w) * n for w, n in words.items()), "tokens in the corpus")
for step in range(1, 9):
    pc = pair_counts(words)
    best = max(pc, key=pc.get)
    words = merge(words, best)
    vocab.append(best[0] + best[1])
    print(f"merge {step}: {best[0]!r} + {best[1]!r} (seen {pc[best]}x) -> vocab {len(vocab)}, corpus "
          f"{sum(len(w) * n for w, n in words.items())} tokens | gaskets = {[w for w in words if ''.join(w) == 'gaskets_'][0]}")

# %% [markdown]
# Real tokenizers do the same with tens of thousands of merges learnt from huge text. Watch how Qwen's tokenizer
# splits Rasoi's text: digits one at a time, the rupee sign as raw bytes, Hindi in many small pieces.

# %%
REC_TOK = brain.load("rec_tokens")
SENTENCES = [s["text"] for s in REC_TOK["sentences"]]
for s, rec in zip(SENTENCES, REC_TOK["sentences"]):
    if LIVE:
        ids = tok(s).input_ids
        shown = [tok.decode([i]) for i in ids]
    else:
        shown = [p["text"] if p["text"] is not None else "<byte>" for p in rec["qwen"]]
    print(f"{len(s):3} characters, {len(s.split()):2} words -> {len(shown):2} tokens:", " | ".join(shown))

# %% [markdown]
# Token counts matter for three reasons: the **context window** (how many tokens fit at once), **cost** (you pay per
# token) and **speed** (the model writes one token at a time). Hindi text costs several times more tokens than the
# same sentence in English letters.

# %% [markdown]
# ## (c) Attention, by hand and for real
# Each token makes three vectors: a **query** (what am I looking for?), a **key** (what do I contain?) and a
# **value** (what do I pass on?). A token's new vector is a weighted sum of the values of the tokens before it,
# weighted by how well its query matches their keys.
#
# Four tokens, two numbers each, small enough to do with a pencil:

# %%
tokens = ["Kavita", "needs", "20,000", "gaskets"]
Q = np.array([[1, 0], [1, 1], [0, 1], [0, 2]], float)
K = np.array([[2, 0], [0, 1], [1, 3], [1, 1]], float)
V = np.array([[4, 0], [0, 1], [0, 8], [2, 2]], float)

def softmax(x):
    e = np.exp(x - x.max(-1, keepdims=True)); return e / e.sum(-1, keepdims=True)

scores = Q @ K.T / np.sqrt(2)                        # 1. match every query with every key, scale by sqrt(d)
mask = np.tril(np.ones((4, 4))) > 0                  # 2. causal mask: a token may look only at itself and earlier
weights = softmax(np.where(mask, scores, -np.inf))   # 3. softmax per row
out = weights @ V                                    # 4. weighted sum of values
print("weights (row = the token that looks, column = the token looked at)\n", np.round(weights, 3))
print("new vector for 'gaskets':", np.round(out[3], 3))

# %% [markdown]
# ### Exercise 3 · one row by hand
# Compute the attention weights of the token "needs" (row 2) yourself: its two scores (it may see only "Kavita" and
# "needs"), divide by √2, softmax, then the weighted sum of those two values. Check against the matrix above.

# %%
# TODO (exercise 3): weights_needs and out_needs, by hand with numpy
SOLUTION = True
if SOLUTION:
    s = np.array([Q[1] @ K[0], Q[1] @ K[1]]) / np.sqrt(2)
    weights_needs = np.exp(s) / np.exp(s).sum()
    out_needs = weights_needs @ V[:2]
    print(np.round(weights_needs, 3), np.round(out_needs, 3))

# %% [markdown]
# Now the real thing. Qwen2.5-0.5B has 24 layers with 14 attention heads each. We read the attention weights for
# Kavita's sentence and look at a head that mostly looks one token back.

# %%
SENT = "Kavita needs 20,000 gaskets before the Diwali run."
REC_ATT = brain.load("rec_attention")
if LIVE:
    ids = tok(SENT, return_tensors="pt").input_ids
    att = model(ids, output_attentions=True).attentions      # 24 tensors of shape [1, 14, T, T]
    toks = [tok.decode([i]) for i in ids[0]]
    A = lambda L, H: att[L][0, H].numpy()
else:
    toks = REC_ATT["tokens"]
    A = lambda L, H: np.array(REC_ATT["att"][L][H])
L, H = REC_ATT["prev_head"]["layer"], REC_ATT["prev_head"]["head"]
plt.figure(figsize=(6, 5)); plt.imshow(A(L, H), cmap="Blues"); plt.xticks(range(len(toks)), toks, rotation=60)
plt.yticks(range(len(toks)), toks); plt.title(f"layer {L}, head {H}: looks one token back"); plt.colorbar(); plt.show()

# %% [markdown]
# ### Exercise 4 · find a head
# Search all 24 × 14 heads for the one where the token " gaskets" puts the most weight on the digits of 20,000.
# (In our run: layer 8, head 5, with 77%.)

# %%
gi = REC_ATT["gaskets_index"]                                          # the last piece of " gaskets"
num = [i for i in REC_ATT["number_indices"] if toks[i].strip().isdigit()]  # the digits of "20,000" (not the comma or space)
print("gaskets ->", repr(toks[gi]), "| number pieces ->", [toks[i] for i in num])
# TODO (exercise 4): best = (layer, head) maximising A(layer, head)[gi, num].sum()
SOLUTION = True
if SOLUTION:
    best = max(((l, h) for l in range(24) for h in range(14)), key=lambda lh: A(*lh)[gi, num].sum())
    print("head", best, "puts", round(float(A(*best)[gi, num].sum()), 3), "of gaskets' attention on", [toks[i] for i in num])

# %% [markdown]
# ## (d) A tiny GPT from scratch
# Everything above, in about 80 lines of PyTorch: token and position embeddings, a stack of blocks (attention +
# MLP, each with a residual connection and a layer norm), a final layer that gives one score per character.
# We train it on Rasoi's own text: purchase notes, stores entries, e-mails and policy lines (1,19,651
# characters, all fictional), at the character level.

# %%
import torch.nn as nn
import torch.nn.functional as F

class CausalSelfAttention(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.n_head, self.d = n_head, n_embd // n_head
        self.qkv, self.proj, self.drop = nn.Linear(n_embd, 3 * n_embd), nn.Linear(n_embd, n_embd), nn.Dropout(dropout)
        self.register_buffer("mask", torch.tril(torch.ones(block_size, block_size)).bool())
    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_head, self.d).transpose(1, 2) for t in (q, k, v))
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.d)
        att = att.masked_fill(~self.mask[:T, :T], float("-inf"))
        att = self.drop(F.softmax(att, dim=-1))
        return self.proj((att @ v).transpose(1, 2).contiguous().view(B, T, C))

class Block(nn.Module):
    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.ln1, self.attn = nn.LayerNorm(n_embd), CausalSelfAttention(n_embd, n_head, block_size, dropout)
        self.ln2 = nn.LayerNorm(n_embd)
        self.mlp = nn.Sequential(nn.Linear(n_embd, 4 * n_embd), nn.GELU(), nn.Linear(4 * n_embd, n_embd), nn.Dropout(dropout))
    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))

class TinyGPT(nn.Module):
    def __init__(self, vocab_size, block_size=128, n_layer=4, n_head=4, n_embd=128, dropout=0.1):
        super().__init__()
        self.block_size = block_size
        self.tok, self.pos = nn.Embedding(vocab_size, n_embd), nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)])
        self.ln_f, self.head = nn.LayerNorm(n_embd), nn.Linear(n_embd, vocab_size, bias=False)
    def forward(self, idx, targets=None):
        x = self.tok(idx) + self.pos(torch.arange(idx.shape[1]))
        logits = self.head(self.ln_f(self.blocks(x)))
        loss = None if targets is None else F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss
    @torch.no_grad()
    def generate(self, idx, n, temperature=1.0, g=None):
        for _ in range(n):
            logits, _ = self(idx[:, -self.block_size:])
            p = F.softmax(logits[:, -1, :] / temperature, dim=-1)
            idx = torch.cat([idx, torch.multinomial(p, 1, generator=g)], dim=1)
        return idx

import importlib.resources as ir
text = (ir.files("bahi.course.l2") / "rasoi_corpus.md").read_text()
chars = sorted(set(text)); stoi = {c: i for i, c in enumerate(chars)}
enc = lambda s: [stoi[c] for c in s]; dec = lambda ids: "".join(chars[i] for i in ids)
data = torch.tensor(enc(text)); n = int(0.9 * len(data)); train_d, val_d = data[:n], data[n:]
print(len(text), "characters,", len(chars), "distinct characters (our vocabulary)")
print(text[:300])

# %% [markdown]
# ### Exercise 5 · the loss before training
# The loss is **cross-entropy**: the average of −log p(the true next character). Before training the model guesses
# roughly uniformly over the vocabulary. What loss do you expect? Compute it, then check against step 0 below.

# %%
# TODO (exercise 5): expected_loss = ...
SOLUTION = True
if SOLUTION:
    expected_loss = math.log(len(chars))
    print(f"uniform guess over {len(chars)} characters: loss = ln({len(chars)}) = {expected_loss:.3f}")

# %%
torch.set_grad_enabled(True)   # part (a) switched gradients off for the frozen model; training needs them
torch.manual_seed(1337); g = torch.Generator().manual_seed(1337)
STEPS, BATCH, LR, BLOCK = 1500, 32, 2e-3, 128
gpt = TinyGPT(len(chars), BLOCK)
opt = torch.optim.AdamW(gpt.parameters(), lr=LR, weight_decay=0.01)
print(sum(p.numel() for p in gpt.parameters()), "parameters")
def batch(d):
    ix = torch.randint(len(d) - BLOCK - 1, (BATCH,), generator=g)
    return torch.stack([d[i:i + BLOCK] for i in ix]), torch.stack([d[i + 1:i + 1 + BLOCK] for i in ix])
curve, t0 = [], time.time()
for step in range(STEPS + 1):
    if step % 100 == 0:
        gpt.eval()
        with torch.no_grad():
            tl = sum(gpt(*batch(train_d))[1].item() for _ in range(10)) / 10
            vl = sum(gpt(*batch(val_d))[1].item() for _ in range(10)) / 10
        gpt.train(); curve.append((step, tl, vl))
        print(f"step {step:5d}  train loss {tl:.3f}  val loss {vl:.3f}  ({time.time() - t0:.0f} s)")
    if step == STEPS:
        break
    for gr in opt.param_groups:
        gr["lr"] = LR * min(1.0, (step + 1) / 100) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * step / STEPS)))
    x, y = batch(train_d)
    _, loss = gpt(x, y)
    opt.zero_grad(set_to_none=True); loss.backward()
    torch.nn.utils.clip_grad_norm_(gpt.parameters(), 1.0); opt.step()
plt.plot([c[0] for c in curve], [c[1] for c in curve], label="train"); plt.plot([c[0] for c in curve], [c[2] for c in curve], label="validation")
plt.xlabel("step"); plt.ylabel("loss (cross-entropy)"); plt.legend(); plt.title("Tiny GPT on Rasoi's text"); plt.show()

# %% [markdown]
# Now let it write. Give it the start of a stores line and it continues in Rasoi's style, with a stock figure it
# makes up: it learnt what a stock line **looks like**, not what Rasoi **has**.

# %%
gpt.eval()
def sample(prompt, n=200, temperature=0.8, seed=0):
    gg = torch.Generator().manual_seed(seed)
    return dec(gpt.generate(torch.tensor([enc(prompt)]), n, temperature, gg)[0].tolist())
print(sample("From: Kavita Joshi\nTo: Rohit Mehta\nSubject:", 260))
print("---")
for s in range(5):
    print(sample("Stores, 26 Oct 2026: GSK-SIL-05L in Pune stores,", 40, 0.8, s))

# %% [markdown]
# ### Exercise 6 · temperature on your own model
# Sample the same prompt at temperature 0.3, 1.0 and 2.0. What happens to the spelling and to the numbers?

# %%
# TODO (exercise 6)
SOLUTION = True
if SOLUTION:
    for T in (0.3, 1.0, 2.0):
        print(f"T={T}:", sample("Approval, 26 Oct 2026: PR/2026/04417 is", 120, T, 1).replace("\n", " "))

# %% [markdown]
# ## (e) A real chat model, with no tools
# Ask Rasoi's brain is gemini-3.8-flash. A chat is a list of messages (system, user, assistant). The provider turns
# the list into one long sequence of tokens, and the model continues it. We send the system prompt a first chatbot
# often has, then Kavita's question. (Replayed from cassette `L2v3_coldopen` unless you set a key.)

# %%
from bahi.llm import LLM
llm = LLM(brain.MODEL, cassette="L2v3_coldopen")
msgs = brain.messages(brain.QUESTION, brain.SYSTEM_CONFIDENT)
for m in msgs:
    print(f"[{m['role']}] {m['content']}")
r = llm.chat(msgs)
print("\nAsk Rasoi:", r.content)
print(f"tokens in {r.tokens_in}, tokens out {r.tokens_out}, {r.seconds} s, ₹{r.cost_inr} (replayed: {r.replayed})")
print("The truth in Bahi (check_stock): Pune main stores", brain.TRUE_ANSWER)

# %% [markdown]
# With a more modest system prompt the same model usually says it cannot see the inventory:

# %%
r0 = llm.chat(brain.messages(brain.QUESTION, brain.SYSTEM_BRAIN))
print("Ask Rasoi (modest prompt):", r0.content)

# %% [markdown]
# ### Exercise 7 · the second turn
# Ask the follow-up *"Where did that number come from?"*. Remember: the model has no memory between calls. You must
# send the **whole history** again: system, user, the assistant's reply, then the new question. Watch tokens_in grow.

# %%
# TODO (exercise 7): build msgs2 and call llm.chat(msgs2)
SOLUTION = True
if SOLUTION:
    msgs2 = msgs + [{"role": "assistant", "content": r.content}, {"role": "user", "content": brain.FOLLOW_UP}]
    r2 = llm.chat(msgs2)
    print("Ask Rasoi:", r2.content)
    print(f"tokens in: turn 1 = {r.tokens_in}, turn 2 = {r2.tokens_in}")

# %% [markdown]
# It invents a source as fluently as it invented the number. Nothing in the model is connected to Bahi.
# Lecture 3 gives it the facts (knowledge) and Lecture 4 lets it look things up (tools).
#
# ## Your module (starts Assignment A2)
# Pick your capstone module (for example `hr_leave`). Its policy documents are in `bahi/modules/<module>/docs/`.
# 1. Train the tiny GPT on them (change `text` below) and report the final validation loss and three samples.
# 2. Write one question your module's users ask that needs Bahi's live data, and explain why the bare model cannot
#    answer it. See `A2.md`.

# %%
MY_MODULE = "hr_leave"
docs = ir.files("bahi.modules") / MY_MODULE / "docs"
my_text = "\n\n".join(p.read_text() for p in sorted(docs.iterdir()) if p.name.endswith(".md"))
print(MY_MODULE, ":", len(my_text), "characters,", len(set(my_text)), "distinct characters")
print(my_text[:400])
