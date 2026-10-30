"""A tiny GPT, from scratch, in about 80 lines of PyTorch (Lecture 2). Character level.

The notebook NB2 builds exactly this code cell by cell; the experiment script imports it to log the
numbers the deck shows. Same seed, same corpus, same settings.
"""
import math
import time

import torch
import torch.nn as nn
import torch.nn.functional as F


class Config:
    def __init__(self, vocab_size, block_size=128, n_layer=4, n_head=4, n_embd=128, dropout=0.1):
        self.vocab_size, self.block_size = vocab_size, block_size
        self.n_layer, self.n_head, self.n_embd, self.dropout = n_layer, n_head, n_embd, dropout


class CausalSelfAttention(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.n_head, self.d = c.n_head, c.n_embd // c.n_head
        self.qkv = nn.Linear(c.n_embd, 3 * c.n_embd)       # one matrix makes query, key and value
        self.proj = nn.Linear(c.n_embd, c.n_embd)
        self.drop = nn.Dropout(c.dropout)
        self.register_buffer("mask", torch.tril(torch.ones(c.block_size, c.block_size)).bool())

    def forward(self, x):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)
        q, k, v = (t.view(B, T, self.n_head, self.d).transpose(1, 2) for t in (q, k, v))
        att = (q @ k.transpose(-2, -1)) / math.sqrt(self.d)          # how well each query matches each key
        att = att.masked_fill(~self.mask[:T, :T], float("-inf"))    # causal mask: no peeking at later tokens
        att = self.drop(F.softmax(att, dim=-1))                      # scores -> weights that sum to 1
        y = (att @ v).transpose(1, 2).contiguous().view(B, T, C)     # weighted sum of values, heads joined
        return self.proj(y)


class Block(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.ln1, self.attn = nn.LayerNorm(c.n_embd), CausalSelfAttention(c)
        self.ln2 = nn.LayerNorm(c.n_embd)
        self.mlp = nn.Sequential(nn.Linear(c.n_embd, 4 * c.n_embd), nn.GELU(), nn.Linear(4 * c.n_embd, c.n_embd),
                                 nn.Dropout(c.dropout))

    def forward(self, x):
        x = x + self.attn(self.ln1(x))   # residual: add what attention found
        x = x + self.mlp(self.ln2(x))    # residual: add what the MLP computed
        return x


class TinyGPT(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.c = c
        self.tok = nn.Embedding(c.vocab_size, c.n_embd)   # token -> vector
        self.pos = nn.Embedding(c.block_size, c.n_embd)   # position -> vector
        self.blocks = nn.Sequential(*[Block(c) for _ in range(c.n_layer)])
        self.ln_f = nn.LayerNorm(c.n_embd)
        self.head = nn.Linear(c.n_embd, c.vocab_size, bias=False)  # vector -> one score per token

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        logits = self.head(self.ln_f(self.blocks(x)))
        loss = None if targets is None else F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, n, temperature=1.0, generator=None):
        for _ in range(n):
            logits, _ = self(idx[:, -self.c.block_size:])
            p = F.softmax(logits[:, -1, :] / temperature, dim=-1)
            idx = torch.cat([idx, torch.multinomial(p, 1, generator=generator)], dim=1)
        return idx


def encoder(text):
    chars = sorted(set(text))
    stoi = {ch: i for i, ch in enumerate(chars)}
    return chars, (lambda s: [stoi[ch] for ch in s]), (lambda ids: "".join(chars[i] for i in ids))


def train(text, steps=1500, batch=32, lr=2e-3, seed=1337, eval_every=100, log=print, **cfg):
    torch.manual_seed(seed)
    chars, enc, dec = encoder(text)
    data = torch.tensor(enc(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_d, val_d = data[:n], data[n:]
    c = Config(len(chars), **cfg)
    model = TinyGPT(c)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    g = torch.Generator().manual_seed(seed)

    def get(split):
        d = train_d if split == "train" else val_d
        ix = torch.randint(len(d) - c.block_size - 1, (batch,), generator=g)
        return torch.stack([d[i:i + c.block_size] for i in ix]), torch.stack([d[i + 1:i + 1 + c.block_size] for i in ix])

    @torch.no_grad()
    def estimate():
        model.eval()
        out = {s: sum(model(*get(s))[1].item() for _ in range(10)) / 10 for s in ("train", "val")}
        model.train()
        return out

    curve, t0 = [], time.time()
    for step in range(steps + 1):
        if step % eval_every == 0:
            e = estimate()
            curve.append({"step": step, "train": round(e["train"], 4), "val": round(e["val"], 4),
                          "seconds": round(time.time() - t0, 1)})
            log(f"step {step:5d}  train loss {e['train']:.3f}  val loss {e['val']:.3f}  ({time.time() - t0:.0f} s)")
        if step == steps:
            break
        for gr in opt.param_groups:   # short warm-up, then cosine decay
            gr["lr"] = lr * min(1.0, (step + 1) / 100) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * step / steps)))
        x, y = get("train")
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
    return model, enc, dec, curve


def sample(model, enc, dec, prompt, n=200, temperature=0.8, seed=0):
    model.eval()
    g = torch.Generator().manual_seed(seed)
    idx = torch.tensor([enc(prompt)], dtype=torch.long)
    return dec(model.generate(idx, n, temperature, generator=g)[0].tolist())
