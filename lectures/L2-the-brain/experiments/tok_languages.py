"""Section 2: how the language of a question changes its token count (and so its cost and how much fits in the context).

    /Users/raj/.venv/bin/modal run lectures/L2-the-brain/experiments/tok_languages.py

Emma's question in 12 languages (our own translations), counted with four real tokenizers:
GPT-2 (2019, 50,257 tokens), cl100k_base (GPT-4, 2023), o200k_base (GPT-4o, 2024) and Qwen2.5 (151,665 tokens).
Writes experiments/logs/tok_languages.json.
"""
import json
import pathlib

import modal

HERE = pathlib.Path(__file__).parent
app = modal.App("l2-tok-languages")
image = modal.Image.debian_slim(python_version="3.11").pip_install("tiktoken==0.8.0", "transformers==4.46.3", "tokenizers")

SENTENCES = [
    ("English", "How many city e-bike battery packs do we have in Manchester stores?"),
    ("German", "Wie viele Akkupacks für City-E-Bikes haben wir im Lager in Manchester?"),
    ("Spanish", "¿Cuántas baterías de bicicleta eléctrica urbana tenemos en el almacén de Manchester?"),
    ("French", "Combien de batteries de vélo électrique urbain avons-nous dans le magasin de Manchester ?"),
    ("Russian", "Сколько аккумуляторов для городских электровелосипедов у нас на складе в Манчестере?"),
    ("Arabic", "كم عدد حزم بطاريات الدراجات الكهربائية للمدينة لدينا في مخازن مانشستر؟"),
    ("Hindi", "मैनचेस्टर के गोदाम में हमारे पास सिटी ई-बाइक के कितने बैटरी पैक हैं?"),
    ("Bengali", "ম্যানচেস্টারের গুদামে আমাদের কাছে কতগুলো সিটি ই-বাইক ব্যাটারি প্যাক আছে?"),
    ("Tamil", "மான்செஸ்டர் கிடங்கில் நம்மிடம் எத்தனை நகர மின்-மிதிவண்டி பேட்டரி பேக்குகள் உள்ளன?"),
    ("Chinese", "我们曼彻斯特仓库里有多少城市电动自行车电池组？"),
    ("Japanese", "マンチェスターの倉庫に都市型電動自転車のバッテリーパックはいくつありますか？"),
    ("Korean", "맨체스터 창고에 도시형 전기자전거 배터리 팩이 몇 개 있습니까?"),
]
WORDS = [("Hindi", "बैटरी"), ("Tamil", "மிதிவண்டி"), ("Chinese", "电池"), ("English", " battery")]


@app.function(image=image, timeout=600)
def count() -> dict:
    import tiktoken
    from transformers import AutoTokenizer
    qwen = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B-Instruct")
    encs = {"GPT-2": tiktoken.get_encoding("gpt2"), "GPT-4 (cl100k)": tiktoken.get_encoding("cl100k_base"),
            "GPT-4o (o200k)": tiktoken.get_encoding("o200k_base")}

    def pieces_tik(e, text):
        return [e.decode_single_token_bytes(t).decode("utf-8", errors="replace") for t in e.encode(text)]

    def pieces_qwen(text):
        return [qwen.decode([t]) for t in qwen.encode(text, add_special_tokens=False)]

    rows = []
    for lang, s in SENTENCES:
        r = {"lang": lang, "text": s, "chars": len(s), "utf8_bytes": len(s.encode("utf-8")), "tokens": {}}
        for name, e in encs.items():
            r["tokens"][name] = len(e.encode(s))
        r["tokens"]["Qwen2.5"] = len(qwen.encode(s, add_special_tokens=False))
        rows.append(r)
    eng = rows[0]["tokens"]
    for r in rows:
        r["vs_english"] = {k: round(v / eng[k], 2) for k, v in r["tokens"].items()}
    words = []
    for lang, w in WORDS:
        words.append({"lang": lang, "word": w, "utf8_bytes": len(w.encode("utf-8")),
                      "gpt2": pieces_tik(encs["GPT-2"], w), "o200k": pieces_tik(encs["GPT-4o (o200k)"], w),
                      "qwen": pieces_qwen(w)})
    vocab = {"GPT-2": encs["GPT-2"].n_vocab, "GPT-4 (cl100k)": encs["GPT-4 (cl100k)"].n_vocab,
             "GPT-4o (o200k)": encs["GPT-4o (o200k)"].n_vocab, "Qwen2.5": len(qwen)}
    return {"source": "experiments/tok_languages.py on Modal (tiktoken 0.8.0, transformers 4.46.3)",
            "note": "Translations of Emma's question are our own.", "vocab": vocab, "rows": rows, "words": words}


@app.local_entrypoint()
def main():
    d = count.remote()
    out = HERE / "logs" / "tok_languages.json"
    out.write_text(json.dumps(d, ensure_ascii=False, indent=1))
    for r in d["rows"]:
        print(f"{r['lang']:9s} bytes {r['utf8_bytes']:4d}", r["tokens"], r["vs_english"]["GPT-2"])
    for w in d["words"]:
        print(w["lang"], w["word"], w["utf8_bytes"], "gpt2", len(w["gpt2"]), "o200k", len(w["o200k"]), "qwen", len(w["qwen"]))
    print("vocab", d["vocab"])
