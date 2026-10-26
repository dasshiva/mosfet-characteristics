# MOSFET Common-Source Characteristics

Interactive visualization and laboratory report for:

> **To Obtain the Drain and Transfer Characteristics of a MOSFET Connected in Common-Source Configuration**

## Contents

- `index.html` — interactive bench
- `css/styles.css` — visual design
- `js/app.js` — Shichman–Hodges NMOS model and SVG charts
- `report/MOSFET_CS_Characteristics_Report.pdf` — 12-page laboratory report
- `report/generate_report.py` — rebuilds the PDF
- `report/generate_figures.py` — regenerates the report figures
- `report/details.json` — student and department details used on the cover

## Run the website

Open `index.html` directly, or serve the folder:

```bash
cd mosfet-characteristics
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Rebuild the report

```bash
cd mosfet-characteristics/report
python3 generate_figures.py
python3 generate_report.py
```

The report uses the details in `details.json`.
