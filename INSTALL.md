# Install

1. Unzip into a clone of `github.com/AmDeep/AmDeep` (merge over existing files).
2. Delete the old workflow that writes `assets/metrics.svg` (check `.github/workflows/`), and any old `assets/ai-ecosystem.svg`-generating step, so nothing overwrites the new files.
3. Commit and push to `main`.
4. In the repo: Settings > Actions > General > Workflow permissions > "Read and write permissions".
5. Actions tab > run **Refresh profile assets**, then run **Contribution snake** (this creates the `output` branch the snake image loads from).
6. Reload github.com/AmDeep. The project cards show "n/a" and 0 stars until step 5 has run.
