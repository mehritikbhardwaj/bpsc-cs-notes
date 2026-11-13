# STET / BPSC TRE – Computer Science Notes (Web)

Clean typed version of the 419-page handwritten STET/TRE CS notes as a single web page
with a full chapter/topic index, search, dark mode and mobile layout.

- `index.html` – the finished website (open it directly in a browser)
- `src/chapters/*.html` – content of each chapter (edit these)
- `src/template.html` – page layout, styles and script
- `src/build.py` – joins chapters + template into `index.html` and builds the index
- `vercel.json` – Vercel config (static site)

## Rebuild after editing a chapter
```bash
python3 src/build.py src/chapters index.html src/template.html
```

## Upload to GitHub
```bash
cd ~/Documents/personal/bpsc
git init && git add . && git commit -m "CS notes website"
gh repo create bpsc-cs-notes --private --source=. --push
# (or create an empty repo on github.com, then:)
# git remote add origin https://github.com/<your-username>/bpsc-cs-notes.git
# git branch -M main && git push -u origin main
```

## Deploy on Vercel
Option A – CLI (fastest):
```bash
npx vercel login
npx vercel --prod
```
Option B – Dashboard: vercel.com → Add New → Project → import the GitHub repo →
Framework preset "Other", no build command, output directory `.` → Deploy.
Every `git push` will then redeploy automatically.
