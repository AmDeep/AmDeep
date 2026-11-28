# Portfolio enhancement review

**Repository:** [AmDeep/AmDeep](https://github.com/AmDeep/AmDeep)  
**Research snapshot:** 2026-11-28  
**Purpose:** Make the profile easier for hiring managers and engineering leaders to evaluate, while keeping every claim tied to public evidence.

## Recommendation

Lead with a clear engineering focus, then let a reader inspect a few technically distinct projects without wading through activity widgets. The profile now does that through a concise hero, six repository-backed case studies, direct LinkedIn contact, and live repository signals later in the page.

There is no controlled evidence in the sources reviewed that a specific animation, library, or portfolio layout guarantees interviews or hiring. Treat the portfolio advice below as practitioner guidance and the public examples as references for information hierarchy—not as proof of conversion.

## Implemented

### Hiring-manager path

- Clear applied-AI positioning and direct LinkedIn contact at the top, in the hero, and in the closing contact area.
- Six case studies based on the project repositories' published READMEs. Each includes the design problem, relevant engineering evidence, a repository link, and a stated boundary or limitation.
- The project section comes before repository-activity metrics; metrics support the work rather than substitute for it.
- Project artwork is a set of distinct, inline technical diagrams for agent flow, retrieval, inference, robotics navigation, manipulation safety, and edge inspection—not repeated text banners.
- Decorative README SVGs no longer loop endlessly. The generated metrics chart uses a brief one-shot entry animation and respects reduced motion; website loops can be paused together and also honor `prefers-reduced-motion`.

### Interaction and usability

- `Ctrl/Cmd+K` opens a keyboard-operated command search for sections and projects; arrow keys move through matches and Enter opens the selection.
- Project case studies open in a dialog with a close control and detail view.
- Hero system stages filter the related work.
- Mobile users get a compact section menu rather than a crowded desktop navigation.
- Repository search exposes its result count, language filter, reset action, and a meaningful empty state.
- Readers can choose a recent-push time window, inspect the language distribution and 12-month activity chart, and pause/resume decorative motion.
- The chart module is lazy-loaded so it does not add its full weight to the first route load.

### Search and sharing

- The dashboard prerenders its page content into the initial HTML, rather than shipping an empty React root.
- Added canonical URL, Open Graph/Twitter metadata, a 1200×630 social card, `robots.txt`, sitemap, and a `Person` JSON-LD record.
- Structured profile data contains only details shown on the page or supplied by AmDeep. It is not a promise of richer search results or better ranking.

## Dynamic data: what “live” means here

The metrics come from GitHub's public repository metadata. The scheduled workflow checks every five minutes, and an optional repository-dispatch notifier can request a faster refresh. A source push is therefore not guaranteed to appear instantly: GitHub Actions scheduling/queue time, API availability, the generated-data commit, deployment, and CDN propagation can all add delay. This is a lightweight static snapshot—not a websocket, live GitHub event stream, or per-visitor API call.

This tradeoff avoids embedding a personal access token in the browser and avoids making every visitor consume GitHub API quota. The page reports repository activity, not deployments, users, business impact, or hiring outcomes.

## Package and capability review

| Capability | Status | Package or platform feature | Why |
|---|---|---|---|
| UI and component state | In use | React 19 | Supports the current interactive profile without adding a framework layer. |
| Type safety | In use | TypeScript 7 | Keeps the portfolio data and UI contracts explicit. |
| Build and static hosting | In use | Vite 8 + GitHub Pages | Produces a small static site that fits this profile's deployment model. |
| Motion | In use | Motion 14 (`motion/react`) | Existing package is enough for restrained page/project transitions and reduced-motion handling. |
| Charts | In use | Recharts 3 | Existing data charts are lazy-loaded and use the generated snapshot. |
| Icons | In use | Lucide React | Provides consistent interface icons without image dependencies. |
| Dialog | In use | Native HTML `<dialog>` | Provides a browser primitive for project details; adding Radix Dialog would duplicate this behavior. |
| Command search | In use | Small custom keyboard palette | This page has a short known set of section/project destinations; `cmdk` would add a dependency without a clear current benefit. |
| Browser-level and a11y checks | Optional next | `@playwright/test` + `@axe-core/playwright` | Useful if CI should test actual browser keyboard/focus behavior and detect common accessibility violations. Automated checks still require manual keyboard, contrast, zoom, and screen-reader review. Not installed in this refresh. |
| WebGL scenes / scroll hijacking | Not recommended | Three.js / React Three Fiber, GSAP, Lenis | A 3D scene or custom smooth-scroll system would increase bundle and interaction cost without adding evidence about the projects. |
| Remote-data cache | Not recommended now | TanStack Query / React Query | Visitors read a generated, versioned static snapshot; there is no live client API request to cache or refetch. |
| Metadata helper | Not recommended now | React Helmet | Metadata is static and already present in the HTML document, so a client-side metadata layer is unnecessary. |
| Dialog/command packages | Not recommended now | Radix Dialog, `cmdk` | The existing native dialog and focused, small command search meet the current use case; add a library only if requirements grow. |

**Recommendation:** do not add packages simply to make the stack sound advanced. The current dependencies support the requested profile. The only meaningful optional package group is browser + automated accessibility testing, when its CI runtime cost is acceptable.

## Further improvements that need evidence first

These are intentionally excluded rather than filled with invented facts or `UNKNOWN`/`TBD` placeholders:

- A résumé download needs a current résumé document that AmDeep approves for publication.
- Employment chronology, certifications, project impact, production usage, benchmark claims, and customer outcomes need verifiable source material.
- A code demo or video belongs on a project page only when the demo is safe, available, and accurately represents the repository.
- A public email address was not supplied; LinkedIn is the verified contact path.
- A hiring-conversion metric would require user research/measurement. Adding analytics without a clear need would collect data without proving that the design works better.

## Evidence and references

1. [Brittany Chiang's portfolio](https://brittanychiang.com/) — public example of concise positioning, selected work, and an inspectable portfolio structure. Used for hierarchy, not copied.
2. [Josh Comeau, “Building an Effective Dev Portfolio”](https://www.joshwcomeau.com/effective-portfolio) — practitioner guidance on a focused project highlight reel and useful project details.
3. [GitHub Docs, “Using your GitHub profile to enhance your resume”](https://docs.github.com/en/account-and-profile/tutorials/using-your-github-profile-to-enhance-your-resume) — guidance on pinned repositories and readable project documentation.
4. [Motion for React accessibility](https://motion.dev/docs/react-accessibility) — reduced-motion and accessible animation guidance.
5. [W3C WCAG 2.2, SC 2.2.2: Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) — criteria for controls over certain persistent moving content.
6. [web.dev, “Animations guide”](https://web.dev/articles/animations-guide/) — performance considerations for web animation.
7. [React, `prerender`](https://react.dev/reference/react-dom/static/prerender) — static prerendering for React content.
8. [Playwright, accessibility testing](https://playwright.dev/docs/accessibility-testing) — browser accessibility checks with `@axe-core/playwright` and the limits of automated tests.
9. [Radix UI Dialog](https://www.radix-ui.com/primitives/docs/components/dialog) — dialog alternative considered and not added because the current feature uses native `<dialog>`.

---

The case-study details and repository counts are based on the checked-in profile data and public project READMEs. They describe documented project scope; they do not imply deployments, customer usage, or measured business impact.
