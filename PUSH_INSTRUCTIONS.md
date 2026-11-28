# Push this profile refresh

This archive contains a ready-to-copy repository tree. It has **not** been pushed to GitHub.

1. Unzip `AmDeep-profile-refresh.zip`.
2. In a clone of `https://github.com/AmDeep/AmDeep`, copy the contents of the extracted `AmDeep-profile-refresh/` folder into the repository root, replacing matching files.
3. Remove the legacy files listed in `LEGACY_FILES_TO_REMOVE.txt`. This is important: several old workflow files were at the repository root and were not active GitHub Actions workflows.
4. Use Python 3.12 and Node.js 24, then run the checks from the repository root:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 scripts/build_profile.py --check
   cd site
   npm ci
   npm test
   npm run build
   cd ..
   git diff --check
   ```

5. Review the generated README and SVGs in the GitHub preview. Then create a branch, commit, and push it using the repository's current contribution rules.

## Turn on the live dashboard

After pushing the files, open the profile repository’s **Settings → Pages → Build and deployment** and select **GitHub Actions** as the source. The refresh workflow deploys the dashboard to [https://amdeep.github.io/AmDeep/](https://amdeep.github.io/AmDeep/) after it detects changed data or profile content.

The dashboard reads a generated snapshot of owned public, non-fork repositories. A scheduled GitHub Actions workflow polls every five minutes, so new remote pushes are picked up automatically without editing every source repository. GitHub may delay scheduled jobs, so this is near-real-time rather than guaranteed instantaneous.

For a faster event-triggered refresh, copy `integrations/notify-profile.yml` into `.github/workflows/notify-profile.yml` in any source repository you want to notify the profile. In that source repository, add an Actions secret named `PROFILE_UPDATE_TOKEN`: use a fine-grained token scoped only to `AmDeep/AmDeep`, with the `Contents: write` permission required for the repository-dispatch API. Keep the token in GitHub Secrets; do not put it in a file or commit it. The notifier sends only the generic refresh event, not the source repo name or commit details.

The profile repository’s own refresh workflow uses its built-in `GITHUB_TOKEN` to commit changed metrics and deploy Pages. It has the explicit permissions needed for those actions. No external stats widget or runtime tracking service is used.

## Source of truth

Edit `profile-content.json`, then run `python3 scripts/build_profile.py`. Do not hand-edit generated `README.md` or project SVGs unless you also update the generator and regenerate the outputs. Repository metrics and dashboard data come from `scripts/fetch_profile_metrics.py`; the workflow runs it automatically.

The SVG image URLs use the `main` branch. If you rename the default branch, update `RAW_BASE` in `scripts/build_profile.py` and the `main` branch references in `.github/workflows/refresh-profile.yml`. If you rename the profile repository, also update `PAGES_URL` and `base` in `scripts/build_profile.py` and `site/vite.config.ts`.
