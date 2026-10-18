# Design Foundation &bull; Academic Work Tool

## 1. Design Philosophy

The **University Learning & Internship Platform** is designed as a calm, focused academic work tool, not a marketing website. The aesthetic prioritizes legibility, information density, and functional restraint.

- **Light Theme Only**: High clarity, paper-like contrast.
- **No Marketing Fluff**: No hero banners, glowing cards, blurred backgrounds, or decorative badges.
- **Academic Restraint**: Strict 1px borders, flat surfaces, zero gradients.

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
- **Body Sizing**: 15px base with 1.5 line height.
- **Line Length**: Body paragraphs and descriptive labels are constrained to under 80 characters (`max-w-[75ch]`) to maintain comfortable reading ergonomics.
- **Tabular Numerals**: Tabular figures (`.tabular-nums` / `font-variant-numeric: tabular-nums`) are enforced on grades, dates, timestamps, ports, and numeric data.

---

## 4. Component Library (`src/components/ui/`)

All UI components are built in-house with zero external widget kits:

| Component | Variants / Options | Description |
| :--- | :--- | :--- |
| `Button` | `primary`, `secondary`, `quiet`, `danger` | 6px radius, 1px border, 150ms state motion, no hover-lift |
| `Badge` | `success`, `attention`, `error`, `neutral` | 4px radius, 1px border, sentence case, no pill shapes |
| `TextField` | `label`, `helperText`, `error` | Form input with 1px border and visible petrol focus ring |
| `Select` | `label`, `options`, `error` | Dropdown control styled to platform tokens |
| `Textarea` | `label`, `helperText`, `error` | Multi-line text field with 6px radius |
| `DataTable` | Generic rows with column definitions | 1px border table with sentence case headers and tabular nums |
| `EmptyState` | `title`, `description`, `action` | Guides users on what to do next when data is absent |
| `ErrorMessage` | `whatHappened`, `howToFix`, `action` | Explains what failed and provides exact steps to resolve |
| `Notice` | `info`, `attention`, `error` | Informational or attention banner with platform tints |
| `PageHeader` | `title`, `description`, `actions` | Top view header with sentence case and actions slot |
| `AppShell` | Left sidebar + Top bar + Main canvas | Responsive layout (min 360px wide) with academic hierarchy. Sidebar navigation is configured centrally via `src/config/navigation.ts`, displaying only existing routes |

---

## 5. Visual &amp; Interaction Rules

1. **Corner Radius**: `6px` on controls (buttons, inputs, cards) and `4px` on badges.
2. **Borders &amp; Shadows**: Strict 1px borders (`#D7DDDB`). Shadows are prohibited except for floating menus and dialog overlays (`shadow-menu`, `shadow-dialog`).
3. **Motion**: Transitions are restricted to 150ms for interactive state changes. Respects `prefers-reduced-motion`.
4. **Icons**: `lucide-react` used sparingly. No emojis.
5. **No Decorative Bloat**: No all-caps labels, no small eyebrow text above headings, no decorative pill badges, no hover-lift elevation effects.
6. **Accessibility**:
   - Focus rings: 2px solid petrol with 1px offset (`:focus-visible`).
   - Contrast: All text and border combinations strictly satisfy WCAG AA.
   - Viewport: Full functional responsiveness down to 360px mobile width.

---

## 6. Copy Rules

- **Sentence Case**: Standard capitalisation for all headings, labels, buttons, and badges (e.g., "System status", "Check again", "Core API").
- **Plain Verbs**: Clear, direct actions ("Save changes", "Check again") instead of vague marketing terms ("Submit", "Explore").
- **Error Clarity**: Errors must explicitly explain **what went wrong** and **how to fix it**.
- **No Placeholder Copy**: No placeholder, invented, or phase text anywhere in the UI (e.g. no mock academic terms, fictional environments, or phase badges). Navigation exclusively displays routes that actually exist via `frontend/src/config/navigation.ts`.

---

## 7. Page Layouts &amp; Routing

- **Root Redirect (`/`)**:
  - Has no page of its own. Unauthenticated users are sent to `/login`; authenticated users are sent to their role's home page via `getHomePath(role)` in `src/config/navigation.ts` (currently `/account` for all roles).
- **Public Authentication Pages (`/login`, `/register`)**:
  - Plain centered form on `bg-chalk` page background with a single card (`bg-surface`, 1px border `border-line`, rounded `rounded-control`).
  - No sidebar, navigation links, or decorative heroes.
  - Direct, sentence-case headings and plain actionable error notices.
  - Submit buttons display active progress states (`Signing in...`, `Creating account...`) and prevent double submission.
- **Authenticated Application Shell (`AppShell`)**:
  - Left navigation sidebar dynamically filtered according to the active user's role (`roles` configuration in `src/config/navigation.ts`).
  - Top header displays the active page title, current user's full name, role badge, and a quiet `Log out` action.
- **System Status (`/status`)**: Admin-only. Displays health-check results for the API server and database connection.
- **Route Authorization Guards**:
  - `ProtectedRoute`: Seamlessly redirects unauthenticated requests to `/login` preserving intended destination state.
  - `RoleRoute`: Renders a single access-denied message — heading "You don't have access to this page", description "This page is only available to [role names] accounts." (role names derived from the route's `allowedRoles`), and a "Go to your account" button.

