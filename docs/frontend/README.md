# Front-end visual reference

The approved look of `src/web/`. Approved by the user on 2026-10-18. `docs/design.md` (DEC-002,
DEC-019, DEC-020, sections 2.2 and 4) owns the structure and the API. This file owns only the look.
If they disagree, the design wins: stop and ask.

## The mockups

| File | Shows | Spec IDs |
| --- | --- | --- |
| `job-view.dc.html` | Job view: job text panel, ranked candidate cards. Navigation on the left. | LST-001, LST-002, JOB-002, JOB-003, RNK-003, REC-001 |
| `candidate-view.dc.html` | Candidate view: raw CV, attributes, ranked job descriptions. | CND-001 to CND-003 |
| `job-view-failures.dc.html` | Job view when LLM calls failed: failure panel, "Not available", a candidate with no score ranked last. | ERR-001, ERR-002, MIS-001, MIS-002 |
| `job-view-phone.dc.html` | Job view at phone width. | `ui-design.md` (responsive) |

The files are Design Component pages. They load a `support.js` runtime that is not in this folder, so
a browser does not render them alone. Read them as a specification of markup, spacing and values. They
use inline styles and script-built strings; the build must not (see "How to build from them").
The data in them (names, CV text, scores) is invented.

## Tokens

Define these once in `src/web/css/theme.css` as CSS custom properties. Nothing else holds a color,
size or radius.

| Token | Value | Use |
| --- | --- | --- |
| `--color-accent` | `#4338FF` | Primary: selected navigation item, rank 1, score bar, chips, focus ring |
| `--color-accent-tint` | accent mixed 9% into white (`color-mix(in srgb, var(--color-accent) 9%, white)`) | Rank 2 and below, chips, recommendation box |
| `--color-ink` | `#14142B` | Text |
| `--color-muted` | `#62667D` | Labels, file names, "Not available" |
| `--color-line` | `#E6E8F3` | Borders and dividers |
| `--color-bg` | `#F5F6FC` | Page background |
| `--color-surface` | `#FFFFFF` | Header, cards, panels, footer |
| `--color-track` | `#ECEDF7` | Score bar track |
| `--color-yes-bg`, `--color-yes-text` | `#D8F7EA`, `#07553D` | Interview badge |
| `--color-no-bg`, `--color-no-text` | `#FFE4DE`, `#9B2A1B` | Do-not-interview badge |
| `--color-unknown-bg`, `--color-unknown-text` | `#ECEDF7`, `#44485F` | Verdict "Not available" |
| `--color-alert-bg`, `--color-alert-border`, `--color-alert-text` | `#FFF1EE`, `#FFC9BF`, `#9B2A1B` | Failure panel (body text in it: `#5A2A22`) |
| `--color-logo-dot` | `#2EE6A8` | Second circle of the logo mark |
| `--font` | `system-ui, -apple-system, 'Segoe UI', sans-serif` | The only font. No download. |
| `--radius-card`, `--radius-control`, `--radius-pill` | `16px`, `12px`, `999px` | Cards and panels, rows and boxes, badges and chips |
| `--doc-max-height` | `230px` (job text), `900px` (CV text) | Scroll box of the `.doc` component (DEC-020) |

Text sizes: page title 30px (24px on a phone), card name 16px, body 15px, attribute value 14px,
label 12px, section label 11px uppercase with 0.08em spacing. Weights: 800 for the logo and rank, 700
for names and scores, 600 for values and navigation items. Line height 1.5.
The muted color on white is 5.6:1 and on `--color-bg` 5.2:1; keep it for text no smaller than 12px.

## Layout

- **Page:** a sticky header (64px, 56px on a phone), then a row with the navigation and the main area,
  then the footer. The row wraps: the navigation is `flex: 1 1 260px; max-width: 300px`, the main area
  `flex: 999 1 560px; min-width: 0`. Padding 32px (16px on a phone), gap 32px.
- **Header:** logo mark (30px rounded square in the accent color, one white and one mint circle),
  "CV Matcher" in 18px/800, and on the right "10 candidates · 3 job descriptions" in 13px muted. The
  counts come from the lists.
- **Navigation:** two groups, "Job descriptions" and "Candidates", each with an 11px uppercase label.
  An item is a link: the title or name (14px/600), then the file name below (12px muted). The selected
  item has the accent background, white text and a file name in white at 82%. Below about 700px the
  navigation becomes two native `<select>` controls, "Job description" and "Candidate" (assumption:
  the design does not say how the navigation collapses).
- **Footer:** one 12px muted line with the dataset attribution (TalentCLEF 2026 Task A, CC BY 4.0).
- **Title block:** title or name (30px/700), file name (13px muted), then the meta line in muted text
  ("All 10 candidates, best match first." in the job view, "title. city, country." in the candidate view).

## Components

- **Job text panel** (job view): a `<details open>` card titled "Job description text", the text
  in the `.doc` box (`white-space: pre-wrap`, 14px, scrolls beyond `--doc-max-height`). DEC-020.
- **Candidate card** (job view): a `<details>` card. The mockup shows some cards open and some folded, to
  show both states. The build opens every card (DEC-019: `<details open>`). The summary row holds: rank square (36px, radius
  12px; rank 1 accent with white, others tint with accent text), name with the file name below, score
  bar (190px wide track, 8px high) with the score to two decimals, the verdict badge, and a chevron
  that turns when the card is open. The body holds a tint box "Recommendation. <reason>", then
  "Extracted" (a grid of label and value cells, then skill chips) and "Calculated" (six cells). Last
  job and Companies span the full row.
- **Verdict badge:** pill, 13px/700, with a check icon for "Interview" and a cross icon for "Do not
  interview". "Not available" has no icon. The label always says the verdict, so color is never the
  only signal.
- **Ranked job row** (candidate view): rank square (32px), title with file name, score bar and score.
  A link to the job view. No verdict (CND-003).
- **Candidate view body:** two columns that wrap: the CV text card (`flex: 1 1 360px`) and a column of
  three cards (Extracted attributes, Calculated attributes, Job descriptions).
- **Failure panel** (`/api/failures`, ERR-001): an alert card above the job text panel with a triangle
  icon, the heading "N results could not be computed", the line "Everything else is shown. Restart the
  app to try again." (ERR-003 retry is withdrawn, so there is no retry button), and one line per failure:
  the item ID in bold, then "step: cause". The mockup's causes are examples of the short messages in
  `docs/design.md`.
- **"Not available"** (MIS-001): the text "Not available" in muted italic, for any `null` value. A
  score that is missing shows it in place of the number and the bar stays empty. The candidate stays in
  the list and is ranked after every scored candidate (MIS-002).
- **Focus:** a 3px accent outline with 2px offset on links, summaries and selects.
- **Icons:** inline stroke SVG, 2 to 3px stroke, `aria-hidden` when decorative. No emoji.

## How to build from them

- Follow `.claude/rules/javascript.md` and `html-css.md`. The mockups use inline styles and strings
  built in script for speed; the build puts every value above in CSS files (`theme.css` tokens, then
  `base.css`, `layout.css`, `detail.css`), clones `<template>` elements from `index.html`, inserts text
  with `textContent`, and toggles CSS classes. No `innerHTML`, no inline `style`.
- Every button and icon control gets a `title`, and an icon-only control an `aria-label`.
- Native controls only: `a`, `details`, `summary`, `select`.
- UI tests (DEC-019, DEC-020) check behavior, not pixels: the header stays at the top while scrolling,
  a file name sits below its name in a smaller size, the job text appears above the ranked candidates,
  "Not available" appears for a `null`, and the failure panel lists each cause.
- The accent color is the one value meant to change. Change `--color-accent` and the tint follows.
