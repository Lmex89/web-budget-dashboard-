---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, Apple/minimal (dark & white), etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Mobile-first**: Assume mobile is the primary canvas. All layouts must work and look considered on small screens first; desktop is the enhancement.
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

## Apple/minimal (dark & white)

When the user requests an Apple-like aesthetic with dark and white themes, apply these specific guidelines:

- **Typography**: San Francisco (system font on Apple devices) or SF Pro — crisp, clean, highly legible. For display text, use large, thin (200–300 weight) fonts with generous letter-spacing. Avoid serifs entirely.
- **Color**: Pure white (#fff) and near-black (#1d1d1f) as the two poles. Accent colors are used sparingly — typically one saturated hue (blue #0071e3 or a warm accent) for CTAs and links only.
- **Spacing**: Generous, almost architectural whitespace. Content feels airy and intentionally placed. Use multiples of 8px/16px for consistent rhythm.
- **Backgrounds**: Solid white in light mode, solid near-black in dark mode. Subtle frosted-glass effects (backdrop-filter: blur()) for overlays, modals, and nav bars. No gradients, no textures, no noise.
- **Borders & Shadows**: Hairline borders (0.5px or 1px) in light gray (#d2d2d7). Minimal, tight drop shadows for elevation. Corners are generously rounded (12–16px for cards, 8px for buttons).
- **Motion**: Slick, fast, and purposeful. 200–300ms ease-in-out transitions. Spring animations for interactive elements. Parallax and blur transitions between sections. Never bouncy or playful.
- **Layout**: Strict grid alignment, generous margins (16–20px on mobile), centered content. Single-column on mobile with full-width cards. No asymmetry that feels chaotic — controlled compositional tension only.

### Mobile-first specifics for Apple aesthetic
- Touch targets: minimum 44x44pt (Apple HIG guideline).
- Bottom-sheet patterns for actions and filters (native-feeling slide-ups).
- Safe area insets respected (env(safe-area-inset-*)) for notched devices.
- Thumb-friendly zones: primary actions in the lower third of the screen.
- Navigation: tab bar at bottom (system-like), never a hamburger menu on mobile.
- Gesture-driven: swipe-to-dismiss modals, pull-to-refresh, drag-to-reorder where appropriate.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
