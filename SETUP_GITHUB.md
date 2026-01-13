# GitHub Setup Instructions

## Step 1: Create the Repository on GitHub

Go to GitHub and create your repository with these settings:
- **Repository name**: `compute-demand-signals`
- **Description**: AI infrastructure demand signals from SEC filings
- **Visibility**: Public ✅
- **Add README**: NO (we already have one)
- **Add .gitignore**: NO (we already have one)
- **Add license**: Choose MIT License ✅

## Step 2: Push Your Code

After creating the repository, run these commands:

```bash
# Navigate to your project
cd "/Users/mattrobinson/Library/Mobile Documents/com~apple~CloudDocs/AI street/Projects/Claude Code/Compute Demand"

# Add the remote (replace YOUR_USERNAME with your actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/compute-demand-signals.git

# Push your code
git push -u origin main
```

## Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in the left sidebar)
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/reports`
4. Click **Save**

GitHub will build and deploy your site. After a few minutes, your site will be live at:
```
https://YOUR_USERNAME.github.io/compute-demand-signals/
```

## Step 4: Update README

Once your site is live, update the README with your actual URL:

```bash
# Edit README.md and replace the placeholder:
# [Your GitHub Pages URL will go here]
#
# With your actual URL:
# https://YOUR_USERNAME.github.io/compute-demand-signals/

git add README.md
git commit -m "Add live website URL to README"
git push
```

## Step 5: Set Up Automatic Updates (Optional)

To automatically update your website daily, create `.github/workflows/update-reports.yml`:

```yaml
name: Update Reports

on:
  schedule:
    - cron: '0 12 * * *'  # Daily at 12pm UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests beautifulsoup4 click lxml

      - name: Run pipeline
        run: |
          python -m aistreet run-all --since 90d

      - name: Commit and push if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add reports/*.html
          git diff --quiet && git diff --staged --quiet || (git commit -m "Update reports [automated]" && git push)
```

This will:
- Run daily at 12pm UTC
- Fetch new filings
- Extract signals
- Update all HTML reports
- Automatically push to GitHub Pages

## Troubleshooting

**Issue**: Permission denied when pushing
**Solution**: Make sure you're authenticated with GitHub. You may need to use a personal access token instead of password.

**Issue**: GitHub Pages not working
**Solution**:
1. Make sure the repository is public
2. Check that you selected `/reports` folder, not `/root` or `/docs`
3. Wait a few minutes for the initial deployment

**Issue**: Website shows 404
**Solution**: The URL should be `https://YOUR_USERNAME.github.io/compute-demand-signals/` (with trailing slash for the index page)

## Your Website Structure

Your live site will have these pages:
- `index.html` - Landing page with overview
- `calendar.html` - Interactive filing calendar
- `report.html` - Detailed signal analysis

All pages have clickable links to SEC filings!
