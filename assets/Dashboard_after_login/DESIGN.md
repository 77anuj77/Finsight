---
name: Luminous Optical Liquid
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464b'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777c'
  outline-variant: '#c6c6cc'
  surface-tint: '#5a5e69'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#181b25'
  on-primary-container: '#808390'
  inverse-primary: '#c3c6d3'
  secondary: '#006875'
  on-secondary: '#ffffff'
  secondary-container: '#00e3fd'
  on-secondary-container: '#00616d'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#07006c'
  on-tertiary-container: '#7073ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dfe2ef'
  primary-fixed-dim: '#c3c6d3'
  on-primary-fixed: '#181b25'
  on-primary-fixed-variant: '#434751'
  secondary-fixed: '#9cf0ff'
  secondary-fixed-dim: '#00daf3'
  on-secondary-fixed: '#001f24'
  on-secondary-fixed-variant: '#004f58'
  tertiary-fixed: '#e1e0ff'
  tertiary-fixed-dim: '#c0c1ff'
  on-tertiary-fixed: '#07006c'
  on-tertiary-fixed-variant: '#2f2ebe'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-hero:
    fontFamily: Geist
    fontSize: 56px
    fontWeight: '700'
    lineHeight: 64px
    letterSpacing: -0.035em
  display-hero-mobile:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.025em
  display-lg:
    fontFamily: Geist
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.025em
  display-lg-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  title-sm:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  body-base:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-bold:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  label-caps:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.08em
  stat-financial:
    fontFamily: Geist
    fontSize: 34px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.03em
  stat-delta:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: -0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 3rem
  gutter-mobile: 1rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system delivers an ultra-premium, ethereal luxury experience tailored for high-stakes institutional wealth intelligence and modern spatial computational finance. The aesthetic converges the physical precision of optical crown crystal, real-time 3D refraction from the modern WebGL ecosystem (`react-three-fiber`), and the weightless, ambient spatial computing clarity of VisionOS in an ethereal light mode.

The visual philosophy relies on:
- **Ethereal Liquid Glassmorphism**: Translucent, heavy-transmission substrates with high backdrop saturation and generous multi-tier blurs (24px–48px) floating over a luminous platinum-alabaster canvas.
- **Prismatic Dispersion & Chromatic Sheen**: Glancing specular highlights catching dynamic cyan (`#00E5FF`) and electric violet (`#8A2BE2`) refraction edges along curved bevels.
- **Executive Anchoring**: High-contrast, razor-sharp obsidian typography balancing weightless physical materials with decisive institutional authority and flawless data density.

## Colors

The palette balances ethereal light diffusion with high-contrast executive ink:

- **Primary (`#090d16`)**: Deep Obsidian Sapphire. Provides an authoritative anchor for primary typography, dominant execution triggers, and deep contrast grounding.
- **Secondary (`#00e5ff`)**: Electric Prismatic Cyan. Expresses active transmission vectors, focused controls, live telemetry markers, and specular highlight edges.
- **Tertiary (`#6366f1`)**: Refractive Indigo-Violet. Applied to synthetic derivatives, predictive risk envelopes, and secondary interactive accents.
- **Neutral (`#f8fafc`)**: Ethereal Alabaster. An eye-relaxing, light-scattering foundation devoid of sterile flat-white glare.
- **Glass Materials**: Base glass layers utilize `rgba(255, 255, 255, 0.68)` with specular top highlights (`rgba(255, 255, 255, 0.95)`) and subtle structural containment outlines (`rgba(203, 213, 225, 0.45)`).
- **Semantic Indicators**: Mint Emerald (`#059669`) denotes positive yields and capital inflow; Crimson Rose (`#e11d48`) manages drawdown and risk boundaries; Amber Glint (`#d97706`) flags latency and pending liquidity states.

## Typography

Typography establishes an unyielding sense of analytical command through clean neo-grotesque proportions.

- **Tabular Figures**: All financial stats, basis points, yields, and balance readouts must enforce `font-variant-numeric: tabular-nums` to eliminate layout jitter during live-tick WebSocket stream updates.
- **Display & Headlines**: Geist delivers tight, architectural geometry with deliberate negative tracking at display scales, echoing luxury watch faces and precision optics.
- **Body & Controls**: Inter serves running analytical commentary, audit logs, and form fields, ensuring effortless optical legibility through frosted liquid overlays.
- **Precision Eyebrows**: Metric descriptions, asset tickers, and time horizons enforce `label-caps` in uppercase styling with `+0.08em` tracking for a technical, fine-milled appearance.

## Layout & Spacing

The structural layout relies on a balanced 12-column responsive fluid grid operating on a foundational 4px/8px modular rhythm:

- **Desktop (1280px+)**: Multi-pane layout accommodating 3D WebGL topological surfaces, analytical inspector sidebars, and execution tables. Standard section gutters are `1.5rem` (24px) with expansive outer canvas margins of `3rem` (48px) to establish luxury breathing room.
- **Tablet (768px – 1279px)**: Dual-pane layout where 3D stages dock to the top viewport half and controls shift to modular scrollable glass trays.
- **Mobile (< 768px)**: Single-column linear layout with compressed `1rem` margins and gutters. Navigation collapses into a floating bottom pill island.
- **Internal Card Density**: Liquid glass cards feature generous inner padding (`space-lg` to `space-xl`), ensuring financial readouts never appear congested despite high density of data.

## Elevation & Depth

Visual hierarchy is communicated through optical refraction, layered transmission tiers, and dual directional specular borders rather than dark drop shadows:

- **Tier 0 (Base Canvas)**: Ethereal Alabaster (`#f8fafc`) with subtle ambient radial gradients in pale cyan and violet light cones.
- **Tier 1 (Surface Containers & Cards)**: Translucent glass membranes (`rgba(255, 255, 255, 0.68)`) with `backdrop-filter: blur(28px) saturate(190%)`. Layered with an inner fresnel glare (`box-shadow: inset 0 1px 1px 0 rgba(255, 255, 255, 0.95)`) and ultra-diffuse optical drop (`0 16px 36px -6px rgba(15, 23, 42, 0.04)`).
- **Tier 2 (Elevated Panels & Flyouts)**: Elevated glass slabs (`rgba(255, 255, 255, 0.84)` with `blur(36px)`) featuring chromatic aberration edge fringes: a top-left bevel glowing with soft specular cyan and a bottom-right rim refracting faint violet.
- **Tier 3 (Floating Spatial Docks & Active Modals)**: Floating crystalline capsules with 48px blur, suspended with an ethereal ambient glow (`0 20px 48px -8px rgba(99, 102, 241, 0.12), inset 0 1px 2px rgba(255, 255, 255, 1)`).
- **Specular Hairline Borders**: 1px gradient borders flowing from light-facing specular glints (`rgba(255, 255, 255, 0.95)`) to diffused slate edges (`rgba(203, 213, 225, 0.35)`).

## Shapes

The design language embodies organic fluidity sculpted with optical precision:

- Base elements (inputs, tooltips, nested modules) utilize standard rounded curvature (`0.5rem` / 8px).
- Primary containers, metrics tiles, and data cards feature soft liquid contours (`rounded-lg` at `1rem` / 16px to `rounded-xl` at `1.5rem` / 24px).
- Spatial navigation docks, floating segmented tabs, status indicators, and pill tags employ continuous curvature (`rounded-full`), reflecting molded liquid crystal lenses.

## Components

### Buttons
- **Primary Execution**: Deep Obsidian (`#090d16`) solid background with pure white typography, an internal 1px specular highlight along the upper lip (`inset 0 1px 0 rgba(255, 255, 255, 0.25)`), and smooth tactile micro-scale (`scale(0.985)`) on click.
- **Liquid Secondary**: Frosted white glass fill (`rgba(255, 255, 255, 0.72)` with 20px backdrop blur), dual specular border, and obsidian text. Hover activates a luminous electric-cyan rim reflection (`box-shadow: 0 0 16px rgba(0, 229, 255, 0.3)`).
- **Spatial Ghost**: Unfilled container with slate text transitioning to a faint iridescent wash (`rgba(0, 229, 255, 0.08)`) with cyan boundary glints upon focus or hover.

### Cards & Analytical Slabs
- Built from multi-layered liquid glass (`rgba(255, 255, 255, 0.72)`) with 28px blur, 24px border radius, and dual-layer gradient borders.
- Headers integrate an 11px uppercase tracking label alongside a pulsing live WebSocket telemetry dot. Numbers sit below in Geist bold tabular figures.

### Inputs & Controls
- **Refractive Text Inputs**: Sunken glass wells (`rgba(255, 255, 255, 0.5)`) that clarify to `rgba(255, 255, 255, 0.92)` upon interaction, accompanied by an iridescent cyan focus ring (`0 0 0 3px rgba(0, 229, 255, 0.22)`).
- **Checkboxes & Radios**: Crystalline square/circle toggles with 1px frosted specular borders. Active states fill with obsidian or electric cyan, displaying pure white glyphs.
- **Refractive Sliders**: Precision hairlines filled with cyan-to-violet linear gradients, traversed by a polished platinum bead thumb containing an internal specular light center.

### Chips & Status Badges
- Compact pill-shaped modules (`rounded-full`) with semi-transparent tinted backgrounds:
  - Alpha Gain: Emerald glass background (`#d1fae5` at 60% opacity) with `#059669` bold text.
  - Drawdown: Soft rose glass (`#ffe4e6` at 60% opacity) with `#e11d48` text.
  - Neutral / Horizon: Frosted platinum glass with slate metadata typography.

### Spatial Navigation Dock
- A floating, bottom-anchored or top-centered pill island crafted with 36px backdrop blur, containing tactile icon and text buttons. The active route is cradled inside a self-illuminating white optical capsule with a soft violet shadow aura.

### 3D Canvas Integration
- Dedicated viewports for `react-three-fiber` surfaces feature transparent backgrounds, allowing 3D models (IOR 1.52 crown glass, dynamic dispersion) to blend smoothly with the underlying alabaster plane while 2.5D glass HUD tiles float overhead.