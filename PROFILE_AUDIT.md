# AmDeep profile audit and implementation notes

## What was checked

The public `AmDeep/AmDeep` repository, its profile README, generated SVGs, Python generators, tests, and GitHub Actions workflow were reviewed. The six highlighted repositories were also checked against their README descriptions so that project claims in the replacement remain within the evidence those repositories publish.

## Confirmed discrepancies

1. **Three visuals literally displayed a waiting state.** `profile/activity.svg`, `profile/insights.svg`, and `profile/universe.svg` each said “Waiting for the first data refresh: run the Actions workflow.” The README embedded the activity and insights assets, so they could render as empty dashboards.
2. **The contribution skyline presented a false zero state.** `profile/skyline.svg` said “0 contributions in the last year” and showed zero streak/activity values. The generator's GraphQL fallback could preserve stale output or render zero-shaped data when contribution data was unavailable; those numbers were not safe to present as a measured result.
3. **The snake image had no active producer.** The README referenced `output/github-snake.svg` and `output/github-snake-dark.svg`, but the repository had no `output/` assets. `snake.yml` was at the repository root rather than `.github/workflows/`, so GitHub Actions would not run it as a workflow.
4. **The visible stats path and the updating workflow disagreed.** The only active workflow was `.github/workflows/auto-update-metrics.yml`; it generated `assets/metrics.svg`. The README did not embed that file and instead used third-party stats, streak, activity-graph, profile-view, typing, and icon services. The activity-graph endpoint returned “This deployment is temporarily paused” during this audit.
5. **The generator and test files were duplicated.** Root-level and `scripts/` copies of `build_profile.py`, `render_metrics.py`, and the metrics tests were byte-for-byte identical. The existing test suite passed three tests, but none exercised the main profile generator or checked that every README image existed.
6. **The profile spent space on unreliable/low-signal widgets.** It repeated broad tool lists and multiple charts, while the most verifiable evidence was in six project repositories. The revised README leads with the projects and the engineering decisions those repositories demonstrate.
7. **Public contact details are incomplete.** The public account metadata had no bio or website URL, and the repository contained no verified LinkedIn or email link. The replacement therefore does not invent contact information. A suggested short account bio is included below for manual use if desired.

## What the replacement changes

- Rebuilds the profile as a short, proof-led review path: a clear role, six evidence-based project cards, engineering approach, current repository signals, and links to the source.
- Removes the unsupported contribution-count graphic, inactive snake reference, and third-party widgets rather than displaying stale, zero, or externally hosted results.
- Adds self-hosted SVGs with accessible titles/descriptions and reduced-motion fallbacks. The checked-in SVGs render immediately; the metrics SVG is regenerated from GitHub public repository metadata.
- Adds a separate responsive dashboard with animated project cards, search and filters, repository sorting, a recent-push selector, language mix, and a 12-month chart. Chart code is lazy-loaded and split from the first page bundle.
- Keeps portfolio claims scoped to documented repository contents. The 12/15/12 figures are counts of documented labs/projects/stages, not deployment, usage, or business-impact metrics.
- Adds Python data/SVG tests and React interaction tests, plus CI validation for the generated README, dashboard, and production build.

## Live-data behavior and limits

- The scheduled workflow polls GitHub every five minutes for owned, public, non-fork repositories. A source-repository push is reflected after the next successful poll; a repository-dispatch event can start a refresh sooner when the optional notifier is installed.
- GitHub Actions schedule times are not guaranteed to start exactly on the cron minute, and queues/CDN propagation add latency. This is near-real-time, not an instantaneous guarantee.
- Only commits pushed to GitHub are visible. Local, unpushed edits are not observable.
- The refresh script filters private repositories and forks, requests public repository metadata only, and fails closed on API errors or missing featured repositories instead of publishing fake zero values.
- It compares the new snapshot with the previous snapshot. When neither the data nor generated files changed, it does not write a commit or rebuild/deploy the dashboard.
- The README’s raw SVG URL receives a snapshot version query when data changes. The React dashboard consumes the generated JSON snapshot and is deployed to GitHub Pages after a successful change.
- To publish the dashboard, enable **Settings → Pages → Build and deployment → GitHub Actions** in the profile repository once. The deployment workflow then builds `site/` and publishes the static artifact.
- For a faster push-triggered refresh, copy `integrations/notify-profile.yml` to `.github/workflows/notify-profile.yml` in each source repository that should notify the profile. Add an Actions secret named `PROFILE_UPDATE_TOKEN` in that source repository. The fine-grained token should be limited to `AmDeep/AmDeep` with the `Contents: write` permission required by GitHub’s repository-dispatch endpoint. The payload contains only the generic event type, not the source repository name or commit.
- The optional notifier is not required for automatic updates; the five-minute poll covers all public repositories. The profile workflow uses its repository-scoped `GITHUB_TOKEN` to update generated files and publish Pages.

## Dashboard stack and interaction

The dashboard is a static client-side app; it does not run JavaScript inside the GitHub profile README itself. It uses React 19.3.0, TypeScript 7.0.2, Vite 8.4.0, Recharts 3.11.1 for data visuals, Motion 14.14.0 for restrained transitions, and Lucide React 1.81.0 for interface icons. Vitest 5.1.0 and Testing Library cover core interactions. Versions are locked in `site/package-lock.json`.

The layout is original, not copied from another developer. It follows broadly useful portfolio patterns—specific positioning, selected work before an exhaustive project list, and direct evidence links—while using a different visual system. Motion respects `prefers-reduced-motion`; charts are code-split so they do not inflate the initial JavaScript chunk.

## Evidence used for project descriptions

- `AIAgents`: README describes 12 independently packaged Python labs with tests, architecture notes, and demo evidence.
- `RAGSystemLabs`: README describes 15 focused projects, local fixtures, tests, and injectable hosted/model dependencies.
- `inference-serving-portfolio`: README describes a 12-stage portfolio with reproducible experiments, serving patterns, benchmark evidence, assumptions, and limitations.
- `ros2-vllm-navigation-bridge`: README describes vLLM mission interpretation into structured waypoints and a deterministic local controller with bounded `Twist` output and replay checks.
- `manipulation-vllm-safety-gateway`: README describes validating proposed joint targets and rejecting invalid targets while keeping actuator limits deterministic.
- `edge-vision-vllm-inspector`: README describes capture metadata, robot state, optional semantic interpretation, and offline replay.

## Suggested GitHub account bio

`Applied AI engineer | Retrieval, agents & robotics | Toronto`

This is a suggestion only; changing the account bio is a separate profile-settings action and is not part of these repository files.

## References

- GitHub Docs, “Using your GitHub profile to enhance your resume”: https://docs.github.com/en/account-and-profile/tutorials/using-your-github-profile-to-enhance-your-resume
- GitHub Docs, “Managing your profile README”: https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme
- GreatFrontEnd, “Frontend Developer GitHub Profile: How to Stand Out to Recruiters (2026)”: https://www.greatfrontend.com/blog/frontend-developer-github-profile
- MDN, `prefers-reduced-motion`: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion

### Additional implementation sources

- GitHub Docs, `repository_dispatch` events and schedule behavior: https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows
- GitHub Docs, repository dispatch REST API and fine-grained token permissions: https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event
- GitHub Docs, custom workflows for GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- Brittany Chiang’s portfolio, used as a hierarchy/clarity reference (not a visual template): https://brittanychiang.com/
- GreatFrontEnd portfolio guidance: https://www.greatfrontend.com/blog/frontend-developer-github-profile
- React documentation, versions: https://react.dev/versions
