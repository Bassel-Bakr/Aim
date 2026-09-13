# Theme picker — Design

Date: 2026-09-13
Status: Approved in brainstorming, pending spec review
Maintenance: kept in step with the repository. Changes made after approval are marked inline with
the date they landed, rather than rewritten silently.

## Goal

A reader can pick one colour, and the whole site re-colours around it in both light and dark
schemes. The picker sits in the header next to the light/dark toggle. Until a reader picks
something, the site looks exactly as it does today.

## Non-goals

- Changing the category colours. `--aim-clicking`, `--aim-tracking` and `--aim-switching` identify
  the same three categories on every page, and re-hueing them could make two categories look alike.
- Changing neutral text. Body ink, the dark scheme's body text, and code colours stay as they are.
- Fonts, spacing, or anything other than colour.
- Syncing a choice across devices or visitors. The choice lives in one browser.
- A picker that works without JavaScript. Without JavaScript the site shows its default colours,
  which is the same as a reader who never opened the picker.

## Default behaviour

The stylesheet stays the source of the default palette. With no saved seed, the script injects
nothing, so the default site is byte-for-byte the colours `aim.css` defines today, and a visitor
without JavaScript sees the same. Brick, the first preset, is that default: choosing it clears the
saved seed rather than deriving a palette that approximates the stylesheet.

## Pieces

### `overrides/main.html` (new)

A template that extends the theme's `base.html` and fills its `extrahead` block with one blocking
script tag:

```html
{% extends "base.html" %}

{% block extrahead %}
  <script src="{{ 'assets/javascripts/aim-theme.js' | url }}"></script>
{% endblock %}
```

`zensical.toml` gains `custom_dir = "overrides"` under `[project.theme]`. The base template emits
`extra_css` before `extrahead`, so the script runs after `aim.css` has loaded and a `<style>` it
appends wins on source order. Because it runs in `<head>` before the body is parsed, the derived
colours are in place before first paint: no flash of the default palette.

No theme partial is copied. The palette toggle's partial and script are generated files the theme
may change on upgrade; the picker attaches to the rendered header from the script instead.

### `docs/assets/javascripts/aim-theme.js` (new)

One file with three parts, in order:

1. **Colour maths.** sRGB ↔ OKLCH conversion, relative luminance, contrast ratio, and gamut mapping.
2. **Derivation.** `derive(seedHex)` returns the full token set for both schemes. It is pure: no DOM,
   no storage, so it can be tested in Node.
3. **Wiring.** On load, read the saved seed and, if valid, inject the derived tokens. After
   `DOMContentLoaded`, insert the picker button and its popover next to the light/dark toggle.

The file assigns `aimTheme = { derive, isDefault, apply, reset, PRESETS }` on the global object.
When `document` is absent it stops after that assignment, so Node can load it for tests with
`node:vm` without a DOM. It stays a single classic script with no build step, so the site keeps
having none. `derive` and `isDefault` are pure; `apply` and `reset` touch the DOM and storage.

### `docs/assets/stylesheets/aim.css`

Gains styles for the picker button and popover, documented above their rules as every component in
the file is. Colours in those rules read from existing tokens, so the popover re-colours with the
rest of the site. No existing rule changes.

## Derivation

The seed is converted to OKLCH. Its hue `h` drives every derived colour. Its chroma `c` is kept
where a role wants a strong colour, capped per role so a neon seed does not produce a neon page.

### Tokens derived

These are every scheme-dependent colour token in `aim.css` except the category colours and neutral
ink. The injected `<style>` sets them inside the same two scheme selectors the stylesheet uses,
`[data-md-color-scheme="default"][data-md-color-primary]` and
`[data-md-color-scheme="slate"][data-md-color-primary]`, so the light/dark toggle keeps working
untouched.

| Token | Light scheme | Dark scheme |
| --- | --- | --- |
| `--aim-accent` | L 0.48, C min(c, 0.14) | L 0.71, C min(c, 0.13) |
| `--aim-heading` | L 0.38, C min(c, 0.12) | L 0.80, C min(c, 0.10) |
| `--aim-myth-wash` | accent at 6% alpha | accent at 8% alpha |
| `--md-accent-fg-color--transparent` | accent at 8% alpha | accent at 12% alpha |
| `--aim-chrome` | L 0.915, C 0.012 | — (uses `--aim-night`) |
| `--aim-night` | — | L 0.16, C 0.008 |
| `--aim-night-accent` | — | same as dark `--aim-accent` |
| `--md-default-bg-color` | — | L 0.15, C 0.008 |
| `--aim-key` | hue h+50°, L 0.76, C 0.15 | hue h+50°, L 0.82, C 0.13 |
| `--aim-key-ink` | hue h+50°, L 0.45, C 0.10 | same as dark `--aim-key` |
| `--aim-key-wash` | key at 12% alpha | key at 8% alpha |
| `--aim-tag-ink`, `--aim-key-tag-ink` | chosen per tag, see guards | chosen per tag, see guards |

`--aim-nav-active-bg` and `--aim-chrome-accent` already reference tokens above, so they follow
without being set directly.

The targets are taken from today's palette measured in OKLCH, so a seed near brick lands near the
current look: light accent `#9c3522` is L 0.476, C 0.141, h 32.6; dark accent `#e38268` is L 0.706,
C 0.126; light NOTE `#e0a800` is L 0.763, C 0.157, h 84.4; dark NOTE `#f2c14e` is L 0.834, h 85.4.
The NOTE hue offset of +50° is the gap between accent and NOTE in those measurements, 51.8° light
and 49.5° dark, so the default pair's relationship carries to every seed.

2026-09-13: two changes after the first build. Myth and NOTE blocks are no longer derived: they keep
fixed colours under every picked colour, so red means wrong and yellow means remember on every page.
The myth block reads a new fixed `--aim-myth` token instead of the accent, and `--aim-myth-wash`,
the `--aim-key` family and both tag inks drop out of the derived set; `derive` still writes
`--aim-chrome-on-accent` for the dark hero button. Grey seeds, which have almost no chroma, were
rejected because the guard's chroma loop never ran below its minimum; the guard now always tries the
chroma it is given, and the chrome and dark page tints scale with the seed's chroma so a grey seed
gives neutral ones.

### Guards

After the targets above, each guard adjusts lightness in steps of 0.01 until it passes, moving away
from the background it is measured against:

| Colour | Must reach | Against |
| --- | --- | --- |
| Light accent | 4.5:1 | white, and light `--aim-chrome` |
| Light heading | 4.5:1 | white |
| Light NOTE title (`--aim-key-ink`) | 4.5:1 | white |
| Dark accent | 4.5:1 | dark `--md-default-bg-color`, and dark `--aim-night` |
| Dark heading | 4.5:1 | dark `--md-default-bg-color` |
| Dark NOTE title | 4.5:1 | dark `--md-default-bg-color` |
| Tag ink | 4.5:1 | its tag colour (accent for MYTH, key for NOTE) |

Tag ink is not adjusted; it is chosen. Each tag takes whichever of `--aim-night` and
`--aim-night-fg` gives the higher contrast on its tag colour, and the guard confirms the winner
clears 4.5:1. If a guard runs out of lightness range before passing, derivation reduces that
colour's chroma and retries; a seed that still fails is rejected and the default palette stays.

### Gamut

Every OKLCH colour is mapped into sRGB by reducing chroma at fixed lightness and hue until it fits,
before any guard measures it. Output is always a six-digit or eight-digit hex string.

## Presets

Eight seeds, each a hex colour run through the same `derive`:

| Name | Seed |
| --- | --- |
| Brick (default) | `#9c3522` |
| Teal | `#1f7a78` |
| Forest | `#3f7a3a` |
| Cobalt | `#2f5fb3` |
| Violet | `#6f4bb0` |
| Rose | `#b0406e` |
| Amber | `#a8680f` |
| Slate | `#4f6272` |

Brick clears the saved seed instead of deriving, per Default behaviour.

## Picker

**Button.** An icon button in `.md-header__option`, immediately after the light/dark toggle, with
`aria-label="Change colour"`, `aria-haspopup="dialog"` and `aria-expanded`. The icon is a filled
circle drawn in the current `--aim-accent`, so the button shows the active colour.

**Popover.** A small panel anchored under the button:

- A radio group of the eight presets, each a swatch with its name as the accessible label. The
  active preset is `aria-checked="true"`.
- "Custom…", a native `<input type="color">`. Changing it applies the colour live. A custom seed
  shows as checked in place of any preset.
- "Reset", which clears the saved seed and returns to Brick.

**Keyboard.** The button opens and closes the popover with Enter or Space. Arrow keys move between
swatches. Escape closes the popover and returns focus to the button. Clicking outside closes it.

**Failure.** If `derive` rejects a custom colour, the popover says so in a short line under the
colour input and keeps the previous colour.

## Persistence

The seed is stored as a hex string in `localStorage` under `aim.theme.seed`. Every read and write is
wrapped in try/catch, so private browsing or blocked storage falls back to the default palette. A
stored value that is not a valid `#rrggbb` string is ignored and removed.

## Testing

`scripts/aim-theme.test.mjs`, run with `node --test scripts/aim-theme.test.mjs`, loads `aim-theme.js` into a `node:vm`
context and checks:

1. Every preset, Brick included, derives a full token set with no guard failure.
2. A sweep of 36 hues × 3 chroma levels (0.05, 0.12, 0.25) at L 0.55 derives without failure, and
   every guard in the table above holds on the output.
3. Every output colour is a valid hex string inside the sRGB gamut.
4. Tag ink on both tags reaches 4.5:1 for every derived palette.
5. `isDefault` is true for Brick in any letter case and false for every other preset, so choosing
   Brick clears the override rather than deriving one.

The page check and the site build stay green. CI's build job gains a Node setup step and
`node --test scripts/aim-theme.test.mjs` before `zensical build`. A manual check in a browser covers what the tests
cannot: first paint without a flash, the popover's keyboard behaviour, and the light/dark toggle
with a custom colour active.

2026-09-13: the command was `node --test scripts/` at approval. Node 24 rejects a directory there,
so the test file is named explicitly.

## Documentation

`AGENTS.md` gains a row in its layout table for `overrides/` and a short note that colour tokens in
`aim.css` are also written by `aim-theme.js`, so a new colour token must be added to both, or it
will not re-colour. `aim.css`'s header comment gains `.aim-theme-picker` in its component list.

## Risks

- **A token added to `aim.css` but not to `derive`** stays at its default under a custom colour. The
  AGENTS.md note is the guard against that; the test suite checks `derive`'s output, not the
  stylesheet, so it cannot catch it.
- **Theme upgrades** could rename `.md-header__option`, where the button attaches. The script looks
  the element up once and does nothing if it is missing, so an upgrade degrades to no picker, not to
  a broken header.
- **The blocking head script** adds one small request before first paint. It is a few kilobytes and
  cached after the first page.
