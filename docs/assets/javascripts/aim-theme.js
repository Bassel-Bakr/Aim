/* Aim colour theme.
 *
 * A reader picks one colour; this file derives the site's colour tokens for both schemes from it
 * and writes them over the stylesheet's defaults. With nothing picked it writes nothing, so the
 * stylesheet stays the default palette. See specs/2026-09-13-theme-picker-design.md.
 *
 * Three parts, in order: colour maths, derivation, and wiring. The first two are pure and load in
 * Node for tests; wiring runs only where there is a document. */
(function (global) {
  "use strict";

  /* -------------------------------------------------------------------------------------------
   * Colour maths: sRGB, OKLCH, contrast, gamut
   * ---------------------------------------------------------------------------------------- */

  function parseHex(hex) {
    var match = /^#?([0-9a-f]{6})$/i.exec(String(hex).trim());
    if (!match) return null;
    var n = parseInt(match[1], 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255].map(function (v) { return v / 255; });
  }

  function byteHex(v) {
    var byte = Math.round(Math.min(1, Math.max(0, v)) * 255);
    return (byte < 16 ? "0" : "") + byte.toString(16);
  }

  /* A six-digit hex string, or eight digits when an alpha is given. */
  function toHex(rgb, alpha) {
    return "#" + rgb.map(byteHex).join("") + (alpha === undefined ? "" : byteHex(alpha));
  }

  function toLinear(v) { return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function fromLinear(v) { return v <= 0.0031308 ? v * 12.92 : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; }

  function rgbToOklch(rgb) {
    var r = toLinear(rgb[0]), g = toLinear(rgb[1]), b = toLinear(rgb[2]);
    var l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
    var m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
    var s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
    var L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
    var A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
    var B = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
    return { l: L, c: Math.hypot(A, B), h: (Math.atan2(B, A) * 180 / Math.PI + 360) % 360 };
  }

  /* Linear sRGB for an OKLCH colour, unclamped, so the caller can tell whether it is in gamut. */
  function oklchToLinear(L, C, H) {
    var rad = H * Math.PI / 180, A = C * Math.cos(rad), B = C * Math.sin(rad);
    var l = Math.pow(L + 0.3963377774 * A + 0.2158037573 * B, 3);
    var m = Math.pow(L - 0.1055613458 * A - 0.0638541728 * B, 3);
    var s = Math.pow(L - 0.0894841775 * A - 1.291485548 * B, 3);
    return [
      4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
      -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
      -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s
    ];
  }

  function inGamut(lin) {
    return lin.every(function (v) { return v >= -1e-4 && v <= 1 + 1e-4; });
  }

  /* An sRGB colour at this lightness and hue, with chroma reduced until it fits the gamut. */
  function fit(L, C, H) {
    L = Math.min(1, Math.max(0, L));
    var lin = oklchToLinear(L, C, H);
    if (!inGamut(lin)) {
      var lo = 0, hi = C;
      for (var i = 0; i < 24; i++) {
        var mid = (lo + hi) / 2;
        if (inGamut(oklchToLinear(L, mid, H))) lo = mid; else hi = mid;
      }
      lin = oklchToLinear(L, lo, H);
    }
    return lin.map(function (v) { return fromLinear(Math.min(1, Math.max(0, v))); });
  }

  function luminance(rgb) {
    return 0.2126 * toLinear(rgb[0]) + 0.7152 * toLinear(rgb[1]) + 0.0722 * toLinear(rgb[2]);
  }

  function contrast(a, b) {
    var x = luminance(a), y = luminance(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  }

  /* -------------------------------------------------------------------------------------------
   * Derivation
   * ---------------------------------------------------------------------------------------- */

  var DEFAULT_SEED = "#9c3522";
  var TEXT_CONTRAST = 4.5;
  /* Today's accent and NOTE sit about 50 degrees apart in OKLCH hue: 51.8 light, 49.5 dark. */
  var KEY_HUE_OFFSET = 50;
  var WHITE = [1, 1, 1];
  var NIGHT_FG = parseHex("#e8eaf0");

  var PRESETS = [
    { name: "Brick", seed: "#9c3522" },
    { name: "Teal", seed: "#1f7a78" },
    { name: "Forest", seed: "#3f7a3a" },
    { name: "Cobalt", seed: "#2f5fb3" },
    { name: "Violet", seed: "#6f4bb0" },
    { name: "Rose", seed: "#b0406e" },
    { name: "Amber", seed: "#a8680f" },
    { name: "Slate", seed: "#4f6272" }
  ];

  function isDefault(seed) {
    return typeof seed === "string" && seed.trim().toLowerCase() === DEFAULT_SEED;
  }

  /* The first colour from a starting lightness, stepping 0.01 in one direction, that reaches
   * 4.5:1 against every background. When lightness runs out, chroma halves and the walk restarts;
   * null when even a near-grey cannot pass. */
  function guard(L, C, H, backgrounds, step) {
    for (var chroma = C; chroma >= 0.004; chroma /= 2) {
      for (var l = L; l >= 0 && l <= 1; l += step) {
        var rgb = fit(l, chroma, H);
        var passes = backgrounds.every(function (bg) { return contrast(rgb, bg) >= TEXT_CONTRAST; });
        if (passes) return rgb;
      }
    }
    return null;
  }

  /* The ink with more contrast on a solid tag colour, or null if neither reaches 4.5:1. */
  function tagInk(tag, night) {
    var best = contrast(night, tag) >= contrast(NIGHT_FG, tag) ? night : NIGHT_FG;
    return contrast(best, tag) >= TEXT_CONTRAST ? best : null;
  }

  /* Token values for both schemes, or null when the seed cannot produce a readable palette. */
  function derive(seed) {
    var rgb = parseHex(seed);
    if (!rgb) return null;
    var base = rgbToOklch(rgb), h = base.h, c = base.c, keyH = (h + KEY_HUE_OFFSET) % 360;

    var chrome = fit(0.915, 0.012, h);
    var lAccent = guard(0.48, Math.min(c, 0.14), h, [WHITE, chrome], -0.01);
    var lHeading = guard(0.38, Math.min(c, 0.12), h, [WHITE], -0.01);
    var lKey = fit(0.76, 0.15, keyH);
    var lKeyInk = guard(0.45, 0.1, keyH, [WHITE], -0.01);

    var page = fit(0.15, 0.008, h);
    var night = fit(0.16, 0.008, h);
    var dAccent = guard(0.71, Math.min(c, 0.13), h, [page, night], 0.01);
    var dHeading = guard(0.8, Math.min(c, 0.1), h, [page], 0.01);
    var dKey = fit(0.82, 0.13, keyH);
    var dKeyInk = guard(0.82, 0.13, keyH, [page], 0.01);

    if (!lAccent || !lHeading || !lKeyInk || !dAccent || !dHeading || !dKeyInk) return null;
    var lTag = tagInk(lAccent, night), lKeyTag = tagInk(lKey, night);
    var dTag = tagInk(dAccent, night), dKeyTag = tagInk(dKey, night);
    if (!lTag || !lKeyTag || !dTag || !dKeyTag) return null;

    return {
      light: {
        "--aim-accent": toHex(lAccent),
        "--aim-heading": toHex(lHeading),
        "--aim-myth-wash": toHex(lAccent, 0.06),
        "--md-accent-fg-color--transparent": toHex(lAccent, 0.08),
        "--aim-chrome": toHex(chrome),
        "--aim-key": toHex(lKey),
        "--aim-key-ink": toHex(lKeyInk),
        "--aim-key-wash": toHex(lKey, 0.12),
        "--aim-tag-ink": toHex(lTag),
        "--aim-key-tag-ink": toHex(lKeyTag)
      },
      dark: {
        "--aim-accent": toHex(dAccent),
        "--aim-heading": toHex(dHeading),
        "--aim-myth-wash": toHex(dAccent, 0.08),
        "--md-accent-fg-color--transparent": toHex(dAccent, 0.12),
        "--md-default-bg-color": toHex(page),
        "--aim-night": toHex(night),
        "--aim-night-accent": toHex(dAccent),
        "--aim-key": toHex(dKey),
        "--aim-key-ink": toHex(dKeyInk),
        "--aim-key-wash": toHex(dKey, 0.08),
        "--aim-tag-ink": toHex(dTag),
        "--aim-key-tag-ink": toHex(dKeyTag),
        // aim.css sets these at :root from night and the accent, and var() resolves there, before
        // the scheme block, so they are written again here or they keep the default night.
        "--aim-chrome": toHex(night),
        "--aim-chrome-accent": toHex(dAccent),
        "--aim-chrome-on-accent": toHex(dTag),
        "--aim-chrome-on-hover": toHex(night)
      }
    };
  }

  var SCHEMES = {
    light: '[data-md-color-scheme="default"][data-md-color-primary]',
    dark: '[data-md-color-scheme="slate"][data-md-color-primary]'
  };

  /* The derived tokens as a stylesheet: one block per scheme, on the selectors aim.css uses. */
  function toCss(tokens) {
    return Object.keys(SCHEMES).map(function (scheme) {
      var lines = Object.keys(tokens[scheme]).map(function (name) {
        return "  " + name + ": " + tokens[scheme][name] + ";";
      });
      return SCHEMES[scheme] + " {\n" + lines.join("\n") + "\n}";
    }).join("\n");
  }

  var api = global.aimTheme = {
    PRESETS: PRESETS,
    DEFAULT_SEED: DEFAULT_SEED,
    derive: derive,
    isDefault: isDefault,
    toCss: toCss,
    /* Exposed for tests: contrast between two six-digit hex colours, and an in-gamut hex colour
     * for an OKLCH lightness, chroma and hue. */
    contrast: function (a, b) { return contrast(parseHex(a), parseHex(b)); },
    oklchHex: function (L, C, H) { return toHex(fit(L, C, H)); }
  };

  if (typeof document === "undefined") return;

  /* -------------------------------------------------------------------------------------------
   * Wiring: storage, painting, and the picker
   * ---------------------------------------------------------------------------------------- */

  var STORAGE_KEY = "aim.theme.seed";
  var STYLE_ID = "aim-theme";

  /* The saved seed, lower-cased, or null. Storage can throw in private windows or when a browser
   * blocks site data; that reads as nothing saved. A malformed value is removed. */
  function readSeed() {
    try {
      var seed = localStorage.getItem(STORAGE_KEY);
      if (seed === null) return null;
      if (parseHex(seed)) return seed.trim().toLowerCase();
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) { /* storage unavailable */ }
    return null;
  }

  function writeSeed(seed) {
    try {
      if (seed === null) localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, seed);
    } catch (error) { /* storage unavailable: the choice lasts until the page is left */ }
  }

  /* Write the tokens into one <style> at the end of <head>, or remove it for the default. */
  function paint(tokens) {
    var style = document.getElementById(STYLE_ID);
    if (!tokens) {
      if (style) style.parentNode.removeChild(style);
      return;
    }
    if (!style) {
      style = document.createElement("style");
      style.id = STYLE_ID;
      document.head.appendChild(style);
    }
    style.textContent = toCss(tokens);
  }

  var active = DEFAULT_SEED;
  var listeners = [];

  function notify() {
    listeners.forEach(function (listener) { listener(active); });
  }

  /* Re-colour the site from a seed and remember it. Brick is the default, so it clears instead.
   * Returns false, changing nothing, when the seed cannot produce a readable palette. */
  function apply(seed) {
    if (isDefault(seed)) {
      reset();
      return true;
    }
    var tokens = derive(seed);
    if (!tokens) return false;
    active = seed.trim().toLowerCase();
    paint(tokens);
    writeSeed(active);
    notify();
    return true;
  }

  function reset() {
    active = DEFAULT_SEED;
    paint(null);
    writeSeed(null);
    notify();
  }

  api.apply = apply;
  api.reset = reset;

  // Runs in <head>, before the body is parsed, so a saved colour is in place before first paint.
  var saved = readSeed();
  if (saved && !isDefault(saved)) {
    var tokens = derive(saved);
    if (tokens) {
      active = saved;
      paint(tokens);
    } else {
      writeSeed(null);
    }
  }

  function element(tag, attributes, children) {
    var node = document.createElement(tag);
    Object.keys(attributes || {}).forEach(function (name) { node.setAttribute(name, attributes[name]); });
    (children || []).forEach(function (child) {
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function buildPicker(anchor) {
    var button = element("button", {
      type: "button",
      class: "md-header__button md-icon aim-theme-picker__button",
      "aria-label": "Change colour",
      "aria-haspopup": "dialog",
      "aria-expanded": "false",
      "aria-controls": "aim-theme-panel"
    }, [element("span", { class: "aim-theme-picker__dot", "aria-hidden": "true" })]);

    var swatches = PRESETS.map(function (preset) {
      return element("button", {
        type: "button",
        role: "radio",
        class: "aim-theme-picker__swatch",
        style: "--aim-swatch: " + preset.seed,
        "aria-label": preset.name,
        title: preset.name,
        "data-seed": preset.seed
      });
    });
    var group = element("div", {
      role: "radiogroup",
      "aria-label": "Preset colours",
      class: "aim-theme-picker__swatches"
    }, swatches);

    var custom = element("input", { type: "color", class: "aim-theme-picker__input" });
    var customLabel = element("label", { class: "aim-theme-picker__custom" }, ["Custom…", custom]);
    var message = element("p", { class: "aim-theme-picker__message", role: "status", hidden: "" });
    var resetButton = element("button", { type: "button", class: "aim-theme-picker__reset" }, ["Reset"]);

    var panel = element("div", {
      id: "aim-theme-panel",
      class: "aim-theme-picker__panel",
      role: "dialog",
      "aria-label": "Site colour",
      hidden: ""
    }, [group, customLabel, message, resetButton]);

    var wrapper = element("div", { class: "md-header__option aim-theme-picker" }, [button, panel]);
    anchor.parentNode.insertBefore(wrapper, anchor.nextSibling);

    function sync(seed) {
      var preset = null;
      swatches.forEach(function (swatch) {
        var checked = swatch.getAttribute("data-seed") === seed;
        if (checked) preset = swatch;
        swatch.setAttribute("aria-checked", String(checked));
        swatch.tabIndex = -1;
      });
      (preset || swatches[0]).tabIndex = 0;
      customLabel.toggleAttribute("data-active", !preset);
      custom.value = seed;
    }

    function open() {
      panel.hidden = false;
      button.setAttribute("aria-expanded", "true");
      var checked = swatches.filter(function (swatch) { return swatch.tabIndex === 0; })[0];
      checked.focus();
    }

    function close(returnFocus) {
      panel.hidden = true;
      message.hidden = true;
      button.setAttribute("aria-expanded", "false");
      if (returnFocus) button.focus();
    }

    function choose(seed) {
      message.hidden = true;
      if (!apply(seed)) {
        message.textContent = "That colour can't be made readable. Try a different one.";
        message.hidden = false;
      }
    }

    button.addEventListener("click", function () {
      if (panel.hidden) open(); else close(false);
    });

    swatches.forEach(function (swatch, index) {
      swatch.addEventListener("click", function () { choose(swatch.getAttribute("data-seed")); });
      swatch.addEventListener("keydown", function (event) {
        var step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
        if (!step) return;
        event.preventDefault();
        var next = swatches[(index + step + swatches.length) % swatches.length];
        next.focus();
        choose(next.getAttribute("data-seed"));
      });
    });

    custom.addEventListener("input", function () { choose(custom.value); });
    resetButton.addEventListener("click", function () {
      message.hidden = true;
      reset();
    });

    panel.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        event.preventDefault();
        close(true);
      }
    });

    document.addEventListener("click", function (event) {
      if (!panel.hidden && !wrapper.contains(event.target)) close(false);
    });

    listeners.push(sync);
    sync(active);
  }

  document.addEventListener("DOMContentLoaded", function () {
    // The light/dark toggle's form. If a theme upgrade renames it, there is simply no picker.
    var anchor = document.querySelector('.md-header__option[data-md-component="palette"]');
    if (anchor) buildPicker(anchor);
  });
})(typeof globalThis !== "undefined" ? globalThis : this);
