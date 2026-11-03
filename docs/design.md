# Design Foundation &bull; Academic Work Tool

## 1. Design Philosophy &amp; Brand Identity

The **University Learning & Internship Platform** is designed as a calm, focused academic work tool, not a marketing website. The aesthetic prioritizes legibility, information density, and functional restraint.

- **Light Theme Only**: High clarity, paper-like contrast.
- **No Marketing Fluff**: No hero banners, glowing cards, blurred backgrounds, or decorative badges.
- **Academic Restraint**: Strict 1px borders, flat surfaces, zero gradients.
- **Brand Identity (`Brand`)**:
  - Visible wordmark: **UNIVERSITY** in uppercase tracking (`tracking-wider`) styled in platform `ink` (`#1C2733`).
  - Subtitle tagline: **Learning & Internship Platform** styled in secondary `pencil` (`#5B6772`).
  - Shared component `src/components/ui/Brand.tsx` (`sm`, `md`, `lg` sizes) mounted on headers, drawer, login, register, and error views.
  - Browser tab title standard: `[Page Title] - UNIVERSITY` via `usePageTitle`.

---

## 2. Color Palette &amp; Design Tokens

The Tailwind configuration replaces default color scales with this dedicated token set:

| Token | Hex Value | Purpose / Usage |
| :--- | :--- | :--- |
| `chalk` | `#F3F5F4` | Global page background |
| `surface` | `#FFFFFF` | Cards, tables, controls, and panel backgrounds |
| `ink` | `#1C2733` | Primary body and heading text (high contrast, WCAG AA) |
| `pencil` | `#5B6772` | Secondary text, column headers, metadata, helper text |
| `line` | `#D7DDDB` | 1px borders, table dividers, control outlines |
| `petrol` | `#14565F` | Primary interactive color (buttons, focus rings) |
| `petrol-hover` | `#0F4249` | Interactive hover state |
| `petrol-tint` | `#E3EEEF` | Active navigation items, selected row highlights |
| `marigold` | `#E0A526` | Attention, pending states, and deadlines only |
| `marigold-tint`| `#FBF1D6` | Attention banner backgrounds and warning badges |
| `moss` | `#2F7D52` | Success status indicators and operational badges |
| `brick` | `#B23A2E` | Error status, alert messages, and destructive actions |

> **Prohibition**: Default Tailwind color classes (`indigo`, `blue`, `slate`, `gray`, `zinc`, etc.) are not used in application code.

---

## 3. Typography &amp; Numerals

- **Typeface**: **IBM Plex Sans** (weights 400, 500, 600) self-hosted via `@fontsource/ibm-plex-sans`. No third-party font CDNs.
- **Body Sizing**: 15px base with 1.5 line height. Form controls use `text-[16px]` to prevent mobile iOS viewport auto-zoom.
- **Line Length**: Body paragraphs and descriptive labels are constrained to under 80 characters (`max-w-[75ch]`) to maintain comfortable reading ergonomics.
- **Tabular Numerals**: Tabular figures (`.tabular-nums` / `font-variant-numeric: tabular-nums`) are enforced on grades, dates, timestamps, ports, and numeric data.

---

## 4. Component Library (`src/components/ui/`)

All UI components are built in-house with zero external widget kits:

| Component | Variants / Options | Description |
| :--- | :--- | :--- |
| `Brand` | `sm`, `md`, `lg` | Unified platform wordmark and subtitle lockup |
| `Button` | `primary`, `secondary`, `quiet`, `danger` | 6px radius, 1px border, 150ms state motion, min 44px touch targets |
| `TextLink` | `to`, `href`, `children` | Accessible styled text navigation link with petrol underline |
| `IconButton` | `icon`, `aria-label`, `quiet` | 44px min touch target square button with accessible label |
| `Card` | `interactive`, `to`, `children` | Surface container; link-wrapped with border highlight when interactive |
| `BackLink` | `fallbackTo`, `label` | Contextual back navigation with history fallback |
| `Badge` | `success`, `attention`, `error`, `neutral` | 4px radius, 1px border, sentence case, no pill shapes |
| `TextField` | `label`, `helperText`, `error` | Form input with 1px border, petrol focus ring, and 16px font |
| `Select` | `label`, `options`, `error` | Dropdown control styled to platform tokens with 16px font |
| `Textarea` | `label`, `helperText`, `error` | Multi-line text field with 6px radius and 16px font |
| `DataTable` | Generic rows with column definitions | 1px border table with container scrolling and tabular numerals |
| `EmptyState` | `title`, `description`, `action` | Guides users on what to do next when data is absent |
| `ErrorMessage` | `whatHappened`, `howToFix`, `action` | Explains what failed and provides exact steps to resolve |
| `Notice` | `info`, `attention`, `error` | Informational or attention banner with platform tints |
| `PageHeader` | `title`, `description`, `actions` | Top view header with sentence case and actions slot |
| `AppShell` | Left sidebar + Top bar + Main canvas | Responsive shell with drawer, focus trap, and safe area insets |

---

## 5. Visual &amp; Interaction Rules

1. **Corner Radius**: `6px` on controls (buttons, inputs, cards) and `4px` on badges.
2. **Borders &amp; Shadows**: Strict 1px borders (`#D7DDDB`). Shadows are prohibited except for floating menus and dialog overlays (`shadow-menu`, `shadow-dialog`).
3. **Interactive Affordances**:
   - Every interactive element has a visible default visual cue (borders or fills on buttons; underline on text links; cursor-pointer).
   - Hover state: 150ms transition to hover token (`bg-petrol-hover` or `text-petrol-hover`).
   - Active state: Pressed feedback via subtle scale (`active:scale-[0.99]`).
   - Focus ring: 2px solid petrol with 1px offset (`:focus-visible`).
   - Disabled state: Clear `cursor-not-allowed` and reduced opacity or muted background.
   - Guarded by `affordance-guard.test.ts` ensuring no unstyled raw `<button>` or `<a>` elements outside shared UI components.
4. **Motion**: Transitions restricted to 150ms. Respects `prefers-reduced-motion`.
5. **Icons**: `lucide-react` used sparingly. No emojis.
6. **No Decorative Bloat**: No all-caps labels, no small eyebrow text above headings, no decorative pill badges, no hover-lift elevation effects.

---

## 6. Back Navigation Rules

1. **Placement**: Detail views, creation/editing forms, report views, and notification center feature a `BackLink` above the view header.
2. **Behavior**:
   - If browser history within the app exists (`canGoBack` / `history.state.idx > 0`), clicking triggers `navigate(-1)`.
   - If user landed directly on the page, it resolves to the deterministic parent view via `resolveBackTarget(pathname)` in `src/config/navigation.ts`.
3. **Touch Targets**: Guaranteed minimum 44px touch target height with visible chevron and underline on hover.

---

## 7. Mobile &amp; Responsive Layout Rules (Down to 360px)

1. **Zero Horizontal Overflow**: `scrollWidth <= window.innerWidth` verified at 360px, 390px, 768px, and 1440px via Playwright tests.
2. **Navigation Drawer**:
   - Accessible hamburger toggle with min 44px hit target.
   - Dimmed backdrop overlay (`bg-ink/40`).
   - Trapped keyboard focus within drawer when open.
   - Body scroll locked (`document.body.style.overflow = 'hidden'`).
   - Dismisses cleanly on Escape key, outside click, close button, or link navigation.
   - Respects mobile safe area insets (`env(safe-area-inset-top)` / `bottom`).
3. **Mobile Form Ergonomics**:
   - All input fields, selects, and textareas enforce minimum 16px font size to prevent iOS Safari auto-zoom on focus.
   - Form action button bars stack vertically (primary submit full-width on top, secondary/cancel below).
   - Radio buttons and checkboxes feature min 44px touch target tap areas.
4. **Modal Dialogs as Bottom Sheets**:
   - Modals align as bottom sheets on screens < 640px (`items-end`, `rounded-t-xl`, full width).
   - Include visible close button and handle Escape key dismissal.
5. **Data Tables &amp; Stat Strips**:
   - Tables provide container scrolling (`overflow-x-auto overscroll-x-contain`) with clear borders.
   - Stat strips stack vertically on small screens (`grid-cols-1 md:grid-flow-col divide-y md:divide-y-0 md:divide-x`).

---

## 8. Copy Rules

- **Sentence Case**: Standard capitalisation for all headings, labels, buttons, and badges (e.g., "System status", "Check again", "Core API").
- **Plain Verbs**: Clear, direct actions ("Save changes", "Check again") instead of vague marketing terms ("Submit", "Explore").
- **Error Clarity**: Errors must explicitly explain **what went wrong** and **how to fix it**.
- **No Placeholder Copy**: Navigation exclusively displays routes that actually exist via `src/config/navigation.ts`.

---

## 9. Page Layouts &amp; Routing

- **Root Redirect (`/`)**: Unauthenticated users redirect to `/login`; authenticated users redirect to role dashboard via `getHomePath(role)`.
- **Authentication Pages (`/login`, `/register`)**: Centered form with `Brand` lockup, clear notices, and progress indicators.
- **Authenticated Shell (`AppShell`)**: Responsive sidebar or drawer with role-filtered links, user header, and notifications bell.
- **Route Authorization**: `ProtectedRoute` and `RoleRoute` with explicit access-denied message and navigation back to account.
