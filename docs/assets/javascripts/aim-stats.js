/* Aim stats count-up.
 *
 * The aim_stats extension writes the landing page's counts into <ul class="aim-stats"> as plain
 * numbers. This file counts each one up from 0 the first time the row scrolls into view. The real
 * numbers stay in the HTML, so a reader without JavaScript, or one who asks for reduced motion,
 * sees them straight away. */
(function () {
  "use strict";

  var DURATION = 1200;

  var row = document.querySelector(".aim-stats");
  if (!row || !("IntersectionObserver" in window)) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var counts = Array.prototype.map.call(row.querySelectorAll(".aim-stats__count"), function (el) {
    return { el: el, target: parseInt(el.textContent, 10) };
  }).filter(function (count) { return count.target > 0; });

  counts.forEach(function (count) { count.el.textContent = "0"; });

  function show(eased) {
    counts.forEach(function (count) {
      count.el.textContent = String(Math.round(count.target * eased));
    });
  }

  function animate() {
    var start = null;
    var done = false;
    function frame(now) {
      if (done) return;
      /* Timed from the first frame drawn, so a tab opened in the background still counts up. */
      if (start === null) start = now;
      var progress = Math.min(1, (now - start) / DURATION);
      /* Ease out, so the count slows as it lands on the number. */
      show(1 - Math.pow(1 - progress, 3));
      if (progress < 1) requestAnimationFrame(frame);
      else done = true;
    }
    requestAnimationFrame(frame);
    /* Frames can stop, in a hidden tab or a headless renderer; never leave a count short of its
     * number because of that. */
    setTimeout(function () {
      if (start === null || done) return;
      done = true;
      show(1);
    }, DURATION + 500);
  }

  var observer = new IntersectionObserver(function (entries) {
    if (!entries.some(function (entry) { return entry.isIntersecting; })) return;
    observer.disconnect();
    animate();
  });
  observer.observe(row);
})();
