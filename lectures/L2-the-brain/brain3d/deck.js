/* Registers the Lecture 2 3D scene with the plate engine: FIGS.brain3d, mounted on [data-fig="brain3d"][data-section="N"].
   Load after brain3d/trace.js and before ../../engine/plates.js. Needs the three.js import map in <head> (see README.md).
   One scene serves the whole lecture: every brain3d figure shares one renderer, which moves into the slide being shown,
   so the camera flies on from the previous section. After k deck steps the figure shows step k of its section;
   entering the slide shows that step's end state, a forward step plays it. */
(function () {
  window.FIGS = window.FIGS || {};
  var base = document.currentScript.src.replace(/deck\.js(\?.*)?$/, '');
  var shared = null, loading = null;
  function poster(el, s) {
    el.innerHTML = '<img src="' + base + 'poster-s' + s + '.png" alt="The Brain, section ' + s + '" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">';
  }
  function get(el, s) {
    if (shared) return Promise.resolve(shared);
    if (!loading) loading = import(base + 'brain3d.js').then(function (m) {
      shared = m.mountBrain3D(el, { trace: window.BRAIN_TRACE, mode: 'deck', section: s });
      window.brain3d = shared;
      return shared;
    });
    return loading;
  }
  window.FIGS.brain3d = function (el) {
    var s = Math.max(1, Math.min(9, parseInt(el.dataset.section || '1', 10)));
    if (document.body.classList.contains('print')) { poster(el, s); return { step: function () {} }; }
    var want = null;
    return {
      step: function (k, instant) {
        want = [k, instant];
        get(el, s).then(function (b) {
          if (!want) return;
          b.attach(el);
          if (b.section !== s) b.setSection(s, want[0], true); else b.go(want[0], want[1]);
        }).catch(function (e) { console.error('brain3d', e); poster(el, s); });
      },
    };
  };
})();
