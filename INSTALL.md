# Install

1. Unzip over a clone of `github.com/AmDeep/AmDeep` (merge, replace README.md).
2. Delete the old image folder `assets/` and any older workflows in `.github/workflows/` that write images, so nothing overwrites `profile/`.
3. Commit and push to `main`.
4. Repo Settings > Actions > General > Workflow permissions > "Read and write permissions".
5. Actions tab > **Refresh profile** > Run workflow. It fills `profile/` with live data from all your repos.
6. If an image looks broken, open `profile/<file>.svg` directly in the repo. If it 404s, the file did not get pushed.
