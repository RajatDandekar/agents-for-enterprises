/* Registers the 3D "How it works" figure with the plate engine: FIGS.flow3d, mounted on [data-fig="flow3d"].
   Load after flow3d/trace.js and before ../../engine/plates.js. Needs the three.js import map in <head> (see README.md).
   Each deck step k shows stage k; entering the slide jumps to the stage's end state, a forward step plays it. */
(function () {
  window.FIGS = window.FIGS || {};
  var base = document.currentScript.src.replace(/deck\.js(\?.*)?$/, '');
  function poster(el) {
    el.innerHTML = '<img src="' + base + 'poster.png" alt="How a request flows through Ask Northbridge" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">';
  }
  window.FIGS.flow3d = function (el) {
    var api = null, want = [0, true];
    if (document.body.classList.contains('print')) { poster(el); return { step: function () {} }; }
    import(base + 'flow3d.js').then(function (m) {
      api = m.mountFlow3D(el, { trace: window.FLOW3D_TRACE, mode: 'deck' });
      api.go(want[0], want[1]);
    }).catch(function (e) { console.error('flow3d', e); poster(el); });
    return { step: function (k, instant) { want = [k, instant]; if (api) api.go(k, instant); } };
  };
})();
