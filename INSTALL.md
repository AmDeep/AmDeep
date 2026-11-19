# Clean Deployment Instructions

This package has the **correct structure**:

```
AmDeep/
├── README.md                 ← uses absolute raw.githubusercontent.com URLs
├── profile/                  ← all custom SVGs live here
│   ├── hero.svg
│   ├── marquee.svg
│   ├── card-*.svg
│   ├── universe.svg
│   ├── insights.svg
│   ├── activity.svg
│   ├── skyline.svg
│   ├── toolbox.svg
│   ├── loop.svg
│   └── footer.svg
├── .github/workflows/
│   ├── refresh-profile.yml
│   └── snake.yml
└── INSTALL.md
```

### Steps to deploy

1. **Delete or move** any old root-level SVG files (hero.svg, marquee.svg, etc.) so they don't conflict.

2. Copy the contents of this ZIP into your `AmDeep/AmDeep` repository root.

3. Commit and push:
   ```bash
   git add .
   git commit -m "feat: clean animated profile with correct structure"
   git push origin main
   ```

4. **Enable write permissions for Actions**
   - Repository → Settings → Actions → General
   - Workflow permissions → **Read and write permissions**
   - Save

5. **Run the workflows once**
   - Go to the **Actions** tab
   - Run **Generate contribution snake**
   - Run **Refresh profile** (optional but recommended)

6. Hard-refresh your profile page (`Ctrl + Shift + R` or `Cmd + Shift + R`).

After this, the hero, marquee, project cards, stats, snake, and all visualizations should appear correctly.
