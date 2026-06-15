# EdTech Weekly Report Generator — Web Version

A browser-based version of `edtech_analyzer.py`. Upload your weekly usage Excel
file(s), get the **exact same** interactive HTML report, charts, red flags,
insights, and multi-sheet Excel summary — with download buttons. Nothing is
uploaded to any server: the analysis runs entirely in your browser using
[Pyodide](https://pyodide.org) (your original Python, compiled to WebAssembly).

## What's inside

| File | Purpose |
|------|---------|
| `index.html` | The web page / UI |
| `app.js` | Loads Pyodide, runs the analysis, wires up downloads |
| `edtech_analyzer.py` | Your original script, used **unchanged** as the engine |
| `.nojekyll` | Tells GitHub Pages to serve files as-is |

The web app imports `edtech_analyzer.py` as a module and calls the same
functions your command-line tool uses (`load_data`, `build_html_report`,
`export_excel_summary`, the current-week variants, etc.), so the output is
identical.

## Run it online (GitHub Pages) — free, no server

1. Create a new repository on GitHub (e.g. `edtech-report`).
2. Upload **all files in this `webapp` folder** to the repo root
   (`index.html`, `app.js`, `edtech_analyzer.py`, `.nojekyll`).
   - Web upload: on the repo page → **Add file → Upload files** → drag them in → **Commit**.
   - Or with git:
     ```bash
     git init
     git add .
     git commit -m "EdTech report web app"
     git branch -M main
     git remote add origin https://github.com/<your-username>/edtech-report.git
     git push -u origin main
     ```
3. In the repo: **Settings → Pages**. Under **Build and deployment → Source**
   choose **Deploy from a branch**, pick branch `main` and folder `/ (root)`,
   then **Save**.
4. Wait ~1 minute. Your site will be live at:
   ```
   https://<your-username>.github.io/edtech-report/
   ```
   Share that link — anyone who opens it can upload a file and generate a report.

> If you put these files in a subfolder instead of the repo root, the URL becomes
> `https://<your-username>.github.io/edtech-report/webapp/`.

## Run it locally (optional)

Because Pyodide is fetched over the network, open it through a local server
(not by double-clicking the file):

```bash
cd webapp
python3 -m http.server 8000
# then open http://localhost:8000
```

## How to use

1. **Current week file** — required `.xlsx`.
2. **Previous week file** — optional; add it to unlock Week-on-Week comparison.
3. **Mode** — `Auto` (compare if a previous file is present, else current-week),
   `Compare`, or `Current week only`.
4. Click **Generate report**. First load takes ~10–20s while the Python engine
   downloads; after that it's fast.
5. Use **Download HTML report** / **Download Excel summary**, plus the
   per-section "Save as JPG" buttons inside the report itself.

No data file? Click **Try with demo data** to see a full sample report.

### Expected Excel columns

`username`, `district`, `s.name`, `Project Name`, `class`, `Total Usage`,
`Weekly Usage`, `Language_weekly`, `English_weekly`, `Math_weekly`, `CT_Weekly`,
`Lang PreciseLevel`, `Math Precise Level`, `English PreciseLevel`
(same format the desktop script expects).

## Notes

- Everything runs client-side; your spreadsheets never leave your computer.
- Keeping the report logic in `edtech_analyzer.py` means you maintain **one**
  codebase — update that file and both the desktop tool and this web app stay in sync.
- Requires a modern browser (Chrome, Edge, Firefox, Safari).
