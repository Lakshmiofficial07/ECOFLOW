# EcoFlow AI Design System Specification

This document serves as the single source of truth for the design system of EcoFlow AI, based on the Google Stitch exported screens. It outlines the color palettes, typography, spacing scales, gradients, and key UI component patterns.

---

## 1. Color Palette

### Base & Backgrounds
* **Warm Cream**: `#F6F5EF` — Primary background (Landing, Login right panel, Citizen main area)
* **Pure White**: `#FFFFFF` — Card backgrounds, input fields
* **Off-White Warm**: `#EAE8E2` — Secondary beige accents, tab containers
* **Deep Forest Green**: `#064E3B` — Hero sections, login left panel
* **Admin Dark BG**: `#0D1C16` — Admin dashboard deep background
* **Admin Card BG**: `#152A20` — Admin stat cards, dark panels

### Brand Colors (Green Spectrum)
* **Primary Emerald**: `#10B981` — Buttons, active states, progress bars, CTA
* **Forest Green**: `#047857` — Text headings, link accents
* **Deep Emerald**: `#064E3B` — Large heading text, card titles
* **Muted Mint**: `#A7F3D0` — Light borders, soft highlights
* **Soft Green Accent**: `#E6F4EA` — Pill badges, icon backgrounds, light success states
* **Teal Accent**: `#0D9488` — Chart accents, secondary data colors

### Status Colors
* **Success Green**: `#10B981` / bg: `#ECFDF5`
* **Warning Amber**: `#F59E0B` / bg: `#FFFBEB`
* **Error Rose**: `#EF4444` / bg: `#FEF2F2`
* **Info Blue**: `#3B82F6` / bg: `#EFF6FF`

### Severity Badge Colors
* **HIGH**: bg `#EF4444`, text `#FFFFFF`
* **MED**: bg `#F59E0B`, text `#FFFFFF`
* **LOW**: bg `#10B981`, text `#FFFFFF`

### Text Colors
* **Primary Dark Slate**: `#0F172A` — Main body text
* **Secondary Slate**: `#334155` — Card body text
* **Muted Gray**: `#64748B` — Subtitles, helper text
* **Light Gray**: `#94A3B8` — Placeholder text
* **White**: `#FFFFFF` — Text on dark backgrounds
* **Emerald Text on Dark**: `#A7F3D0` — Subtitle text on green backgrounds

### Chart Colors
* **Collected (Line)**: `#10B981`
* **Predicted (Line)**: `#F59E0B`
* **Organic**: `#10B981`
* **Recyclable**: `#3B82F6`
* **Hazardous**: `#F59E0B`
* **Residual**: `#94A3B8`

---

## 2. Typography

* **Font Family**: `Geist` (primary), system sans-serif fallback
* **Headings**:
  * `h1`: 3rem–4.5rem (48–72px) | Weight: `800` (Extra Bold) | Tracking: `-0.025em`
  * `h2`: 1.5rem–2rem (24–32px) | Weight: `700` (Bold)
  * `h3`: 1.125rem–1.25rem (18–20px) | Weight: `600` (Semi Bold)
* **Body Text**:
  * Large: 1.125rem (18px) | Line-height: `1.75`
  * Base: 1rem (16px) | Line-height: `1.5`
  * Small: 0.875rem (14px) | Line-height: `1.5`
  * Extra Small: 0.75rem (12px) | Line-height: `1.4`
* **Stat Numbers**: 3.5rem–5rem (56–80px) | Weight: `800` | Tracking: `-0.02em`

---

## 3. Spacing & Layout Scale

* **Page max-width**: `max-w-7xl` (80rem / 1280px)
* **Container padding**: `px-6` (24px) to `px-8` (32px)
* **Section spacing**: `py-16` (64px) to `py-24` (96px)
* **Card padding**: `p-6` (24px) to `p-8` (32px)
* **Grid gaps**: `gap-4` (16px), `gap-6` (24px), `gap-8` (32px)
* **Component spacing**: `space-y-4`, `space-y-6`

### Border Radii
* **Hero section bottom**: `rounded-b-[3rem]`
* **Large cards / panels**: `rounded-3xl` (24px)
* **Medium cards**: `rounded-2xl` (16px)
* **Buttons / Inputs**: `rounded-2xl` (16px) or `rounded-full`
* **Small badges**: `rounded-lg` (8px) or `rounded-full`
* **Sidebar**: `rounded-r-[2.5rem]`

---

## 4. Gradients

### Hero Background
```css
background: linear-gradient(135deg, #064E3B 0%, #0D3B2E 40%, #0A4D3A 60%, #042F24 100%);
```
Plus an organic radial overlay:
```css
background-image: radial-gradient(ellipse at 70% 50%, rgba(13, 148, 136, 0.3) 0%, transparent 60%);
```

### CTA Button Gradient
```css
background: linear-gradient(135deg, #10B981 0%, #047857 100%);
```

### Sidebar Glassmorphism (Citizen)
```css
background: linear-gradient(180deg, rgba(6, 78, 59, 0.85) 0%, rgba(6, 78, 59, 0.65) 100%);
backdrop-filter: blur(24px);
```

### Admin Dark Gradient
```css
background: linear-gradient(180deg, #0D1C16 0%, #152A20 100%);
```

---

## 5. Component Patterns

### Navigation — Vertical Sidebar (Admin/Citizen)
* Width: `w-64` (256px)
* Background: glassmorphism (citizen) or solid dark (admin)
* Active item: Pill-shaped with `bg-white/15` or `bg-emerald-600/20`, white text
* Inactive item: `text-white/60`, hover `text-white`
* Items: icon (20px) + label, `py-3 px-4 rounded-2xl`
* Logo: Leaf icon + "EcoFlow AI" text at top

### Navigation — Horizontal Top Bar (HKS)
* Full-width, white background, bottom border
* Links: `text-slate-600 font-semibold`, active: `text-[#064E3B] font-bold border-b-2 border-[#10B981]`
* Logo left, nav items center

### Role Selector Tabs (Login)
* Container: `bg-[#EAE8E2]` beige, `rounded-full`, `p-1.5`
* Active tab: `bg-[#10B981]` emerald, white text, `rounded-full`
* Inactive tab: `text-slate-500`, hover `text-slate-800`

### Stat Cards
* Light mode: White background, subtle border, sparkline at bottom
* Dark mode (admin): `bg-[#152A20]` with emerald-tinted borders
* Metric: Large number + trend indicator (↑ or ↓) + percentage
* Label above, sublabel below

### Status Badges
* **Completed**: `bg-[#ECFDF5] text-[#10B981] border border-[#A7F3D0]`
* **In Progress**: `bg-[#EFF6FF] text-[#3B82F6] border border-[#93C5FD]`
* **Pending**: `bg-[#FFFBEB] text-[#F59E0B] border border-[#FCD34D]`

### Data Table (Admin Complaints)
* Header row: `bg-slate-50 text-slate-500 text-xs uppercase font-bold`
* Body rows: White background, bottom border
* Severity column: colored badge (HIGH=red, MED=amber, LOW=green)
* Action column: outlined buttons (`border border-slate-300 rounded-lg`)

### Upload Drop Zone
* `border-2 border-dashed border-[#10B981]/40`
* `rounded-2xl` with cloud upload icon centered
* Hover: border becomes solid `border-[#10B981]`

### Interactive Buttons
* **Primary CTA**: Gradient green, `rounded-2xl`, shadow, hover scale
* **Secondary**: `bg-white border border-slate-200`, slate text
* **Action (Table)**: `border border-slate-300 rounded-lg px-4 py-2 text-sm font-semibold`

### Floating Overlay Cards (HKS Map)
* `bg-white rounded-2xl shadow-xl p-4`
* Positioned absolutely over map viewport
* Semi-transparent backdrop on mobile

---

## 6. Shadows

* **Card shadow**: `shadow-lg` or `0 4px 20px rgba(0,0,0,0.06)`
* **Elevated card**: `shadow-xl` or `0 8px 30px rgba(0,0,0,0.08)`
* **Button shadow**: `shadow-md shadow-emerald-900/10`
* **Sidebar shadow**: `shadow-2xl`

---

## 7. Animation & Transitions

* **Card hover**: `hover:shadow-xl hover:scale-[1.02]` with `transition-all duration-300`
* **Button hover**: `hover:scale-[1.02] active:scale-[0.98]`
* **Page entry**: Framer Motion `fadeIn` + `slideUp` (y: 20 → 0, duration: 0.5s)
* **Staggered children**: 0.1s delay between sibling card animations
