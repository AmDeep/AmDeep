# Deploy the high-impact animated profile

This package combines the strongest patterns from the best GitHub profiles in 2026:

- Animated typing identity
- Live stats + streak + activity graph
- Contribution snake (light/dark)
- Custom data-driven animated SVGs (hero, marquee, project cards, universe plot, insights, skyline, toolbox)
- Consistent premium dark teal theme
- Self-updating via GitHub Actions

### Deployment steps

1. **Push everything**
   ```bash
   git add .
   git commit -m "feat: cinematic animated profile with live metrics and data SVGs"
   git push origin main
   ```

2. **Enable Actions write access**
   - Repo → Settings → Actions → General
   - Workflow permissions → **Read and write permissions**
   - Save

3. **Run the workflows (required once)**
   - Actions → **Refresh profile** → Run workflow  
     (generates/updates all custom SVGs in `profile/`)
   - Actions → **Generate contribution snake** → Run workflow  
     (creates the snake on the `output` branch)

4. Hard-refresh your profile page (Ctrl+Shift+R / Cmd+Shift+R).

### What you should see after the workflows finish
- Fully animated hero banner
- Scrolling tech marquee
- Typing identity lines
- Live GitHub stats, languages, streak, activity graph
- Contribution snake
- Project cards that link to your featured work
- Repository universe visualization
- Insights, activity timeline, and contribution skyline
- Toolbox + skill icons

Everything updates automatically after the initial run.
