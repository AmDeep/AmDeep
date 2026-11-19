# Install / Update this profile

1. **Backup** (optional): clone your current `AmDeep/AmDeep` repo.
2. Unzip this package **over** a fresh clone (or existing) of `https://github.com/AmDeep/AmDeep`.
   - It replaces `README.md`, adds/updates `scripts/build_profile.py`, workflows, and the `profile/` folder.
3. Delete any leftover root-level `*.svg` files that are now inside `profile/` (optional cleanup).
4. Commit and push to `main`:
   ```bash
   git add .
   git commit -m "feat: enhanced animated + data-driven profile"
   git push
   ```
5. **Repo Settings → Actions → General → Workflow permissions** → enable **Read and write permissions**.
6. Go to the **Actions** tab:
   - Run **Refresh profile** (generates live SVGs into `profile/`).
   - Run **Generate contribution snake** (creates the snake on the `output` branch).
7. Wait ~1–2 minutes, refresh your profile page. The data-driven cards, universe plot, insights, skyline, and snake will populate.

### Notes
- All custom SVGs are regenerated from public GitHub data (no private tokens required beyond the default GITHUB_TOKEN).
- External widgets (stats, streak, typing SVG, skill icons, visitor counter) update in real time.
- The color palette matches the existing teal/amber dark theme (`#5CC8C0`, `#0E1621`, etc.).
