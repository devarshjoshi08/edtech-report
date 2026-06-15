/* EdTech Weekly Report Generator — web front-end.
   Runs the original edtech_analyzer.py unchanged, in-browser, via Pyodide. */

const PYODIDE_VERSION = "v0.26.4";

let pyodide = null;
let lastHtml = null;          // string
let lastXlsx = null;          // Uint8Array
let lastHtmlName = "EdTech_Report.html";
let lastXlsxName = "EdTech_Summary.xlsx";

const $ = (id) => document.getElementById(id);
const statusEl = $("status");
const generateBtn = $("generateBtn");
const demoBtn = $("demoBtn");

function setStatus(msg, kind) {
  statusEl.style.display = "block";
  statusEl.className = kind || "";
  statusEl.innerHTML = (kind === "loading" || kind === undefined && msg.includes("…"))
    ? `<span class="spinner"></span>${msg}`
    : msg;
}
function busy(msg) {
  statusEl.style.display = "block";
  statusEl.className = "";
  statusEl.innerHTML = `<span class="spinner"></span>${msg}`;
}

// ── Python glue: mirrors main() in edtech_analyzer.py ────────────────────────
const GLUE = `
import edtech_analyzer as ea
from datetime import datetime

def run_report(current_path, previous_path, mode, report_date):
    if not report_date:
        report_date = datetime.now().strftime("%d %B %Y")
    if mode == "auto":
        mode = "compare" if previous_path else "current"
    if mode == "compare" and not previous_path:
        mode = "current"

    curr_df = ea.load_data(current_path)
    prev_df = None
    if mode == "compare" and previous_path:
        prev_df = ea.load_data(previous_path)
        curr_df, prev_df = ea.filter_common_students(curr_df, prev_df)

    html_path = "/report.html"
    xlsx_path = "/summary.xlsx"

    if mode == "current":
        ea.build_html_report_current_only(curr_df, report_date, html_path)
        kpis = ea.compute_kpis(curr_df)
        flags = ea.find_red_flags(curr_df, None)
        insights = ea.generate_current_week_insights(curr_df)
        ea.export_excel_summary_current_only(curr_df, kpis, flags, insights, report_date, xlsx_path)
    else:
        ea.build_html_report(curr_df, prev_df, report_date, html_path)
        kpis = ea.compute_kpis(curr_df)
        deltas = ea.compute_delta(kpis, ea.compute_kpis(prev_df)) if prev_df is not None else None
        flags = ea.find_red_flags(curr_df, prev_df)
        ea.export_excel_summary(curr_df, prev_df, kpis, deltas, flags, report_date, xlsx_path)

    safe = report_date.replace(" ", "_").replace(",", "")
    suffix = "_CurrentWeek" if mode == "current" else ""
    return [mode, "EdTech_Report" + suffix + "_" + safe + ".html",
            "EdTech_Summary" + suffix + "_" + safe + ".xlsx"]

def make_demo():
    ea.generate_demo_data("/demo_current.xlsx", "/demo_previous.xlsx")
    return ["/demo_current.xlsx", "/demo_previous.xlsx"]
`;

// ── Init Pyodide ─────────────────────────────────────────────────────────────
async function init() {
  try {
    busy("Loading Python engine (one-time, ~10–20s)…");
    pyodide = await loadPyodide({
      indexURL: `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`,
    });

    busy("Loading data libraries (pandas, matplotlib)…");
    await pyodide.loadPackage(["pandas", "numpy", "matplotlib", "Pillow", "micropip"]);

    busy("Installing openpyxl…");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("openpyxl");

    busy("Loading the analysis script…");
    const code = await (await fetch("edtech_analyzer.py")).text();
    pyodide.FS.writeFile("edtech_analyzer.py", code);
    pyodide.runPython("import edtech_analyzer");   // imported as module → main() does NOT run
    pyodide.runPython(GLUE);

    setStatus("✅ Engine ready. Upload a file and click Generate, or try the demo data.", "ok");
    generateBtn.disabled = false;
    generateBtn.textContent = "⚡ Generate report";
    demoBtn.disabled = false;
  } catch (err) {
    setStatus("❌ Failed to load the engine: " + (err.message || err), "error");
    console.error(err);
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
async function writeUpload(fileInput, fsPath) {
  const f = fileInput.files[0];
  if (!f) return null;
  const buf = new Uint8Array(await f.arrayBuffer());
  pyodide.FS.writeFile(fsPath, buf);
  return fsPath;
}

function readOutputs(names) {
  lastHtml = pyodide.FS.readFile("/report.html", { encoding: "utf8" });
  lastXlsx = pyodide.FS.readFile("/summary.xlsx");   // Uint8Array
  lastHtmlName = names[1];
  lastXlsxName = names[2];
  $("reportFrame").srcdoc = lastHtml;
  $("output").style.display = "block";
  $("output").scrollIntoView({ behavior: "smooth" });
}

function callRunReport(curPath, prevPath, mode, date) {
  const fn = pyodide.globals.get("run_report");
  const proxy = fn(curPath, prevPath, mode, date);
  const arr = proxy.toJs();
  proxy.destroy(); fn.destroy();
  return arr;
}

function download(name, data, mime) {
  const blob = new Blob([data], { type: mime });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

// ── Generate from uploaded files ─────────────────────────────────────────────
async function generate() {
  if (!$("currentFile").files[0]) {
    setStatus("⚠️ Please choose a current-week Excel file first.", "error");
    return;
  }
  generateBtn.disabled = true; demoBtn.disabled = true;
  try {
    busy("Reading uploaded file(s)…");
    const curPath = await writeUpload($("currentFile"), "/current.xlsx");
    const prevPath = await writeUpload($("previousFile"), "/previous.xlsx");

    busy("Crunching numbers and rendering charts…");
    await new Promise(r => setTimeout(r, 30)); // let the spinner paint
    const names = callRunReport(curPath, prevPath || "", $("mode").value, $("reportDate").value.trim());

    readOutputs(names);
    setStatus(`✅ Report generated in <strong>${names[0].toUpperCase()}</strong> mode.`, "ok");
  } catch (err) {
    setStatus("❌ " + (err.message || err), "error");
    console.error(err);
  } finally {
    generateBtn.disabled = false; demoBtn.disabled = false;
  }
}

// ── Generate from built-in demo data ─────────────────────────────────────────
async function runDemo() {
  generateBtn.disabled = true; demoBtn.disabled = true;
  try {
    busy("Generating demo dataset…");
    await new Promise(r => setTimeout(r, 30));
    const dfn = pyodide.globals.get("make_demo");
    const dproxy = dfn(); const paths = dproxy.toJs(); dproxy.destroy(); dfn.destroy();

    busy("Crunching demo numbers and rendering charts…");
    await new Promise(r => setTimeout(r, 30));
    const mode = $("mode").value === "current" ? "current" : "compare";
    const names = callRunReport(paths[0], paths[1], mode, $("reportDate").value.trim());

    readOutputs(names);
    setStatus(`✅ Demo report generated in <strong>${names[0].toUpperCase()}</strong> mode. Upload your own file to use real data.`, "ok");
  } catch (err) {
    setStatus("❌ " + (err.message || err), "error");
    console.error(err);
  } finally {
    generateBtn.disabled = false; demoBtn.disabled = false;
  }
}

// ── Wire up ──────────────────────────────────────────────────────────────────
generateBtn.addEventListener("click", generate);
demoBtn.addEventListener("click", runDemo);
$("dlHtml").addEventListener("click", () => {
  if (lastHtml) download(lastHtmlName, lastHtml, "text/html");
});
$("dlXlsx").addEventListener("click", () => {
  if (lastXlsx) download(lastXlsxName, lastXlsx,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
});

init();
