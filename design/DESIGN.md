---
name: Midnight Financial Intelligence
colors:
  surface: '#111318'
  surface-dim: '#111318'
  surface-bright: '#37393e'
  surface-container-lowest: '#0c0e12'
  surface-container-low: '#1a1c20'
  surface-container: '#1e2024'
  surface-container-high: '#282a2e'
  surface-container-highest: '#333539'
  on-surface: '#e2e2e8'
  on-surface-variant: '#bacac5'
  inverse-surface: '#e2e2e8'
  inverse-on-surface: '#2f3035'
  outline: '#859490'
  outline-variant: '#3c4a46'
  surface-tint: '#3cddc7'
  primary: '#57f1db'
  on-primary: '#003731'
  primary-container: '#2dd4bf'
  on-primary-container: '#00574d'
  inverse-primary: '#006b5f'
  secondary: '#c0c1ff'
  on-secondary: '#1000a9'
  secondary-container: '#3131c0'
  on-secondary-container: '#b0b2ff'
  tertiary: '#d8dadc'
  on-tertiary: '#2d3133'
  tertiary-container: '#bcbec0'
  on-tertiary-container: '#4a4d4f'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#62fae3'
  primary-fixed-dim: '#3cddc7'
  on-primary-fixed: '#00201c'
  on-primary-fixed-variant: '#005047'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#111318'
  on-background: '#e2e2e8'
  surface-variant: '#333539'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 57px
    fontWeight: '700'
    lineHeight: 64px
    letterSpacing: -0.25px
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  headline-md:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  title-lg:
    fontFamily: Inter
    fontSize: 22px
    fontWeight: '500'
    lineHeight: 28px
  title-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '500'
    lineHeight: 24px
    letterSpacing: 0.15px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0.5px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0.25px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.1px
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.5px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  xxl: 48px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
---

## Brand & Style
The design system is engineered for a premium financial FAQ assistant, prioritizing authority, security, and high-performance clarity. The brand personality is "The Sophisticated Advisor"—expert, calm, and instantaneous. 

The visual style utilizes a **Modern Corporate** approach with a **Glassmorphic** infusion. It leans into deep, light-absorbing backgrounds to minimize eye strain during intensive data review, while using vibrant accents to highlight critical insights. The aesthetic is characterized by precision, utilizing strict alignment and high-contrast typography to ensure that complex financial information is digestible and trustworthy.

## Colors
This design system employs a deep, multi-layered dark palette to establish depth and hierarchy.

- **Primary (Vibrant Teal):** Reserved for primary actions, focus states, and successful financial trends. It provides a high-energy contrast against the midnight base.
- **Secondary (Indigo):** Used for secondary interactions, data visualization categories, and subtle branding elements.
- **Neutral/Surface:** The background architecture uses `#0A0C10` for the lowest layer, with `#161B22` and `#1D242E` used for elevated cards and containers to create a sense of physical stacking.
- **Functional Colors:** Error states should utilize a high-chroma red (#F43F5E) to ensure immediate visibility against the dark backdrop.

## Typography
The typography follows the MD3 (Material Design 3) scale, utilizing **Inter** for its exceptional legibility in data-heavy environments. 

- **Hierarchy:** Use `Display` and `Headline` roles for prominent financial figures and section headers. 
- **Readability:** `Body-lg` is the default for assistant responses to ensure comfort during long reading sessions.
- **Data Densitiy:** `Label` roles are utilized for metadata, timestamps, and table headers. 
- **Contrast:** Maintain a minimum contrast ratio of 7:1 for all body text against background surfaces to ensure premium accessibility.

## Layout & Spacing
This design system is built on a **strict 8dp grid**. All dimensions, padding, and margins must be multiples of 8px (or 4px for micro-adjustments).

- **Grid Model:** A 12-column fluid grid for desktop and a 4-column fluid grid for mobile.
- **Alignment:** Content should be centered in a max-width container of 1280px on large displays to prevent excessive line lengths in FAQ responses.
- **Rhythm:** Use `md` (16px) for internal component padding and `lg` (24px) for spacing between distinct content blocks.
- **Mobile Adaptations:** Gutters reduce to 16px on mobile devices to maximize horizontal real estate for text.

## Elevation & Depth
Elevation is expressed through **Tonal Layers** and **Subtle Glassmorphism** rather than heavy shadows.

- **Level 0 (Base):** `#0A0C10`. Used for the main application background.
- **Level 1 (Surface):** `#161B22`. Used for persistent sidebars or inactive cards.
- **Level 2 (Elevated):** `#1D242E`. Used for active FAQ cards and dialogue bubbles.
- **Overlays:** Use a 10% white tint "State Layer" on top of the surface color for hover states, and a 16% tint for pressed states.
- **Glass Effect:** For floating headers or navigation bars, use a background-blur of 12px with a 60% opacity fill of the surface color to maintain context of the content scrolling beneath.

## Shapes
The shape language combines structural stability with approachable softness.

- **Inputs & Search:** Use the "Pill-shape" (3) for all search bars and primary input fields to distinguish them as interactive entry points.
- **Action Elements:** Buttons and Chips also follow the pill-shaped convention.
- **Containers:** Large cards and modal dialogs should use `rounded-xl` (24px on desktop, 16px on mobile) to soften the professional tone.
- **Consistency:** Never mix sharp corners with rounded elements; the interface should feel cohesive and fluid.

## Components
- **Buttons:** Primary buttons are pill-shaped, filled with Teal (#2DD4BF), using Indigo text or black text for maximum legibility. Secondary buttons use a subtle Indigo outline.
- **Input Fields:** Search bars must be pill-shaped with a 1px border of `#30363D` and a subtle inner glow on focus using the Primary Teal color.
- **FAQ Cards:** Use the Level 2 surface. Title text should be `Title-lg` in Teal. Include a chevron icon for expandable sections that rotates 180 degrees on interaction.
- **Chips/Filters:** Small, pill-shaped tags used for categorizing financial topics (e.g., "Tax," "Investment," "Retirement"). Use an Indigo background at 15% opacity with solid Indigo text.
- **State Layers:** All interactive elements must have a fluid transition (200ms, ease-out) when changing states. Hover states should slightly increase the surface brightness rather than shifting the object's position.
- **Assistant Bubbles:** Distinguish assistant messages with a subtle Indigo border-left (4px) to provide a clear visual anchor for the AI's "voice."