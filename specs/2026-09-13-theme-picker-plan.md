# Theme Picker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a reader pick one colour in the header and re-colour the whole site from it, in both
schemes, while the site looks exactly as it does today until they do.

**Architecture:** One classic script, `docs/assets/javascripts/aim-theme.js`, loaded blocking from
`<head>` through a `main.html` template override. It derives both schemes' colour tokens from a seed
in OKLCH, with contrast guards, and writes them into one `<style>` after `aim.css`; with no saved
seed it writes nothing. The same file builds the header picker. The derivation is pure and tested
in Node with `node:test`.

**Tech Stack:** Zensical (Material theme) with `custom_dir` overrides; vanilla ES5-style JavaScript
with no build step and no dependencies; Node 22+ `node:test` and `node:vm` for tests.

**Spec:** `specs/2026-09-13-theme-picker-design.md`

## Global Constraints

- With no saved seed, or with Brick (`#9c3522`) chosen, the script injects nothing: the default site
  is exactly the colours `aim.css` defines.
- Every text colour the derivation produces reaches 4.5:1 against the backgrounds in the spec's
  Guards table, in both schemes.
- Category colours (`--aim-clicking`, `--aim-tracking`, `--aim-switching`) and neutral ink are never
  derived.
- The injected `<style>` uses exactly the scheme selectors `aim.css` uses:
  `[data-md-color-scheme="default"][data-md-color-primary]` and
  `[data-md-color-scheme="slate"][data-md-color-primary]`.
- Storage key: `aim.theme.seed`. Every storage access is wrapped in try/catch.
- No build step, no npm dependency, no copied theme partial.
- `zensical build` is not run with `--strict`: read its output rather than trusting the exit code.
- The shell's `grep` in this repository is wrapped by a proxy that has returned whole files; use
  Python to count or locate text.
- Activate the virtualenv before Python or Zensical: `source .venv/Scripts/activate` in bash.

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `docs/assets/javascripts/aim-theme.js` | Colour maths and derivation (Task 1); storage, painting and early paint (Task 2); the picker (Task 3) | 1, 2, 3 |
| `scripts/aim-theme.test.mjs` | Node tests for the derivation | 1 |
| `overrides/main.html` | Loads the script in `<head>` | 2 |
| `zensical.toml` | `custom_dir = "overrides"` | 2 |
| `docs/assets/stylesheets/aim.css` | Picker styles and header component list | 3 |
| `.github/workflows/check.yml` | Runs the Node tests in CI | 4 |
| `AGENTS.md` | Layout rows and the token note | 4 |
| `specs/2026-09-13-theme-picker-design.md` | Test command correction | 4 |

## Correction to the spec

The spec gives the test command as `node --test scripts/`. Node 24 does not accept a directory for
`--test` and fails with `Cannot find module 'D:\Projects\aim\scripts'`. This plan runs
`node --test scripts/aim-theme.test.mjs`, and Task 4 corrects the spec inline.

## How this plan was verified

Every code block below was written, run, and reassembled before the plan was written. The three
script parts concatenate to the tested file exactly. Against the repository: the tests fail with
`ENOENT` before the script exists and pass 7 of 7 after Task 1; a mutation that starts the light
accent at L 0.66 and lowers the guard to 3:1 fails the two readability tests; a build with Tasks 1–3
applied passes `check_pages.py`, emits the script after `aim.css` in `<head>`, resolves its path at
every page depth, and finds the palette toggle the picker attaches to.

What was **not** verified is anything that needs a browser: first paint, the popover, and keyboard
behaviour. Task 3 ends with that manual check.

---

### Task 1: Colour derivation, tested

**Files:**
- Create: `docs/assets/javascripts/aim-theme.js`
- Create: `scripts/aim-theme.test.mjs`

**Interfaces:**
- Consumes: nothing.
- Produces, on the global object as `aimTheme`:
  - `PRESETS`: array of `{ name: string, seed: "#rrggbb" }`, eight entries, Brick first.
  - `DEFAULT_SEED`: `"#9c3522"`.
  - `derive(seed: string) -> { light: {token: hex}, dark: {token: hex} } | null`.
  - `isDefault(seed: string) -> boolean`.
  - `toCss(tokens) -> string`, two blocks on the scheme selectors.
  - `contrast(hexA, hexB) -> number` and `oklchHex(L, C, H) -> "#rrggbb"`, for tests.
- The script's last two lines inside the wrapper are
  `  if (typeof document === "undefined") return;` followed by a blank line; Tasks 2 and 3 insert
  code before the closing `})(typeof globalThis !== "undefined" ? globalThis : this);` line.

- [ ] **Step 1: Write the test**

Create `scripts/aim-theme.test.mjs`:

````javascript
// Tests for the colour derivation in docs/assets/javascripts/aim-theme.js.
// Run with: node --test scripts/
import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import vm from "node:vm";

// The script is a classic browser script, so it is run in a fresh context rather than imported.
// Without a document it stops after defining aimTheme, which is all the derivation needs.
const source = new URL("../docs/assets/javascripts/aim-theme.js", import.meta.url);
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(source, "utf8"), context);
const theme = context.aimTheme;

const HEX = /^#[0-9a-f]{6}([0-9a-f]{2})?$/;
const NIGHT_FG = "#e8eaf0";

function sweep() {
  const seeds = [];
  for (let hue = 0; hue < 360; hue += 10) {
    for (const chroma of [0.05, 0.12, 0.25]) seeds.push(theme.oklchHex(0.55, chroma, hue));
  }
  return seeds;
}

function assertReadable(seed, tokens) {
  const l = tokens.light;
  const d = tokens.dark;
  const at = (a, b) => theme.contrast(a.slice(0, 7), b.slice(0, 7));
  const pairs = [
    ["light accent on white", l["--aim-accent"], "#ffffff"],
    ["light accent on chrome", l["--aim-accent"], l["--aim-chrome"]],
    ["light heading on white", l["--aim-heading"], "#ffffff"],
    ["light NOTE title on white", l["--aim-key-ink"], "#ffffff"],
    ["dark accent on page", d["--aim-accent"], d["--md-default-bg-color"]],
    ["dark accent on night", d["--aim-accent"], d["--aim-night"]],
    ["dark heading on page", d["--aim-heading"], d["--md-default-bg-color"]],
    ["dark NOTE title on page", d["--aim-key-ink"], d["--md-default-bg-color"]],
    ["light MYTH tag ink", l["--aim-tag-ink"], l["--aim-accent"]],
    ["light NOTE tag ink", l["--aim-key-tag-ink"], l["--aim-key"]],
    ["dark MYTH tag ink", d["--aim-tag-ink"], d["--aim-accent"]],
    ["dark NOTE tag ink", d["--aim-key-tag-ink"], d["--aim-key"]],
    ["dark hero button ink", d["--aim-chrome-on-accent"], d["--aim-chrome-accent"]]
  ];
  for (const [name, fg, bg] of pairs) {
    const ratio = at(fg, bg);
    assert.ok(ratio >= 4.5, `${seed}: ${name} is ${ratio.toFixed(2)}:1 (${fg} on ${bg})`);
  }
}

test("every preset derives a readable palette", () => {
  assert.equal(theme.PRESETS.length, 8);
  for (const preset of theme.PRESETS) {
    const tokens = theme.derive(preset.seed);
    assert.ok(tokens, `${preset.name} did not derive`);
    assertReadable(preset.seed, tokens);
  }
});

test("a sweep of 36 hues at 3 chroma levels derives readable palettes", () => {
  const seeds = sweep();
  assert.equal(seeds.length, 108);
  for (const seed of seeds) {
    const tokens = theme.derive(seed);
    assert.ok(tokens, `${seed} did not derive`);
    assertReadable(seed, tokens);
  }
});

test("every derived value is a lower-case hex colour", () => {
  for (const seed of [...theme.PRESETS.map((p) => p.seed), ...sweep()]) {
    const tokens = theme.derive(seed);
    for (const scheme of ["light", "dark"]) {
      for (const [name, value] of Object.entries(tokens[scheme])) {
        assert.match(value, HEX, `${seed} ${scheme} ${name} = ${value}`);
      }
    }
  }
});

test("tag ink is one of the two night inks", () => {
  for (const preset of theme.PRESETS) {
    const tokens = theme.derive(preset.seed);
    for (const scheme of ["light", "dark"]) {
      const night = tokens.dark["--aim-night"];
      for (const name of ["--aim-tag-ink", "--aim-key-tag-ink"]) {
        assert.ok([night, NIGHT_FG].includes(tokens[scheme][name]), `${preset.name} ${scheme} ${name}`);
      }
    }
  }
});

test("Brick is the default in any letter case, and no other preset is", () => {
  assert.equal(theme.isDefault("#9c3522"), true);
  assert.equal(theme.isDefault(" #9C3522 "), true);
  for (const preset of theme.PRESETS.slice(1)) assert.equal(theme.isDefault(preset.seed), false);
  assert.equal(theme.isDefault(null), false);
});

test("malformed seeds derive nothing", () => {
  for (const seed of ["", "red", "#abc", "#12345g", "9c35220", null, undefined]) {
    assert.equal(theme.derive(seed), null, String(seed));
  }
});

test("the stylesheet sets every token under both scheme selectors", () => {
  const tokens = theme.derive("#1f7a78");
  const css = theme.toCss(tokens);
  const [light, dark] = css.split('[data-md-color-scheme="slate"][data-md-color-primary] {');
  assert.ok(light.startsWith('[data-md-color-scheme="default"][data-md-color-primary] {'));
  for (const [name, value] of Object.entries(tokens.light)) assert.ok(light.includes(`${name}: ${value};`), name);
  for (const [name, value] of Object.entries(tokens.dark)) assert.ok(dark.includes(`${name}: ${value};`), name);
});
````

- [ ] **Step 2: Run it and watch it fail**

Run: `node --test scripts/aim-theme.test.mjs`

Expected: FAIL, with `Error: ENOENT: no such file or directory, open '...docs\assets\javascripts\aim-theme.js'`
and `pass 0`. The script does not exist yet.

- [ ] **Step 3: Write the derivation**

Create `docs/assets/javascripts/aim-theme.js` with exactly:

````javascript
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

})(typeof globalThis !== "undefined" ? globalThis : this);
````

- [ ] **Step 4: Run the tests and watch them pass**

Run: `node --test scripts/aim-theme.test.mjs`

Expected: `pass 7`, `fail 0`, with these seven names:

```
✔ every preset derives a readable palette
✔ a sweep of 36 hues at 3 chroma levels derives readable palettes
✔ every derived value is a lower-case hex colour
✔ tag ink is one of the two night inks
✔ Brick is the default in any letter case, and no other preset is
✔ malformed seeds derive nothing
✔ the stylesheet sets every token under both scheme selectors
```

- [ ] **Step 5: Prove the readability tests can fail**

In `docs/assets/javascripts/aim-theme.js`, temporarily change `var TEXT_CONTRAST = 4.5;` to
`var TEXT_CONTRAST = 3;` and `guard(0.48, Math.min(c, 0.14), h, [WHITE, chrome], -0.01)` to
`guard(0.66, Math.min(c, 0.14), h, [WHITE, chrome], -0.01)`.

Run: `node --test scripts/aim-theme.test.mjs`

Expected: `pass 5`, `fail 2` — the preset and sweep readability tests.

Undo both changes, run again, and confirm `pass 7`.

- [ ] **Step 6: Commit**

```bash
git add docs/assets/javascripts/aim-theme.js scripts/aim-theme.test.mjs
git commit -m "feat: derive a colour palette from one seed" -m "The theme picker needs every scheme-dependent colour token from a single reader-chosen colour. The derivation works in OKLCH, takes its target lightness from today's palette, and walks each text colour until it clears 4.5:1 against its backgrounds, so any seed produces a readable site or none at all." -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Apply a saved colour before first paint

**Files:**
- Modify: `docs/assets/javascripts/aim-theme.js` (insert before the closing line)
- Create: `overrides/main.html`
- Modify: `zensical.toml` (`[project.theme]`)

**Interfaces:**
- Consumes: `derive`, `isDefault`, `toCss`, `parseHex`, `DEFAULT_SEED` from Task 1, in the same
  closure.
- Produces, in the same closure for Task 3: `apply(seed) -> boolean`, `reset()`, the variable
  `active` (current seed, lower-case), and the array `listeners` of functions called with `active`
  after every change. Also adds `aimTheme.apply` and `aimTheme.reset`.

- [ ] **Step 1: Insert storage, painting, and early paint**

In `docs/assets/javascripts/aim-theme.js`, insert this block immediately before the final line
`})(typeof globalThis !== "undefined" ? globalThis : this);`, after the blank line that follows `if (typeof document === "undefined") return;`:

````javascript
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

````

- [ ] **Step 2: Confirm the derivation tests still pass**

Run: `node --check docs/assets/javascripts/aim-theme.js && node --test scripts/aim-theme.test.mjs`

Expected: no syntax error, then `pass 7`, `fail 0`. Node has no `document`, so the new block never
runs there.

- [ ] **Step 3: Create the template override**

Create `overrides/main.html`:

```html
{% extends "base.html" %}

{% block extrahead %}
  <script src="{{ 'assets/javascripts/aim-theme.js' | url }}"></script>
{% endblock %}
```

- [ ] **Step 4: Point the theme at it**

In `zensical.toml`, under `[project.theme]`, add a line directly after `name = "material"`:

```toml
custom_dir = "overrides"
```

- [ ] **Step 5: Build and check the script lands after the stylesheet**

Run: `python scripts/check_pages.py` — expected `All pages OK`.

Run: `zensical build` — expected `Build finished`, no warnings.

Run:

```bash
python - <<'EOF'
import re
h = open('site/wiki/fundamentals/how-aim-works/index.html', encoding='utf-8').read()
head = h[:h.index('</head>')]
i_css, i_js = head.find('assets/stylesheets/aim.css'), head.find('aim-theme.js')
print('script after aim.css:', 0 < i_css < i_js)
print(re.search(r'<script src="[^"]*aim-theme\.js"></script>', head).group(0))
print('root src:', re.search(r'<script src="([^"]*aim-theme\.js)"', open('site/index.html', encoding='utf-8').read()).group(1))
EOF
```

Expected:

```
script after aim.css: True
<script src="../../../assets/javascripts/aim-theme.js"></script>
root src: ./assets/javascripts/aim-theme.js
```

- [ ] **Step 6: Commit**

```bash
git add docs/assets/javascripts/aim-theme.js overrides/main.html zensical.toml
git commit -m "feat: apply a saved colour theme before first paint" -m "A template override loads the colour script from head, after aim.css, so a saved seed's tokens are written before the page draws and there is no flash of the default palette. With nothing saved, or Brick saved, nothing is written. Storage errors read as nothing saved." -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: The header picker

**Files:**
- Modify: `docs/assets/javascripts/aim-theme.js` (insert before the closing line)
- Modify: `docs/assets/stylesheets/aim.css` (append, and the header component list)

**Interfaces:**
- Consumes: `apply`, `reset`, `active`, `listeners`, `PRESETS` from Tasks 1 and 2, in the closure.
- Produces: the picker markup in the header, using the classes styled below. Nothing later depends on
  it.

- [ ] **Step 1: Insert the picker**

In `docs/assets/javascripts/aim-theme.js`, insert this block immediately before the final line
`})(typeof globalThis !== "undefined" ? globalThis : this);`, after the block Task 2 added:

````javascript
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
````

- [ ] **Step 2: Syntax-check and re-run the tests**

Run: `node --check docs/assets/javascripts/aim-theme.js && node --test scripts/aim-theme.test.mjs`

Expected: no syntax error, `pass 7`, `fail 0`.

- [ ] **Step 3: Style the picker**

Append to the end of `docs/assets/stylesheets/aim.css`:

````css
/* .aim-theme-picker — the colour picker in the header. docs/assets/javascripts/aim-theme.js inserts
 * it next to the light/dark toggle, so no Markdown produces it:
 *
 *   <div class="md-header__option aim-theme-picker">
 *     <button class="md-header__button md-icon aim-theme-picker__button">…dot…</button>
 *     <div class="aim-theme-picker__panel" role="dialog" hidden>
 *       swatches, a Custom… colour input, a status line, and Reset
 *     </div>
 *   </div>
 *
 * Every colour here reads from the site's tokens, so the picker re-colours with the page it
 * changes. The button's dot is the live accent, so it always shows the colour in use. */
.aim-theme-picker {
  position: relative;
}

.aim-theme-picker__button {
  border: 0;
  background: none;
  cursor: pointer;
}

.aim-theme-picker__dot {
  display: block;
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background-color: var(--aim-accent);
  box-shadow: 0 0 0 2px var(--aim-chrome), 0 0 0 3px var(--aim-chrome-fg-lighter);
}

.aim-theme-picker__panel {
  position: absolute;
  top: calc(100% + 0.3rem);
  right: 0;
  z-index: 10;
  width: 12rem;
  padding: 0.8rem;
  border: 1px solid var(--md-default-fg-color--lightest);
  color: var(--md-default-fg-color);
  background-color: var(--md-default-bg-color);
  box-shadow: 0 0.3rem 1rem #0000002e;
  font-size: 0.68rem;
}

.aim-theme-picker__panel:not([hidden]) {
  display: grid;
  gap: 0.7rem;
}

.aim-theme-picker__swatches {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
  justify-items: center;
}

.aim-theme-picker__swatch {
  width: 1.8rem;
  height: 1.8rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background-color: var(--aim-swatch);
  cursor: pointer;
}

/* The chosen swatch gets a ring in the page's own ink, clear of the swatch by a gap of page
 * background, so it shows on every swatch colour in both schemes. */
.aim-theme-picker__swatch[aria-checked="true"] {
  box-shadow: 0 0 0 2px var(--md-default-bg-color), 0 0 0 4px var(--md-default-fg-color);
}

.aim-theme-picker__swatch:focus-visible,
.aim-theme-picker__reset:focus-visible,
.aim-theme-picker__input:focus-visible {
  outline: 2px solid var(--aim-accent);
  outline-offset: 3px;
}

.aim-theme-picker__custom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  cursor: pointer;
}

.aim-theme-picker__custom[data-active] {
  font-weight: 700;
}

.aim-theme-picker__input {
  width: 2.2rem;
  height: 1.4rem;
  padding: 0;
  border: 1px solid var(--md-default-fg-color--lighter);
  background: none;
  cursor: pointer;
}

.aim-theme-picker__message {
  margin: 0;
  color: var(--aim-accent);
}

.aim-theme-picker__reset {
  justify-self: start;
  padding: 0;
  border: 0;
  color: var(--aim-accent);
  background: none;
  font: inherit;
  font-family: var(--aim-display);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}
````

- [ ] **Step 4: Add the component to the stylesheet's header list**

In `docs/assets/stylesheets/aim.css`, replace:

```
 * it: .aim-hero, .aim-cards, .aim-steps, .aim-category, .aim-table-stack, .aim-myth, .aim-key.
```

with:

```
 * it: .aim-hero, .aim-cards, .aim-steps, .aim-category, .aim-table-stack, .aim-myth, .aim-key,
 * .aim-theme-picker.
```

- [ ] **Step 5: Build**

Run: `python scripts/check_pages.py` — expected `All pages OK`.
Run: `zensical build` — expected `Build finished`, no warnings.

- [ ] **Step 6: Check it in a browser**

Run `zensical serve` and open a wiki page. Confirm each of these by hand; none is covered by tests:

1. A dot in the current accent sits right of the light/dark toggle.
2. Clicking it opens the panel with focus on the Brick swatch; Escape closes it and returns focus.
3. Teal re-colours links, headings, the header, the myth and NOTE blocks at once; the arrow keys move
   between swatches and apply each.
4. Reload: the page opens already teal, with no brick flash first.
5. The light/dark toggle keeps working with Teal active, and both schemes look derived.
6. Custom… with a pale yellow applies a darker, readable yellow, not the pale one.
7. Reset returns to Brick; reload stays Brick, and `localStorage.getItem("aim.theme.seed")` is `null`.
8. In a private window with storage blocked, choosing a colour still applies until the page is left.

If any fails, fix it in `aim-theme.js` or the picker CSS, then re-run Steps 2 and 5.

- [ ] **Step 7: Commit**

```bash
git add docs/assets/javascripts/aim-theme.js docs/assets/stylesheets/aim.css
git commit -m "feat: add a colour picker to the header" -m "A dot beside the light/dark toggle opens eight preset colours, a custom colour input, and Reset. The dot shows the colour in use, the swatches are a keyboard radio group, Escape closes the panel and returns focus, and a colour that cannot be made readable is refused with a message rather than applied." -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: CI, docs, and the spec correction

**Files:**
- Modify: `.github/workflows/check.yml` (the `build` job)
- Modify: `AGENTS.md` (Layout table and Page components section)
- Modify: `specs/2026-09-13-theme-picker-design.md` (Testing section)

**Interfaces:**
- Consumes: `scripts/aim-theme.test.mjs` from Task 1.
- Produces: nothing later tasks use.

- [ ] **Step 1: Run the tests in CI**

In `.github/workflows/check.yml`, in the `build` job, replace:

```yaml
      - run: pip install -r requirements.txt
      - run: python scripts/check_pages.py
```

with:

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: node --test scripts/aim-theme.test.mjs
      - run: pip install -r requirements.txt
      - run: python scripts/check_pages.py
```

- [ ] **Step 2: Update the layout table in `AGENTS.md`**

Replace:

```markdown
| `docs/assets/` | Favicon and `stylesheets/aim.css`, which documents each page component it defines. |
```

with:

```markdown
| `docs/assets/` | Favicon, `stylesheets/aim.css`, which documents each page component it defines, and `javascripts/aim-theme.js`, the colour picker. |
| `overrides/` | Theme template overrides. `main.html` loads the colour picker script in `<head>`. |
```

- [ ] **Step 3: Add the token note to `AGENTS.md`**

In the `## Page components` section, immediately before the line `## Rules that are easy to get wrong`,
insert:

```markdown
Colour tokens in `aim.css` are also written by `docs/assets/javascripts/aim-theme.js` when a reader
picks a colour. A new scheme-dependent colour token has to be added to `derive` there as well, or it
keeps its default colour under every picked colour, and no test catches that.
```

followed by one blank line.

- [ ] **Step 4: Correct the spec's test command**

In `specs/2026-09-13-theme-picker-design.md`, replace:

```markdown
`scripts/aim-theme.test.mjs`, run with `node --test scripts/`, loads `aim-theme.js` into a `node:vm`
```

with:

```markdown
`scripts/aim-theme.test.mjs`, run with `node --test scripts/aim-theme.test.mjs`, loads `aim-theme.js` into a `node:vm`
```

and replace `CI's build job gains a Node setup step and
`node --test scripts/` before` with `CI's build job gains a Node setup step and
`node --test scripts/aim-theme.test.mjs` before`. Then add, at the end of the Testing section:

```markdown
2026-09-13: the command was `node --test scripts/` at approval. Node 24 rejects a directory there,
so the test file is named explicitly.
```

- [ ] **Step 5: Run every check**

Run: `node --test scripts/aim-theme.test.mjs` — expected `pass 7`, `fail 0`.
Run: `python scripts/check_pages.py` — expected `All pages OK`.
Run: `zensical build --clean` — expected `Build finished`, no warnings.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/check.yml AGENTS.md specs/2026-09-13-theme-picker-design.md
git commit -m "ci: run the colour theme tests and document the picker" -m "CI now runs the derivation tests before the page checks. AGENTS.md records where the picker lives and that a new colour token must be added to the derivation too, the one gap the tests cannot see. The spec's test command is corrected: Node 24 does not accept a directory for --test." -m "Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.** Default behaviour, no injection: Task 2 early paint skips a missing or Brick seed;
Global Constraints. `overrides/main.html` and `custom_dir`: Task 2 Steps 3–4. Script parts in order,
pure derivation, `node:vm` loading: Task 1. Tokens derived, including the `:root`-resolved ones the
spec's table did not list: Task 1's `derive`, commented in place. Guards and chroma retry: `guard` and
`tagInk`. Gamut: `fit`. Presets: `PRESETS`. Picker button, popover, keyboard, failure message:
Task 3. Persistence: `readSeed`, `writeSeed`, Task 2. Testing 1–5: the seven tests. CI: Task 4 Step 1.
AGENTS.md note and the header component list: Task 4 Steps 2–3, Task 3 Step 4. Manual browser check:
Task 3 Step 6.

**Addition to the spec.** The spec's token table lists `--aim-night`, but `aim.css` resolves
`--aim-chrome`, `--aim-chrome-accent`, `--aim-chrome-on-accent` and `--aim-chrome-on-hover` from night
at `:root`, where `var()` resolves before the scheme block exists. Overriding night alone would leave
the dark scheme's header, footer and hero on the default near-black, so `derive` writes those four
too. This is recorded in a comment beside them.

**Placeholders.** None. Every code step carries the complete code, taken from files that were run.

**Name consistency.** `apply`, `reset`, `active`, `listeners`, `paint`, `readSeed`, `writeSeed` are
defined in Task 2 and used in Task 3 by those names. `derive`, `isDefault`, `toCss`, `parseHex`,
`PRESETS`, `DEFAULT_SEED` are defined in Task 1. The picker's class names in Task 3's script match
the selectors in Task 3's CSS.
