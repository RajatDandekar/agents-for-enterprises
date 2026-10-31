"""One-off: rebuild index.html in the v5 order (REWORK_V5.md). Reads the v4 deck from the scratchpad backup.

    python3 lectures/L2-the-brain/tools_v5_assemble.py <v4 index.html>
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
src = pathlib.Path(sys.argv[1]).read_text()
head, rest = src.split('<div class="deck" id="deck">', 1)
body, tail = rest.rsplit("\n</div>\n<script src=\"figdata.js\">", 1)
S = re.findall(r"<section.*?</section>", body, re.S)
assert len(S) == 73, len(S)
old = lambda i: S[i - 1]  # 1-based, as in the v4 slide list


def sq(section, text, cue="Answer in one line in the chat · then we watch the film"):
    return f'''<section class="slide q hero" data-plain="1">
  <span class="hero-num q-mark" aria-hidden="true">?</span>
  <div class="qbox">
    <p class="q-label">Ask the class · {section} · <span class="qnum"></span></p>
    <h2 class="q-text">{text}</h2>
    <p class="q-cue">{cue}</p>
  </div>
</section>'''


def check(film, items):
    lis = "\n".join(f'      <li><span class="chk-q"><b>{i + 1}</b>{q}</span><span class="chk-a step">{a}</span></li>'
                    for i, (q, a) in enumerate(items))
    return f'''<section class="slide q hero chk" data-plain="1">
  <span class="hero-num q-mark" aria-hidden="true">✓</span>
  <div class="qbox">
    <p class="q-label">Check · after {film}</p>
    <ol class="chk-list">
{lis}
    </ol>
  </div>
</section>'''


def film(plate, name, title, what):
    return f'''<section class="slide" data-plate="{plate}">
  <div class="lec-top" style="top:96px"><h2 style="font-size:44px">{title}</h2></div>
  <div class="fig" data-fig="film" data-name="{name}" data-what="{what}" style="left:250px;top:180px;width:1100px;height:619px"></div>
</section>'''


def part(n, label, h1, recall=None, lede=None):
    r = f'\n    <div class="recall"><b>Last section</b>{recall}</div>' if recall else ""
    l = f'\n    <p class="lede">{lede}</p>' if lede else ""
    return f'''<section class="slide part" data-plain="1" data-num="{n}">
  <div class="center"><span class="num">{label}</span>{r}
    <h1 class="q2">{h1}</h1>{l}</div>
</section>'''


def retitle(sec, plate, title, name=None):
    sec = re.sub(r'data-plate="[^"]*"', f'data-plate="{plate}"', sec, 1)
    sec = re.sub(r'<h2 style="font-size:44px">.*?</h2>', f'<h2 style="font-size:44px">{title}</h2>', sec, 1)
    if name:
        sec = re.sub(r'data-name="[^"]*"', f'data-name="{name}"', sec, 1)
    return sec


def hidden(n):
    return "".join('<span class="step" style="display:none"></span>' for _ in range(n))


def code(lines, hl=()):
    out = []
    for i, ln in enumerate(lines, 1):
        t = html.escape(ln, quote=False)
        t = re.sub(r"(#.*)$", r'<span class="cmt">\1</span>', t)
        out.append(f'<span class="ln{" hl" if i in hl else ""}">{t or " "}</span>')
    return "".join(out)


N = []
add = N.append

# ---------------- opening (unchanged) ----------------
for i in range(1, 10):
    add(old(i))
add(check("the overture", [
    ("How many tokens go into the model for Emma’s question?", "100: her question, the app’s instructions and the chat markers."),
    ("In one pass through the model, how many tokens are chosen?", "One, out of 151,936. Then the whole pass runs again for the next one."),
    ("What did the model answer, and what is the truth?", "100 battery packs. Ledgerline says 5,400."),
]))

# ---------------- 1 · next-token prediction ----------------
add(old(10)); add(old(11))
add(sq("Section 1", "What does a language model <em>actually do?</em>"))
add(retitle(old(13), "Film · 1 · Next-token prediction", "Film · 1 · Next-token prediction"))
add(check("Film 1", [
    ("At the end of one pass, what does the model give out?", "A probability for every entry in its vocabulary: 151,936 numbers that add up to 1."),
    ("Which first token was most likely, and how likely?", "“We”, at 56%. Then “As” 8%, “Manchester” 6%."),
    ("At the first digit of the number, how sure was it of “1”?", "34%. “2” had 21% and “5” 12%. Every digit is a bet."),
]))

# ---------------- 2 · tokens ----------------
add(old(14)); add(old(15)); add(old(16))
add('''<section class="slide" data-plate="Two Extremes">
  <div class="lec-top"><h2>How small should a piece be?</h2><p class="sub">Emma’s question, cut three ways. Click to see each.</p></div>
  <div class="fig" data-fig="extremes" style="left:100px;top:230px;width:1400px;height:620px"></div>
  ''' + hidden(2) + '''
</section>''')
add(old(17).replace('<h2>Where the pieces come from</h2>', '<h2>BPE: building the middle</h2>'))
add('''<section class="slide" data-plate="Try It Live · Tiktokenizer">
  <div class="col" style="width:380px">
    <h2>Try it live</h2>
    <p>This is Qwen’s own tokenizer, the model we open today, running in the page.</p>
    <p class="step small">Type Emma’s question. Then try:</p>
    <ol class="legend step" style="margin-top:6px;font-size:19px">
      <li><span class="n">1</span><span><code>5,400</code> and <code>five thousand four hundred</code></span></li>
      <li><span class="n">2</span><span><code>Northbridge</code>, <code>BAT-500</code>, a typo: <code>baterry</code></span></li>
      <li><span class="n">3</span><span>A sentence in your own language</span></li>
      <li><span class="n">4</span><span>The same sentence with the model set to gpt-4o</span></li>
    </ol>
  </div>
  <div class="fig" data-fig="tiktok" style="left:520px;top:100px;width:980px;height:740px"></div>
</section>''')
add(old(18))
add('''<section class="slide" data-plate="Language Changes the Count">
  <div class="col" style="width:380px">
    <h2>The same question, twelve languages</h2>
    <p>Emma’s question, translated, and counted by four real tokenizers. English: 14–15 tokens on all four.</p>
    <p><b>GPT-2</b> (2019, 50,257 pieces): Tamil takes <b class="b">223</b> tokens, 15× English. One token per byte.</p>
    <p class="step"><b>GPT-4</b> (2023, 100,277 pieces): Tamil 106, about 7×.</p>
    <p class="step"><b>GPT-4o</b> (2024, 200,019 pieces): Tamil 32, about 2×. A bigger, more multilingual list.</p>
    <p class="step"><b>Qwen2.5</b> (151,665 pieces), trained on a lot of Chinese: Chinese takes <b class="g">13</b>, fewer than English. Tamil still takes 87, about 6×.</p>
  </div>
  <div class="fig" data-fig="langbars" style="left:520px;top:110px;width:980px;height:700px"></div>
  <div class="cap" style="left:520px;top:824px;width:980px">Our own translations of Emma’s question. Counted on Modal with tiktoken (gpt2, cl100k_base, o200k_base) and Qwen2.5’s tokenizer. <code>experiments/logs/tok_languages.json</code>.</div>
</section>''')
add('''<section class="slide" data-plate="Why Languages Cost More">
  <div class="col" style="width:400px">
    <h2>Why: merges follow the training text</h2>
    <p>Text is stored as bytes. An English letter is 1 byte; a Hindi, Tamil or Chinese character is 3.</p>
    <p class="step">BPE merges the pairs it saw most often. If a tokenizer saw little Tamil, it learnt few Tamil merges, and Tamil stays in small pieces, sometimes <b class="b">pieces of a single letter</b>.</p>
    <p class="step"><b>What it costs you:</b> more tokens to pay for, a context window that fills sooner, slower replies, and often worse answers, because each piece carries less meaning.</p>
    <p class="step small">Check your users’ languages on your model’s tokenizer before you set a budget.</p>
  </div>
  <div class="fig" data-fig="langwhy" style="left:540px;top:120px;width:960px;height:700px"></div>
  ''' + hidden(0) + '''
</section>''')
add(old(19).replace('<p class="step">The same question takes more tokens in other languages, so it costs more.</p>',
                    '<p class="step">The same question in Tamil costs up to 15× more, depending on the tokenizer (two slides back).</p>'))
add(sq("Section 2", "How does text get into a model, and <em>why not just whole words?</em>"))
add(retitle(old(21), "Film · 2 · Tokens", "Film · 2 · Tokens"))
add(check("Film 2", [
    ("Of the 100 tokens, how many are Emma’s own question?", "15. The app’s instructions take 72, and the chat markers 13."),
    ("How many tokens is “5,400”?", "Five: 5 , 4 0 0. Qwen cuts numbers digit by digit."),
    ("Why not one token per word?", "The list would need every word, name, code and typo there is. A missing word is lost as [UNK]. BPE never loses anything: it falls back to smaller pieces."),
]))

# ---------------- 3 · vectors ----------------
add(old(22)); add(old(23)); add(old(24))
add(sq("Section 3", "How can a list of numbers carry <em>the meaning of a word?</em>"))
add(retitle(old(26), "Film · 3 · Vectors", "Film · 3 · Vectors"))
add(check("Film 3", [
    ("How many numbers are in one token’s vector?", "896, in Qwen2.5-0.5B."),
    ("How many rows does the embedding table have?", "151,936: one row per token id."),
    ("Which words sit nearest to “Manchester”, and why?", "Liverpool, Nottingham, Leicester, Leeds. Words used in similar sentences end up with similar rows."),
]))

# ---------------- 4 · attention ----------------
for i in (27, 28, 29, 30, 31):
    add(old(i))
add(sq("Section 4", "How does a word know <em>what is around it?</em>"))
add(retitle(old(33), "Film · 4 · Query, key and value", "Film · 4 · Query, key and value"))
add(check("Film 4", [
    ("How long are the query, key and value in one attention unit?", "64 numbers each."),
    ("Why are the scores divided by 8?", "8 is √64. It stops the scores growing with the vector’s length, so softmax does not get too sharp."),
    ("How much of the last token’s weight went to “Manchester”?", "65.2%. Its score, 7.81, led the next one by 2.4, and softmax magnifies every lead."),
]))

# ---------------- 5 · inside the stack ----------------
add(part(5, "Section 5 of 9 · Inside the stack", "What happens between reading and answering?",
         "One attention unit let the last token find “Manchester”. Now: the real model runs many of them, in 24 blocks."))
add(old(35))
add('''<section class="slide" data-plate="Every Token, Every Block">
  <div class="col" style="width:440px">
    <h2>Which tokens change?</h2>
    <p>All 100 of Emma’s tokens go through every block <b>together</b>, in one pass.</p>
    <p class="step">Attention: each token mixes in what it needs from the tokens <b>before</b> it, never after.</p>
    <p class="step">MLP: each token’s vector is reworked on its own.</p>
    <p class="step"><b class="a">Only the last position</b> becomes the next token. The other 99 are what it reads, in every block.</p>
  </div>
  <div class="fig" data-fig="alltoks" style="left:600px;top:150px;width:900px;height:600px"></div>
</section>''')
add(sq("Section 5", "Inside the 24 blocks, <em>which of the 100 tokens change</em>, and which one makes the answer?"))
add(retitle(old(37), "Film · 5 · Inside the stack", "Film · 5 · Inside the stack: every token, 24 blocks", "blocks"))
add(check("Film 5", [
    ("In one pass, how many of the 100 vectors does each block change?", "All 100. Attention mixes each with the tokens before it; the MLP reworks each one alone."),
    ("Which vector is turned into the next token?", "Only the last position’s, after block 24. The other 99 supply what it reads at every block."),
    ("How many blocks, and how long is each vector between them?", "24 blocks, and 896 numbers all the way up."),
]))
add('''<section class="slide" data-plate="Why Fourteen Heads">
  <div class="col" style="width:470px">
    <h2>Why many heads?</h2>
    <div class="def"><b>Head</b>One attention unit, with its own query matrix. It asks one question of the earlier tokens.</div>
    <p class="step">One head makes one set of weights: it can look one way at a time. The last position needs several things at once.</p>
    <p class="step">So each block runs <b>14 heads side by side</b>. The 896 numbers are split: 14 × 64 = 896. Each head writes 64 numbers, the 14 are joined back to 896, and one more matrix mixes them.</p>
    <p class="step small">To save memory, Qwen’s 14 heads share 2 sets of keys and values, 7 heads to a set (grouped-query attention). Each head keeps its own query.</p>
  </div>
  <div class="hq" style="position:absolute;left:640px;top:150px;width:860px">
    <div class="card step"><span class="tag">What item?</span>battery, packs</div>
    <div class="card step"><span class="tag">Where?</span>Manchester, stores</div>
    <div class="card step"><span class="tag">Who is speaking, and where am I?</span>the chat markers, the first token</div>
    <div class="card step"><span class="tag">What came just before?</span>the previous token</div>
    <p class="small" style="margin-top:6px">Four questions to build intuition. Next: what real heads did.</p>
  </div>
</section>''')
add('''<section class="slide" data-plate="What Real Heads Did">
  <div class="lec-top"><h2>What real heads did on Emma’s question</h2><p class="sub">Measured in Qwen2.5-0.5B on the recorded pass. Click to reveal each.</p></div>
  <div class="fig" data-fig="headsgal" style="left:100px;top:250px;width:1400px;height:560px"></div>
  ''' + hidden(5) + '''
</section>''')
add(sq("Section 5", "Why would one block need <em>fourteen heads</em> instead of one?"))
add(retitle(old(38), "Film · 5b · Heads", "Film · 5b · Heads: fourteen ways of looking", "heads"))
add(check("Film 5b", [
    ("How many heads does each block have, and how many numbers does each head use?", "14 heads × 64 numbers = 896."),
    ("How many sets of keys and values do those 14 heads share?", "2. Seven query heads share each set (grouped-query attention)."),
    ("Name one thing a real head did on Emma’s question.", "Block 24, head 2 put 65% of its weight on “Manchester”. Block 12, head 13 rested all of its weight on the first token, when it had nothing to add."),
]))

# ---------------- 6 · logits and softmax ----------------
add(part(6, "Section 6 of 9 · Logits and softmax", "How does the last vector become the next token?",
         "Every block changed all 100 vectors; the last one now holds the answer as it forms. Now: a vector is not a word."))
add(old(41))
add(sq("Section 6", "How does the last vector become <em>the next token?</em>"))
add(retitle(old(43), "Film · 6 · Logits and softmax", "Film · 6 · From the last vector to the next token: logits and softmax", "next_token"))
add(check("Film 6", [
    ("How many scores (logits) does the last vector produce?", "151,936: one dot product with each row of the table."),
    ("Which table are those rows from?", "The same embedding table that turned the tokens into vectors. Qwen2.5-0.5B uses it both ways."),
    ("What does temperature do?", "It divides the logits before softmax. At 0 the top token always wins; at 0.7 “We” rises to 82%; at 1.2 it falls to 41%."),
]))

# ---------------- 7 · generation ----------------
add(part(7, "Section 7 of 9 · Generation", "How is the entire answer generated?",
         "One pass gives one token. Now: Emma got a whole sentence, with a number in it."))
add(old(45)); add(old(46)); add(old(47))
add(sq("Section 7", "One pass gives one token. <em>How is the entire answer generated?</em>"))
add(retitle(old(49), "Film · 7 · Generation", "Film · 7 · Generating the whole answer, token by token", "generation"))
add(check("Film 7", [
    ("How many passes does the 20-token answer take?", "One per token: 20, and one more that picks the end marker &lt;|im_end|&gt;."),
    ("When it picked the second “0” of “100”, which tokens could it see?", "All 100 prompt tokens and every answer token before it. Never one after."),
    ("What is kept between passes, so the earlier tokens are not worked out again?", "Their keys and values: the KV cache. Each new token needs one new column through the 24 blocks."),
]))

# ---------------- 8 · training ----------------
add(part(8, "Section 8 of 9 · Training", "Where did the numbers in the blocks come from?",
         "The whole machine writes the answer, token by token. Now: every step used numbers we never explained."))
add(film("Film · 8a · 494 million numbers", "params", "Film · 8a · 494 million numbers", "the 24 blocks and the numbers inside them."))
add('''<section class="slide" data-plate="Where the Numbers Live">
  <div class="lec-top"><h2>494,032,768 numbers to set</h2><p class="sub">Every matrix in every block, counted from the model’s own shapes.</p></div>
  <div class="fig" data-fig="paramtree" style="left:100px;top:240px;width:1400px;height:600px"></div>
  ''' + hidden(2) + '''
</section>''')
add(sq("Section 8", "Every answer came from these 494 million numbers. <em>Who chose them, and how?</em>"))
add('''<section class="slide" data-plate="The Whole Corpus">
  <div class="col" style="width:400px">
    <h2>What we trained on</h2>
    <p>To watch training happen, we train a tiny GPT ourselves, on all of Northbridge’s own text.</p>
    <p class="step small">Most of it is generated by <code>corpus.py</code> from Northbridge’s seed data with a fixed random seed: real item codes, suppliers and contract rates. The stock figures are drawn at random on purpose.</p>
    <p class="step small">The policies are copied line by line from Northbridge’s documents. Click a kind to read a real one.</p>
  </div>
  <div class="fig" data-fig="corpusmix" style="left:540px;top:130px;width:960px;height:660px"></div>
  ''' + hidden(5) + '''
  <div class="cap" style="left:540px;top:806px;width:960px"><code>ledgerline/ledgerline/course/l2/northbridge_corpus.md</code>, made by <code>course/l2/corpus.py</code>. Counted by <code>gen_v5data.py</code>.</div>
</section>''')
add('''<section class="slide" data-plate="How the Training Data Is Made">
  <div class="lec-top"><h2>How the training data is made</h2><p class="sub">Nobody labels anything. The text is its own answer key: every next character.</p></div>
  <div class="fig" data-fig="windows" style="left:100px;top:240px;width:1400px;height:600px"></div>
  ''' + hidden(2) + '''
</section>''')
add(old(52)); add(old(53)); add(old(54)); add(old(55))
add(sq("Section 8", "How could a machine set 830,464 numbers <em>by itself?</em>"))
add(retitle(old(59), "Film · 8 · Training", "Film · 8 · How the weights were learnt: training"))
add(check("Film 8", [
    ("Why does the tiny GPT’s loss start near 4.39?", "It guesses evenly over 81 characters, and −ln(1/81) = 4.39."),
    ("How is one training example made?", "Cut 128 characters at a random place. The target is the same text, one character later: 128 guesses."),
    ("5,400 was in its training text. Did it learn the stock?", "No. It learnt what a stock line looks like. In 10 tries it never wrote 5,400."),
]))

# ---------------- the whole machine ----------------
add('''<section class="slide part" data-plain="1">
  <div class="center"><span class="num">Putting it together</span>
    <div class="recall"><b>Eight sections</b>Tokens, vectors, attention, blocks and heads, logits, generation, training. Now: all of it at once.</div>
    <h1 class="q2">The whole machine</h1></div>
</section>''')
add(sq("The whole machine", "Can you say, in order, <em>everything that happened</em> to Emma’s question?"))
add(retitle(old(67), "Film · The whole machine", "Film · The whole machine"))
add(check("the whole machine", [
    ("Put these in order: softmax · tokens · the loop · 24 blocks · embedding lookup · one token chosen.", "Tokens → embedding lookup → 24 blocks (attention and MLP) → logits and softmax → one token chosen → the loop."),
    ("At which step could Northbridge’s real stock have got in?", "Only through the input: the context. The weights were frozen in 2024, and the input held no stock line."),
]))
rec = old(68).replace('<li class="step"><span class="n">5</span><span><b>24 blocks.</b> Look, then think, 24 times; the answer formed near the top.</span></li>',
                      '<li class="step"><span class="n">5</span><span><b>24 blocks, 14 heads.</b> Every block changed all 100 vectors; the last one became the answer.</span></li>')
rec = rec.replace('<li class="step"><span class="n">6</span><span><b>A choice.</b>', '<li class="step"><span class="n">6</span><span><b>Logits and softmax.</b>')
rec = rec.replace('<li class="step"><span class="n">7</span><span><b>The loop.</b>', '<li class="step"><span class="n">7</span><span><b>Generation.</b>')
rec = rec.replace('<li class="step"><span class="n">9</span><span><b>The fix.</b> Nothing carried the stock, so it wrote a likely one. Facts in the context fix it.</span></li>',
                  '<li class="step"><span class="n">9</span><span><b>And still: 100.</b> Every step worked as designed. Ledgerline says 5,400. Why?</span></li>')
add(rec)

# ---------------- 9 · the fix ----------------
add(part(9, "Section 9 of 9 · The fix", "Why did it make the number up, and what fixes it?",
         "The whole machine worked, every step as designed, and still said 100. Now: back to Monday morning."))
add(old(61)); add(old(62)); add(old(63))
add(sq("Section 9", "Why did it make the number up, and <em>what fixes it?</em>"))
add(retitle(old(65), "Film · 9 · Why it made it up", "Film · 9 · Why it made it up, and the fix"))
add(check("Film 9", [
    ("When the model wrote the “1”, which digits were in its context?", "Only the date’s: 26 October 2026. Nothing carried the stock."),
    ("With the stock line added, where did block 10, head 13 look as it wrote the “5”?", "77% of its weight on the five tokens of “5,400” in the fact line."),
    ("Name the two ways we will put facts into the context.", "Knowledge: find the right text and add it (Lecture 3). Tools: let the model ask Ledgerline itself (Lecture 4)."),
]))

# ---------------- hands-on: the Brain Lab ----------------
add('''<section class="slide part" data-plain="1">
  <div class="center"><span class="num">Hands-on · 15 minutes</span>
    <div class="recall"><b>Two ways in</b>A fact can go into the weights (training) or into the context (the prompt). Which is better? Try both.</div>
    <h1 class="q2">The Brain Lab: learn it, or give it?</h1></div>
</section>''')
add(old(56)); add(old(57))

# ---------------- what is next, NB2, A2 ----------------
add(old(69)); add(old(71))
add('''<section class="slide part" data-plain="1">
  <div class="center"><span class="num">Your assignment</span>
    <div class="recall"><b>Due before Lecture 3</b>Sat 7 Nov, 7 AM IST. On your own work or domain.</div>
    <h1 class="q2">A2 · How a brain would read your work</h1></div>
</section>''')
add(old(72))

c59 = ['MY_TEXT = """Paste a page of your own documents here. For example: Leave requests above five days need the line',
       'manager\'s approval in HRMS before the leave starts. Carry-forward is capped at 12 days on 31 March."""',
       'if LIVE:',
       '    my_ids = tok(MY_TEXT, add_special_tokens=False).input_ids',
       '    words_ = MY_TEXT.split()',
       '    split = sorted({w for w in words_ if len(tok(" " + w.strip(".,;:()"), add_special_tokens=False).input_ids) >= 3})',
       '    p_in, p_out = PRICES["gemini-3.8-flash"]',
       '    print(f"{len(MY_TEXT)} characters, {len(words_)} words -> {len(my_ids)} Qwen tokens ({len(MY_TEXT) / len(my_ids):.1f} characters a token)")',
       '    print("words cut into 3 or more tokens:", split)',
       '    print(f"sending it as input once: about ${len(my_ids) * p_in / 1e6:.6f} (Gemini counts its own tokens, so this is an estimate)")']
add(f'''<section class="slide" data-plate="A2 · Part 1 · Tokens">
  <div class="lec-top"><h2>Part 1 · Cut your own text</h2><p class="sub">NB2’s last cell, “Your own documents”. 2 points.</p></div>
  <div class="nbcell" style="left:100px;top:230px;width:930px"><span class="hd">NB2 · last cell</span>{code(c59, hl=(1, 2, 8, 9, 10))}</div>
  <div class="callout step" style="left:1060px;top:230px;width:440px"><b>1 · Paste</b> one or two pages of your own text here. Nothing confidential.</div>
  <div class="callout step" style="left:1060px;top:360px;width:440px"><b>2 · Report</b> characters, words, tokens and characters per token. Compare with Northbridge’s manual (NB2 section 2).</div>
  <div class="callout step" style="left:1060px;top:510px;width:440px"><b>3 · The split words.</b> List the ten that split most and group them: names, codes, numbers, other languages, jargon.</div>
  <div class="callout step" style="left:1060px;top:660px;width:440px"><b>4 · The cost.</b> One realistic question, then 1,000 a day for a year, thinking included (exercise 3).</div>
</section>''')

c1 = ['# os.environ["GEMINI_API_KEY"] = "..."        # optional: your own key, to run live',
      '# os.environ["OPENROUTER_API_KEY"] = "..."    # optional: GPT, Claude, Llama ... via OpenRouter']
c53 = ['for i in range(1, 9):',
       '    r = BrainOnly(f"L2v4_coldopen_r{i}").respond(QUESTION)',
       '    print(f"run {i}: {r[\'reply\'][:150]!r}")']
mine = ['MY_SYSTEM = "You are the assistant for <your team>. Today is <date>."',
        'MY_Q = "<a question people in your domain really ask>"',
        'for i in range(1, 5):                                  # four new chats',
        '    r = BrainOnly(f"my_q1_run{i}", system=MY_SYSTEM, temperature=1.0).respond(MY_Q)',
        '    print(r["reply"])']
add(f'''<section class="slide" data-plate="A2 · Part 2 · Where It Invents">
  <div class="lec-top"><h2>Part 2 · Ask a brain alone, four times</h2><p class="sub">Your own three questions. 3 points.</p></div>
  <div class="nbcell" style="left:100px;top:220px;width:900px"><span class="hd">NB2 · setup cell (add your key to run live)</span>{code(c1, hl=(1,))}</div>
  <div class="nbcell" style="left:100px;top:345px;width:900px"><span class="hd">NB2 · section 9 · the cold open, replayed</span>{code(c53, hl=(2,))}</div>
  <div class="nbcell step" style="left:100px;top:510px;width:900px"><span class="hd">Your version · same code, your prompt</span>{code(mine, hl=(1, 2, 4))}</div>
  <div class="callout step" style="left:1030px;top:220px;width:470px"><b>1 · Three questions</b> people really ask: one needs a fact that changes daily, one needs a written rule.</div>
  <div class="callout step" style="left:1030px;top:380px;width:470px"><b>2 · Paste</b> the exact prompt and all four replies. Or use any chat app with search and file upload off.</div>
  <div class="callout step" style="left:1030px;top:540px;width:470px"><b>3 · Trace</b> one invented detail through today’s steps: input, next-token game, training, cut-off. 200–300 words, at least five of today’s terms.</div>
  <div class="callout step" style="left:1030px;top:720px;width:470px"><b>4 · The dangerous one:</b> who would act on a confident wrong answer, and when would anyone notice?</div>
</section>''')

c55 = ['print("the fact line:", brain.FACT)',
       'SOLUTION = True',
       'if SOLUTION:',
       '    system_with_fact = SYSTEM_BRAIN + "\\n" + brain.FACT',
       '    rf = BrainOnly("L2v4_facts_r1", system=system_with_fact).respond(QUESTION)',
       '    print("Ask Northbridge with the fact:", rf["reply"])']
add(f'''<section class="slide" data-plate="A2 · Part 3 · The Facts It Needs">
  <div class="lec-top"><h2>Part 3 · Put the fact in the prompt</h2><p class="sub">NB2 exercise 6 does it for the stock line. You do it for your question. 3 points.</p></div>
  <div class="nbcell" style="left:100px;top:240px;width:900px"><span class="hd">NB2 · section 9 · exercise 6</span>{code(c55, hl=(4, 5))}</div>
  <div class="callout step" style="left:1030px;top:240px;width:470px"><b>1 · List the facts</b> each question needs, and where each lives today: a system, a document, a spreadsheet, one person’s memory.</div>
  <div class="callout step" style="left:1030px;top:420px;width:470px"><b>2 · Sort them:</b> slow-changing documents (Lecture 3, knowledge) or live lookups (Lecture 4, tools). Give a reason each.</div>
  <div class="callout step" style="left:1030px;top:600px;width:470px"><b>3 · Test it:</b> add one fact to the system prompt, ask again, paste the reply. Did it use the fact? Did it add anything you did not give it?</div>
  <div class="opens step" style="top:560px;left:100px;width:900px;right:auto;background:var(--g1)"><span class="k" style="color:var(--after)">Next week</span>Part 3 becomes your problem statement for Lecture 3.</div>
</section>''')

c9 = ['top5 = NEXT["logits60"][:5]', 'print(top5)', 'SOLUTION = True',
      'if SOLUTION:', '    z = np.array([l for _, l in top5])',
      '    probs = np.exp(z - z.max()) / np.exp(z - z.max()).sum()   # subtract the max first: same result, no overflow',
      '    for (t, _), p in zip(top5, probs):', '        print(f"{t!r:12} {p:.3f}")']
add(f'''<section class="slide" data-plate="A2 · Part 4 · Run NB2">
  <div class="lec-top"><h2>Part 4 · Run NB2, solve three exercises</h2><p class="sub">Colab, free CPU, no key: every model call is replayed. 2 points.</p></div>
  <div class="nbcell" style="left:100px;top:230px;width:860px"><span class="hd">NB2 · section 1 · exercise 1: softmax by hand</span>{code(c9, hl=(3,))}</div>
  <div class="callout step" style="left:100px;top:530px;width:860px"><b>Set <code>SOLUTION = False</code></b> and write the solution yourself, in at least three of the six exercises.</div>
  <ol class="legend" style="position:absolute;left:1000px;top:230px;width:500px;font-size:19px">
    <li><span class="n">1</span><span>Softmax by hand (section 1)</span></li>
    <li><span class="n">2</span><span>One BPE merge (section 2)</span></li>
    <li><span class="n">3</span><span>The price of a question, thinking included (section 2)</span></li>
    <li><span class="n">4</span><span>One attention row by hand (section 4)</span></li>
    <li><span class="n">5</span><span>The loss before training (section 8)</span></li>
    <li><span class="n">6</span><span>Put the fact in the prompt (section 9)</span></li>
  </ol>
  <div class="card af step" style="position:absolute;left:1000px;top:560px;width:500px;font-size:18px"><span class="tag af">Answer in 2–3 sentences</span><br>1. At which block does the answer first appear at the last position? What does that say about where it is made?<br>2. Why is “learnt it in training” the wrong way to know today’s stock?</div>
</section>''')
add(old(73))

deck = head + '<div class="deck" id="deck">\n\n' + "\n\n".join(N) + "\n\n</div>\n<script src=\"figdata.js\">" + tail
deck = deck.replace('<script src="figs.js"></script>', '<script src="figs.js"></script>\n<script src="v5data.js"></script>\n<script src="figs_v5.js"></script>')
out = HERE / "index.html"
out.write_text(deck)
print("slides:", len(N))
