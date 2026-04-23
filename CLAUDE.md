# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Yuguang Zhang's personal portfolio site, served as static files from GitHub Pages at the custom domain in `CNAME` (`www.ygzhang.com`). There is **no build step, no package manager, no test suite, and no framework** — every page is hand-edited HTML committed directly to `master`. Pushing to `master` deploys.

To preview locally, open the `.html` files directly in a browser, or serve the directory with any static server (e.g. `python3 -m http.server`) so relative paths to `css/`, `js/`, and `images/` resolve.

## Architecture

The site started from the **"Magnet" minimal portfolio Bootstrap template**. Every page follows the same skeleton, so when adding or editing pages, copy an existing one rather than writing from scratch:

- `css/bootstrap.min.css` (still used for the grid + navbar collapse classes) and `css/style.css` — load in this order. All site-specific styling lives in `style.css`; per-page tweaks go in an inline `<style>` block in the page head (see `non-human.html` for the pattern).
- A `.navbar` with the same four nav items (Projects → `index.html`, Experiments → `experiments.html`, Blog → external NYU URL, About → `about.html`).
- Page-specific `<section>` content in a Bootstrap 3 `container > row > col-md-*` grid.
- A common `<footer>` whose social icons are **inline SVG** (GitHub / LinkedIn / Instagram / envelope, ~500 bytes each, `fill="currentColor"`). Don't reintroduce FontAwesome.
- One **inline** `<script>` at the bottom — a 4-line vanilla-JS handler that toggles `.in` on `.navbar-collapse` when `.navbar-toggle` is clicked. There is no jQuery and no Bootstrap JS; do not add `<script src="js/...">` tags for those (they were removed in the Phase 1 modernization).

When copying a page to start a new project, use a real project page (e.g. `nephophile.html`) as the source — `single-project.html` is a stale Magnet-template leftover with Lorem ipsum and a live `<i class="fa ...">` that no longer renders.

### Page categories

- **Index pages** — `index.html` (project grid) and `experiments.html` (experiments grid). Each portfolio thumbnail is a `col-md-4 col-sm-6 > a > .portfolio-thumb` block linking to a project page; the cover image lives at `images/<project-slug>/cover.{jpg,png}` or `images/<project-slug>/thumb.*`. Adding a new project means adding both a new page and a new thumbnail block here.
- **Project pages** — one HTML file per project at the repo root (e.g. `nephophile.html`, `non-human.html`, `cloud.html`). `images/<project-slug>/` holds the assets.
- **Interactive p5.js pages** — `ml5js.html`, `non-human.html`, and similar pages embed sketches that load from `js/about/` (`p5.js`, `p5.dom.min.js`, `p5.sound.min.js`, `sketch.js`, `wave600.json`). The `js/about/` folder is the shared p5 library directory despite its name.
- **`-old` / `-new` / `-Copy` files** — `about-old.html`, `index-new.html`, `js/about/ml5js - Copy.html` are stale drafts kept in the tree. Don't modify them when updating the live page; verify which file is actually linked from the nav before editing.

### Image conventions

`images/<project-slug>/` per project. Folder slugs sometimes diverge from the HTML filename (e.g. `machine-timing.html` → `images/maching-timing/`, `frontier-of-concession.html` → `images/frontier-of-consession/`). Check the actual `src` in the existing page rather than assuming a slug.

### Conventions to preserve

- Indentation is 5 spaces in HTML (template style) — match it when editing.
- Keep the nav identical across all pages so the active highlight is the only per-page change (`<li class="active">` on the current section).
- Asset paths are relative (`css/...`, `images/...`, `js/...`) — keep them relative so the site works both on GitHub Pages and when opened from disk.
- Add `loading="lazy"` to every `<img>` after the first one on the page (the first is treated as the above-the-fold cover/hero and stays eager).
- For animated content, prefer `<video autoplay loop muted playsinline src="...mp4">` over animated GIFs. The GIF→MP4 helper at `scripts/gif-to-mp4.py` does the conversion + HTML rewrite for any new heavy GIFs (requires ffmpeg locally; run `python3 scripts/gif-to-mp4.py --apply`).

### Phase 2 (planned, not done)

A visual modernization is planned: drop Bootstrap CSS entirely, rewrite `style.css` (CSS Grid for the portfolio, Flex for the nav), and refresh typography via the `impeccable` design skill. To do that work, install the skill in this project (`npx skills add pbakaus/impeccable` from the repo root), then run `/impeccable teach` to capture design context into `.impeccable.md`, then `/impeccable craft` against the three template pages (`index.html`, a representative project page, `about.html`). Style.css also has dead rules for `#contact`, `#blog`, `#blog-single-post`, `.blog-*` (no such pages exist) that can be deleted in the same pass.