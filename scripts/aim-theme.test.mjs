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
    ["dark accent on page", d["--aim-accent"], d["--md-default-bg-color"]],
    ["dark accent on night", d["--aim-accent"], d["--aim-night"]],
    ["dark heading on page", d["--aim-heading"], d["--md-default-bg-color"]],
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

test("grey seeds derive readable, neutral palettes", () => {
  for (const seed of ["#656565", "#000000", "#ffffff", "#808080", "#1a1a1a", "#f0f0f0"]) {
    const tokens = theme.derive(seed);
    assert.ok(tokens, `${seed} did not derive`);
    assertReadable(seed, tokens);
    // A grey seed must not tint the chrome or the dark page: every channel within 2 of each other.
    for (const hex of [tokens.light["--aim-chrome"], tokens.dark["--md-default-bg-color"], tokens.dark["--aim-night"]]) {
      const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
      assert.ok(Math.max(r, g, b) - Math.min(r, g, b) <= 2, `${seed}: ${hex} is tinted`);
    }
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

test("the dark hero button's ink is one of the two night inks", () => {
  for (const preset of theme.PRESETS) {
    const dark = theme.derive(preset.seed).dark;
    assert.ok([dark["--aim-night"], NIGHT_FG].includes(dark["--aim-chrome-on-accent"]), preset.name);
  }
});

test("myth and NOTE colours are never derived", () => {
  const fixed = ["--aim-myth", "--aim-myth-wash", "--aim-key", "--aim-key-ink", "--aim-key-wash", "--aim-tag-ink", "--aim-key-tag-ink"];
  for (const seed of [...theme.PRESETS.map((p) => p.seed), "#656565"]) {
    const tokens = theme.derive(seed);
    for (const scheme of ["light", "dark"]) {
      for (const name of fixed) assert.equal(tokens[scheme][name], undefined, `${seed} ${scheme} writes ${name}`);
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
