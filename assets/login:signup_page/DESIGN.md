---
name: Liquid Citrus Clay
colors:
  surface: '#faf8ff'
  surface-dim: '#d2d9f4'
  surface-bright: '#faf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f3ff'
  surface-container: '#eaedff'
  surface-container-high: '#e2e7ff'
  surface-container-highest: '#dae2fd'
  on-surface: '#131b2e'
  on-surface-variant: '#584237'
  inverse-surface: '#283044'
  inverse-on-surface: '#eef0ff'
  outline: '#8c7164'
  outline-variant: '#e0c0b1'
  surface-tint: '#9d4300'
  primary: '#9d4300'
  on-primary: '#ffffff'
  primary-container: '#f97316'
  on-primary-container: '#582200'
  inverse-primary: '#ffb690'
  secondary: '#006c49'
  on-secondary: '#ffffff'
  secondary-container: '#6cf8bb'
  on-secondary-container: '#00714d'
  tertiary: '#855300'
  on-tertiary: '#ffffff'
  tertiary-container: '#d78900'
  on-tertiary-container: '#492c00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdbca'
  primary-fixed-dim: '#ffb690'
  on-primary-fixed: '#341100'
  on-primary-fixed-variant: '#783200'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#faf8ff'
  on-background: '#131b2e'
  surface-variant: '#dae2fd'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
    letterSpacing: -0.03em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 30px
    fontWeight: '800'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-numeric:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: -0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2.5rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style
This design system crafts an energetic, optimistic, and radically transparent financial habitat. The aesthetic blends frosted liquid glassmorphism with subtle, pillow-soft claymorphism: tactile, luminous surfaces that feel physical, clean, and elevated without heavy skeuomorphic clutter. 

The emotional tone is confident, refreshing, and organized—countering traditional financial dread with bright porcelain canvases, radiant citrus warmth, and pristine structural clarity. High-contrast typography provides immediate legibility for dense monetary data, while diffused highlights and buoyant colored accents guide the user’s cognitive flow.

## Colors
The foundational canvas is a crisp porcelain white (`#f8fafc` transitioning to `#f1f5f9`), avoiding sterile clinical gray while maintaining pristine luminosity. 

- **Primary (`#f97316` - Warm Citrus Orange):** Drives primary calls to action, high-priority interactive milestones, and active financial tracking states.
- **Secondary (`#10b981` - Fresh Emerald Mint):** Represents positive cash flow, capital yields, security validations, and progress completions.
- **Tertiary (`#f59e0b` - Radiant Marigold):** Applied to secondary metrics, budget warnings, dynamic insights, and active interest gains.
- **Neutral (`#0f172a` - Deep Slate Charcoal):** Delivers uncompromising contrast for balances, ledger lists, headlines, and critical metric labels, stepping down to `#475569` for secondary metadata.

Translucent white layers (`rgba(255, 255, 255, 0.65)` to `rgba(255, 255, 255, 0.85)`) serve as structural cards over tinted ambient underlays.

## Typography
Plus Jakarta Sans delivers friendly authority, wide counters, and geometric clarity across all narrative headings, dashboard structures, and conversational interface zones. 

JetBrains Mono is strategically integrated for raw monetary figures, exchange rates, ticker tickers, and tabular balance statements (`label-numeric`) to prevent horizontal jitter during real-time balance calculations and provide tactile precision. Headings utilize tight negative letter tracking to maintain visual density against airy glass surfaces.

## Layout & Spacing
The layout follows a fluid-responsive 12-column grid system on desktop (switching to 8 columns on tablet and 4 columns on mobile), constrained to a maximum content width of 1440px. 

Components rely on generous internal padding (`space-lg` to `space-xl`) to establish breathing room within glassmorphic frames. Outer canvas boundaries use safe proportional margins (`margin-desktop: 2.5rem`, `margin: 1rem`) to keep interactive cards comfortably detached from screen edges. Stacked balance cards and analytics grids maintain consistent proportional gutters (`gutter: 1.25rem` to `1.5rem`) to accentuate the ambient drop shadows and prevent optical overlapping.

## Elevation & Depth
Depth is produced through a synthesis of frosted glass and soft claymorphism rather than dark, dirty shadows:

1. **Liquid Glass Layer (Base Card):** Built using `backdrop-filter: blur(16px)`, a semi-transparent surface fill (`rgba(255, 255, 255, 0.72)`), and an ultrafine perimeter rim (`border: 1px solid rgba(255, 255, 255, 0.6)`).
2. **Claymorphic Inset Lighting:** Inner specular highlights create a rounded, pillowed feel (`box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.9), inset 0 -2px 4px 0 rgba(226, 232, 240, 0.4)`).
3. **Ambient Tinted Shadows:** Grounding drop shadows are wide, diffuse, and lightly color-tinted with soft slate-blue or ambient citrus glow instead of pure neutral grays:
   - *Elevation 1 (Cards, panels):* `0 10px 25px -5px rgba(15, 23, 42, 0.04), 0 8px 10px -6px rgba(15, 23, 42, 0.02)`
   - *Elevation 2 (Floating actions, modals, active pills):* `0 20px 35px -10px rgba(249, 115, 22, 0.15), 0 1px 3px 0 rgba(0, 0, 0, 0.05)`

## Shapes
A rounded profile (`0.5rem` base, scaling to `1rem` on cards and `1.5rem` on featured containers) forms the physical foundation. 

Small interactive elements like buttons, badges, chips, and quick-filter pills utilize full pill radii (`9999px`) to reinforce the tactile, soft-touch clay feel. Cards and data widgets feature `1.25rem` (`20px`) rounded geometry, allowing liquid glass backdrops to frame internal elements with smooth corner fluidity.

## Components

### Buttons
- **Primary:** Warm citrus background (`#f97316`) with an inset top highlight (`inset 0 1px 0 rgba(255, 255, 255, 0.35)`), rounded pill geometry, crisp white label, and a citrus-tinted diffuse shadow (`0 8px 20px -4px rgba(249, 115, 22, 0.4)`).
- **Secondary Glass:** Translucent backdrop (`rgba(255, 255, 255, 0.8)`), 1px white border, charcoal text (`#0f172a`), subtle inner clay shadow on active/pressed states.
- **Tertiary/Ghost:** Borderless, deep slate text with a hover state activating a warm marigold-tinted ghost wash (`rgba(245, 158, 11, 0.1)`).

### Cards & Data Panels
Multi-layered frosted liquid surfaces: background `rgba(255, 255, 255, 0.75)`, `backdrop-filter: blur(14px)`, `border: 1px solid rgba(255, 255, 255, 0.8)`, and `box-shadow: inset 0 1px 2px rgba(255, 255, 255, 1), 0 12px 24px -6px rgba(15, 23, 42, 0.04)`. Header zones inside cards place category labels in subdued charcoal (`#64748b`) with balances in high-contrast `#0f172a`.

### Chips & Filters
Pill-shaped containers with a `28px` to `32px` height profile. Inactive chips use translucent white fill with subtle borders. Active chips adopt either soft mint tinting (`rgba(16, 185, 129, 0.12)` with `#047857` text) or citrus fill (`#f97316` with `#ffffff` text) depending on functional urgency.

### Input Fields
Inputs use a recessed clay treatment: `background: rgba(241, 245, 249, 0.7)`, `border: 1px solid rgba(203, 213, 225, 0.6)`, and `box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.04)`. On focus, the field transitions to pure white with an energized citrus outline (`border-color: #f97316`) and an outer diffuse glow (`0 0 0 3px rgba(249, 115, 22, 0.15)`).

### Checkboxes & Radio Buttons
Smooth rounded squares (checkboxes) and circles (radios) with a 20px footprint. Checked state fills with fresh emerald mint (`#10b981`), sporting a centered white micro-glyph and a light emerald shadow.

### Lists & Ledger Rows
Alternating row states are avoided in favor of clean white translucent list strips separated by hairline dividers (`rgba(226, 232, 240, 0.6)`). Hover interactions gently elevate the item via `transform: translateY(-1px)` accompanied by an increase in card surface opacity.

### Financial Indicator Badges
Compact status capsules pairing a colored dot indicator with monospace numerical outputs (`JetBrains Mono`). Positive yields display fresh mint (`#10b981`), dynamic notifications display marigold (`#f59e0b`), and critical alerts display citrus red-orange (`#ea580c`).