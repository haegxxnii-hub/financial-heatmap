# Financial Heatmap

## GitHub Pages setup
1. Create a **public** GitHub repository and upload this folder's contents to repository root.
2. Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` → Save.
3. Actions → Update prices → Run workflow (run once to populate data).
4. Then visit `https://USERNAME.github.io/REPOSITORY/`.

Automatically updates at 08:30 KST Tuesday to Saturday (scheduled jobs can be delayed). Real market data are fetched via the unofficial Yahoo Finance source (`yfinance`), not guaranteed. Missing quotes display `--`. Market-cap-weighted returns use latest available market cap; this is not historical beginning-of-period index weighting. Stock prices use regular-session unadjusted close, excludes after-hours. Weekly return compares most recent close this week with previous week's last trading close. If no market session occurred yet this week, the weekly return calculation is based on previous week's last session and should not be used as this week's return. No API key required.
