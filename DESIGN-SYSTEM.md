# Extera Design System v2

Supersedes the v1 style guide, which was a faithful copy of the old extera.co.uk look. v2 keeps what makes Extera recognisable (the logo, the brand blue, Open Sans, night-city photography) and modernises everything around it. Generated with the ui-ux-pro-max skill (pattern: Trust & Authority + Conversion, accessible style, Poppins + Open Sans pairing), then adapted to the brand. Live reference: [styleguide.html](styleguide.html). Source of truth: the tokens at the top of [assets/styles.css](assets/styles.css).

## Principles
1. **Trust first.** Accreditations and partners sit high on the page and are never hidden.
2. **One accent.** Extera blue is the only colour; everything else is a cool slate neutral.
3. **Accessible by default.** 4.5:1 text contrast, visible focus rings, 44px+ targets, reduced motion respected.
4. **Fluid, not stepped.** Type and section spacing scale with the viewport; layout collapses at set breakpoints.
5. **Quiet motion.** 200ms ease-out on hover; a subtle fade-up on scroll where the browser supports it.

## Colour

| Token | Hex | Use |
|---|---|---|
| `--brand-50` | `#eef6fc` | Icon tiles, nav hover, tick backgrounds |
| `--brand-100` | `#d6e9f7` | Light borders on blue |
| `--brand-200` | `#aed3ef` | Card hover border |
| `--brand-300` | `#7cc0f0` | Accent text on dark (hero word, footer hover) |
| `--brand-500` | `#1a75bb` | Primary: buttons, links |
| `--focus` | `#155f99` | Focus outline on light backgrounds (6.7:1 on white) |
| `--focus-on-dark` | `#ffffff` | Focus outline on navy areas: hero, top bar, footer, CTA band (14.7:1) |
| `--brand-600` | `#155f99` | Button hover, gradient start |
| `--brand-700` | `#104a77` | Pressed, badge text, link hover |
| `--brand-900` | `#0b2a45` | Top bar, hero base, footer, gradient end |
| `--ink` | `#0f172a` | Headings |
| `--text` | `#334155` | Body |
| `--muted` | `#475569` | Secondary text (5.9:1 on white) |
| `--line` | `#e2e8f0` | Borders, dividers |
| `--surface-alt` | `#f8fafc` | Alternate sections |
| `--surface` | `#ffffff` | Page and cards |

Contrast: white on `#1a75bb` is about 5:1; `--text` on white about 10:1.
Never use brand-300 on a light background.

## Typography
- **Headings:** Poppins 500/600/700, tight tracking (-0.01 to -0.02em), balanced wrapping.
- **Body:** Open Sans 400/600, 16px / 1.7.
- **Scale (fluid):** hero 36 to 60px; H2 28 to 40px; H3 18px; lead 17 to 20px; small 14px.
- Sentence case for headings. Uppercase is only for the small `.eyebrow` label.

## Spacing, shape, depth
- 4px base scale: 8, 16, 24, 40, 64, 96px. Section padding is fluid: 48 to 96px.
- Radius: 8px inputs, 14px tiles, 22px cards, pill buttons and nav.
- Shadow: `--shadow-sm` at rest, `--shadow-md` on hover and menus. Borders are always 1px `--line`.
- Container: 92% wide, max 1240px.

## Components
| Component | Class | Notes |
|---|---|---|
| Header | `.site-header` | Sticky, frosted white, 76px, pill nav, dropdown |
| Hero | `.hero`, `.page-hero` | Left-aligned, navy gradient over photo; last word of H1 in `brand-300` |
| Buttons | `.btn`, `.btn.outline`, `.btn.outline.dark` | Pill, 48px high, lift 1px on hover |
| Service card | `.service` | Icon tile, lifts 3px on hover |
| Card | `.card` | White, 22px radius, `shadow-sm` |
| Tick list | `.ticks` | Round blue check marker (SVG data URI) |
| Badges | `.badges li` | Pill chips for accreditations and partners |
| Accreditation logos | `.accred` | White tiles so JPEG logos sit cleanly on any background |
| Table | `.table-wrap > table` | Scrolls horizontally on small screens |
| FAQ | `details/summary` | Cards with a rotating plus |
| Form | `form`, `label`, `input` | Visible labels, 48px fields, solid outline on focus |
| CTA band | `.cta-band` | Brand-to-navy gradient |
| Section head | `.sec-head` + `.eyebrow` | Small blue label, H2 and lead; `.center` variant |
| Fact bar | `.factbar` | Four proof points directly under the hero |
| Process steps | `.steps` | Numbered, connected steps; stack on small screens |
| Feature row | `.feature` + `.panel` | Text beside an icon panel; `.flip` swaps sides |
| Footer | `.site-footer`, `.socket` | Navy, four columns, copyright bar |

## Responsive behaviour
| Width | Behaviour |
|---|---|
| above 1240px | Full nav, 4 / 3 / 2 column grids, split layouts |
| 1240px or less | Nav collapses to a Menu button (9 labels no longer fit) |
| 1100px or less | 4-column grids become 2 |
| 960px or less | 3-column grids and splits stack, footer becomes one column |
| 560px or less | Everything single column, buttons full width, smaller logo |

Checked on all 12 pages at 375, 768, 1024 and 1280px with no horizontal page scroll (wide tables scroll inside their own container).

## Accessibility and performance rules
- Skip link first in the body; one `h1` per page; landmark `header`, `nav`, `main`, `footer`.
- Focus: a solid 3px outline with a 3px offset on every focusable element, `--focus` on light areas and white on dark areas. Never remove it. A translucent shadow ring failed the 3:1 contrast rule, so do not use one.
- Icons are inline SVG with `aria-hidden`; logos carry real alt text.
- Motion uses `transform` and `opacity` only, and is switched off under `prefers-reduced-motion`.
- Hero image is the only large asset. Before launch, convert it to WebP/AVIF and add `loading="lazy"` to below-the-fold images.

## Not included yet
- Dark mode (the skill marks the style as supporting it; tokens are structured so it can be added by redefining the variables).
- A logo carousel. Partners are static chips, which avoids the pause and keyboard rules a carousel needs.

## Conventions added after the UX audit
- **Banner titles are white.** Blue is reserved for actions and links, so a light-blue first word no longer competes with the buttons.
- **Banner scale:** page titles 48px (home 52px) against section headings at 36px, so the page title is always clearly the largest text.
- **One headline job:** the home title states the offer ("One UK supplier for your phones, internet, mobiles and cabling"). The company name lives in the logo and the small label above the title.
- **Header call to action:** a "Get a quote" button sits in the header on desktop and tablet. On phones the fixed "Call us / Get a quote" bar replaces it, and banner buttons are hidden on phones so there are never duplicates.
- **Every banner has an action:** inner pages show the quote and call buttons, or a page-specific pair (shop and advice on Extera Direct, urgent call and request on Support).
- **Button labels:** conversion buttons say what the visitor gets ("Get a quote", "Get an 8x8 quote", "Request a free trial", "Request my quote"). Navigation buttons start with "See" ("See 3CX", "See the full comparison"), and shop links start with "Shop". Avoid Explore, Browse and Read as button verbs.
- **No visible build notes:** placeholder or "before launch" text must never appear in the page copy.
