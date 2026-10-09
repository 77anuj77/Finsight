# FinSight - Design Documentation

## Visual Identity
**Theme:** Liquid Glass + Claymorphism  
**Version:** 2.0.0  
**Last Updated:** 2026-09-19

---

## Design Tokens

### Colors
```css
/* Glass Surface */
--glass-bg: rgba(255, 255, 255, 0.08);
--glass-border: rgba(255, 255, 255, 0.12);
--glass-highlight: rgba(255, 255, 255, 0.25);

/* Clay Surface */
--clay-bg: rgba(248, 250, 252, 0.95);
--clay-shadow-light: rgba(255, 255, 255, 0.8);
--clay-shadow-dark: rgba(140, 150, 160, 0.15);

/* Semantic */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-danger: #ef4444;
--color-info: #3b82f6;
```

### Typography
- **Font Family:** Plus Jakarta Sans
- **Display:** 48-60px, Bold, -0.02em tracking
- **Heading:** 28-36px, Bold
- **Body:** 14-16px, Regular
- **Caption:** 10-12px, Medium

### Spacing Scale
4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px, 96px, 128px

### Border Radius
- Small: 1rem
- Medium: 1.5rem
- Large: 2rem
- Pill: 9999px

---

## Component Library

### Glass Card
```jsx
<div className="glass-card">
  {/* Content */}
</div>
```
- Frosted translucent background
- Soft border highlight
- Gentle depth shadow
- Hover: slight elevation + border brighten

### Clay Button
```jsx
<button className="clay-btn-primary">
  Primary Action
</button>
```
- 3D puffy appearance
- Dual shadow (light top-left, dark bottom-right)
- Hover: lift effect
- Active: press effect

### Clay Input
```jsx
<input className="clay-input" placeholder="Enter value" />
```
- Inset shadow for depth
- Smooth focus ring
- Soft rounded corners

### Glass Modal
```jsx
<div className="glass-modal">
  {/* Modal content */}
</div>
```
- Heavy backdrop blur
- Translucent white background
- Soft border glow

---

## Animation Guidelines

### Scroll Reveal
Elements animate in as they enter viewport:
- Fade from opacity 0 → 1
- Translate Y: 24px → 0
- Blur: 4px → 0
- Duration: 800ms
- Easing: `cubic-bezier(0.32, 0.72, 0, 1)`

### Hover States
- Transform: `translateY(-2px)`
- Shadow: increase depth
- Duration: 400ms
- Easing: `cubic-bezier(0.32, 0.72, 0, 1)`

### Click/Active States
- Transform: `scale(0.98)`
- Shadow: reduce depth
- Duration: 200ms

---

## Accessibility

### Focus States
- Visible ring: 2px solid primary color at 30% opacity
- Offset: 2px from element edge
- Duration: 200ms

### Reduced Motion
Respects `prefers-reduced-motion`:
- Disables all animations
- Sets transition duration to 0.01ms
- Maintains visual hierarchy without motion

### Contrast Ratios
- Text on glass: 4.5:1 minimum
- Text on clay: 7:1 minimum
- Interactive elements: 3:1 minimum

---

## Performance Notes

### GPU-Accelerated
- All animations use `transform` and `opacity`
- No layout-triggering properties animated
- `will-change` applied sparingly

### Backdrop Blur
- Applied only to fixed/sticky elements
- Not on scrolling containers
- Fallback: solid background color

### Asset Optimization
- SVG icons inline
- No external font files until needed
- Critical CSS inlined

---

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| Glass effects | 76+ | 103+ | 15.4+ | 79+ |
| Backdrop blur | 76+ | 103+ | 9+ | 79+ |
| CSS variables | 49+ | 31+ | 9.1+ | 15+ |
| Grid | 57+ | 52+ | 10.1+ | 16+ |

Graceful degradation for older browsers.

---

## Usage Examples

### Dashboard Page
```jsx
<div className="space-y-8">
  <h1 className="display-text">Dashboard</h1>
  
  <div className="grid grid-cols-4 gap-6">
    <KPICard title="Balance" value="₹25,000" />
    {/* More KPIs */}
  </div>
  
  <div className="glass-card p-6">
    {/* Chart or content */}
  </div>
</div>
```

### Form Modal
```jsx
<div className="fixed inset-0 z-50 flex items-center justify-center">
  <div className="absolute inset-0 glass-overlay" />
  <div className="relative w-full max-w-md glass-modal p-8">
    <h2 className="text-xl font-bold mb-6">Add Account</h2>
    <form className="space-y-5">
      <input className="clay-input" placeholder="Account name" />
      <button className="clay-btn-primary w-full">Create</button>
    </form>
  </div>
</div>
```

---

## Design Files

- **Figma:** [Link to be added]
- **Color palette:** See `tailwind.config.js`
- **Typography scale:** See `src/index.css`
- **Component library:** See `src/index.css` components section

---

*For questions or contributions, please refer to the main README.md*