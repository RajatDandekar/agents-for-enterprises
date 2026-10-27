// Paste-able deck QA: reveal every step of every slide, then report elements outside the frame,
// overflowing boxes and tiny text. Run in the page: await window.__deckQA()
window.__deckQA = async () => {
  const deck = document.getElementById('deck');
  const slides = [...deck.querySelectorAll('.slide')];
  const out = [];
  for (let i = 0; i < slides.length; i++) {
    deckApi.show(i, true);
    await new Promise((r) => setTimeout(r, 120));
    const s = slides[i], sr = s.getBoundingClientRect(), sc = sr.width / 1600;
    const lim = { l: sr.left + 20 * sc, r: sr.right - 20 * sc, t: sr.top + 20 * sc, b: sr.bottom - 20 * sc };
    const issues = [];
    s.querySelectorAll('*').forEach((e) => {
      if (e.closest('.frame') || e.classList.contains('folio') || e.classList.contains('plate-head')) return;
      const cs = getComputedStyle(e);
      if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) return;
      const r = e.getBoundingClientRect();
      if (!r.width || !r.height) return;
      const out_ = r.left < lim.l - 2 || r.right > lim.r + 2 || r.top < lim.t - 2 || r.bottom > lim.b + 2;
      const own = [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      if (out_ && (own || e.tagName === 'svg' || e.tagName === 'IMG')) issues.push(`OUT ${e.tagName}.${e.className && e.className.baseVal === undefined ? e.className : ''} "${(e.textContent || '').trim().slice(0, 40)}"`);
      if (['DIV', 'PRE', 'P', 'TD'].includes(e.tagName) && e.scrollHeight > e.clientHeight + 4 && cs.overflow !== 'visible' && cs.overflowY !== 'visible') issues.push(`CLIP ${e.tagName}.${e.className} "${(e.textContent || '').trim().slice(0, 40)}"`);
      if (e.tagName === 'text' && e.ownerSVGElement && getComputedStyle(e.ownerSVGElement).overflow !== 'visible') {
        const sv = e.ownerSVGElement.getBoundingClientRect();
        if (r.left < sv.left - 1 || r.right > sv.right + 1 || r.top < sv.top - 1 || r.bottom > sv.bottom + 1) issues.push(`SVGCUT "${e.textContent.trim().slice(0, 40)}"`);
      }
      if (own && parseFloat(cs.fontSize) < 12 && !e.closest('.win') ) issues.push(`TINY ${cs.fontSize} "${e.textContent.trim().slice(0, 30)}"`);
    });
    if (issues.length) out.push({ slide: i + 1, plate: s.dataset.plate || '', issues: [...new Set(issues)].slice(0, 8) });
  }
  deckApi.show(0);
  return out;
};
