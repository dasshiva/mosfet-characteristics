/* ============================================================
   MOSFET Lab — interactive common-source characteristics
   Model: Shichman–Hodges square law with channel-length modulation
   ============================================================ */
(() => {
  "use strict";

  const NOMINAL = { vgs: 4.0, vdd: 12, rd: 2.2, vth: 2.0, kn: 0.5, lambda: 0.02 };
  const FAMILY = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0];
  const PALETTE = ["#9fe8e1", "#7ddcd5", "#5bcec9", "#45bfc1", "#55a8d8", "#6a8ee6", "#7b73e0", "#8b5cf6"];
  const state = { ...NOMINAL, tab: "output" };

  const $ = (id) => document.getElementById(id);
  const chart = $("chart");
  const tooltip = $("tooltip");
  const chartPanel = $("chartPanel");
  const runBtn = $("runBtn");
  let sweepTimer = null;
  let sweepDir = 1;

  /* ---------- model ---------- */
  function drainCurrent(vgs, vds) {
    const vov = vgs - state.vth;
    if (vov <= 0) return 0;
    const lambdaFactor = 1 + state.lambda * vds;
    if (vds < vov) {
      return state.kn * (vov * vds - 0.5 * vds * vds) * lambdaFactor;
    }
    return 0.5 * state.kn * vov * vov * lambdaFactor;
  }

  function regionAt(vgs, vds) {
    if (vgs <= state.vth) return "Cutoff";
    if (vds < vgs - state.vth) return "Triode";
    return "Saturation";
  }

  function gmAt(vgs, vds) {
    const dv = 0.01;
    return (drainCurrent(vgs + dv, vds) - drainCurrent(vgs - dv, vds)) / (2 * dv);
  }

  function computeQ(vgs) {
    if (vgs <= state.vth) {
      return { vds: state.vdd, id: 0, region: "Cutoff" };
    }
    const f = (vds) => drainCurrent(vgs, vds) - (state.vdd - vds) / state.rd;
    let lo = 0;
    let hi = state.vdd;
    for (let i = 0; i < 70; i += 1) {
      const mid = (lo + hi) / 2;
      if (f(mid) > 0) hi = mid;
      else lo = mid;
    }
    const vds = (lo + hi) / 2;
    return { vds, id: drainCurrent(vgs, vds), region: regionAt(vgs, vds) };
  }

  /* ---------- formatting ---------- */
  const fmt = (value, digits = 2) => Number(value).toFixed(digits);
  const fmtSmart = (value) => (Math.abs(value) < 0.01 ? Number(value).toFixed(3) : Number(value).toFixed(2));
  const vdsTransfer = () => Math.min(10, state.vdd);

  /* ---------- chart helpers ---------- */
  function niceMax(value) {
    if (!Number.isFinite(value) || value <= 0) return 1;
    const padded = value * 1.1;
    if (padded <= 2) return Math.ceil(padded * 10) / 10;
    if (padded <= 10) return Math.ceil(padded * 2) / 2;
    return Math.ceil(padded);
  }

  function xTicks(max) {
    const step = max <= 6 ? 1 : max <= 12 ? 2 : max <= 20 ? 4 : 5;
    const ticks = [];
    for (let t = 0; t <= max + 1e-9; t += step) ticks.push(Number(t.toFixed(4)));
    return ticks;
  }

  function yTicks(max) {
    const step = max <= 1 ? 0.2 : max <= 2 ? 0.5 : max <= 10 ? 1 : Math.ceil(max / 6);
    const ticks = [];
    for (let t = 0; t <= max + 1e-9; t += step) ticks.push(Number(t.toFixed(4)));
    return ticks;
  }

  function selectedColor() {
    return "#0d9488";
  }

  function curveColor(index) {
    return PALETTE[index % PALETTE.length];
  }

  function escapeHTML(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  function chartFrame({ title, subtitle, xMax, yMax, xLabel, yLabel, xTickList, yTickList, extraDefs = "" }) {
    const W = 760;
    const H = 470;
    const m = { l: 74, r: 26, t: 48, b: 60 };
    const pw = W - m.l - m.r;
    const ph = H - m.t - m.b;
    const sx = (v) => m.l + (v / xMax) * pw;
    const sy = (v) => m.t + ph - (Math.max(0, Math.min(v, yMax)) / yMax) * ph;
    const gridX = xTickList.map((t) => `<line class="grid-line" x1="${sx(t)}" y1="${m.t}" x2="${sx(t)}" y2="${m.t + ph}"/>`).join("");
    const gridY = yTickList.map((t) => `<line class="grid-line" x1="${m.l}" y1="${sy(t)}" x2="${m.l + pw}" y2="${sy(t)}"/>`).join("");
    const labelsX = xTickList.map((t) => `<text class="tick-text" x="${sx(t)}" y="${m.t + ph + 18}" text-anchor="middle">${t}</text>`).join("");
    const labelsY = yTickList.map((t) => `<text class="tick-text" x="${m.l - 11}" y="${sy(t) + 3.5}" text-anchor="end">${t}</text>`).join("");

    return {
      W, H, m, pw, ph, sx, sy,
      svg: `
        <defs>
          <linearGradient id="selectedFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#2dd4bf" stop-opacity=".28"/>
            <stop offset="1" stop-color="#2dd4bf" stop-opacity="0"/>
          </linearGradient>
          <linearGradient id="satFill" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#e8fbf7" stop-opacity=".8"/>
            <stop offset="1" stop-color="#e8fbf7" stop-opacity="0"/>
          </linearGradient>
          <clipPath id="plotClip"><rect x="${m.l}" y="${m.t}" width="${pw}" height="${ph}"/></clipPath>
          ${extraDefs}
        </defs>
        <rect x="${m.l}" y="${m.t}" width="${pw}" height="${ph}" fill="#fbfdff"/>
        ${gridX}${gridY}
        <line class="axis-line" x1="${m.l}" y1="${m.t + ph}" x2="${m.l + pw}" y2="${m.t + ph}"/>
        <line class="axis-line" x1="${m.l}" y1="${m.t}" x2="${m.l}" y2="${m.t + ph}"/>
        ${labelsX}${labelsY}
        <text class="axis-label" x="${m.l + pw / 2}" y="${H - 12}" text-anchor="middle">${xLabel}</text>
        <text class="axis-label" x="21" y="${m.t + ph / 2}" text-anchor="middle" transform="rotate(-90 21 ${m.t + ph / 2})">${yLabel}</text>
        <text class="chart-title" x="${m.l}" y="25">${title}</text>
        <text class="chart-subtitle" x="${m.l}" y="41">${subtitle}</text>
      `,
      closing: "</svg>"
    };
  }

  /* ---------- output characteristics ---------- */
  function renderOutput() {
    const q = computeQ(state.vgs);
    const maxCurve = FAMILY.reduce((max, vgs) => Math.max(max, drainCurrent(vgs, state.vdd)), 0);
    const yMax = niceMax(Math.max(maxCurve, 1));
    const yT = yTicks(yMax);
    const xT = xTicks(state.vdd);
    const frame = chartFrame({
      title: "Drain characteristics",
      subtitle: `I<tspan baseline-shift="sub" font-size="9">D</tspan> vs V<tspan baseline-shift="sub" font-size="9">DS</tspan> · V<tspan baseline-shift="sub" font-size="9">GS</tspan> stepped from 2.5 V to 6.0 V`,
      xMax: state.vdd,
      yMax,
      xLabel: "Drain–source voltage, V<tspan baseline-shift=\"sub\" font-size=\"9\">DS</tspan> (V)",
      yLabel: "Drain current, I<tspan baseline-shift=\"sub\" font-size=\"9\">D</tspan> (mA)",
      xTickList: xT,
      yTickList: yT
    });
    const { m, pw, ph, sx, sy } = frame;

    // Cut-off/triode boundary for the selected gate bias
    const vov = Math.max(0, state.vgs - state.vth);
    const boundary = vov > 0 && vov < state.vdd
      ? `<line class="boundary" x1="${sx(vov)}" y1="${m.t}" x2="${sx(vov)}" y2="${m.t + ph}"/>
         <text class="tick-text" x="${sx(vov) + 6}" y="${m.t + 15}" fill="#8a99ad">V\u2081\u2082 = V\u2092\u1d65</text>`
      : "";

    // Device curves
    let curves = "";
    FAMILY.forEach((vgs, index) => {
      const selected = Math.abs(vgs - state.vgs) < 0.001;
      const points = [];
      const steps = 140;
      for (let i = 0; i <= steps; i += 1) {
        const vds = (i / steps) * state.vdd;
        points.push([sx(vds), sy(drainCurrent(vgs, vds))]);
      }
      const d = points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
      const fill = selected
        ? `<path d="${d} L${sx(state.vdd)},${m.t + ph} L${m.l},${m.t + ph} Z" fill="url(#selectedFill)" clip-path="url(#plotClip)"/>`
        : "";
      curves += `${fill}<path class="series${selected ? " selected" : ""}" d="${d}" stroke="${selected ? selectedColor() : curveColor(index)}" opacity="${selected ? 1 : 0.62}" clip-path="url(#plotClip)"/>`;
    });

    // DC load line
    const loadLine = `<line class="loadline" x1="${sx(0)}" y1="${sy(state.vdd / state.rd)}" x2="${sx(state.vdd)}" y2="${sy(0)}" clip-path="url(#plotClip)"/>`;

    // Quiescent point
    const qMarkup = `
      <line class="qguide" x1="${sx(0)}" y1="${sy(q.id)}" x2="${sx(q.vds)}" y2="${sy(q.id)}" clip-path="url(#plotClip)"/>
      <line class="qguide" x1="${sx(q.vds)}" y1="${m.t + ph}" x2="${sx(q.vds)}" y2="${sy(q.id)}" clip-path="url(#plotClip)"/>
      <circle class="qpoint" cx="${sx(q.vds)}" cy="${sy(q.id)}" r="6.5"/>
      <text class="q-label" x="${Math.min(sx(q.vds) + 12, m.l + pw - 70)}" y="${Math.max(sy(q.id) - 12, m.t + 14)}">Q</text>
    `;

    const loadLabelX = sx(state.vdd * 0.72);
    const loadLabelY = sy((state.vdd - state.vdd * 0.72) / state.rd) - 10;
    const loadLabel = loadLabelY > m.t + 20
      ? `<text class="tick-text" x="${loadLabelX}" y="${loadLabelY}" fill="#d95f5c">DC load line</text>`
      : "";

    chart.innerHTML = `<title id="chartTitle"></title><desc id="chartDesc"></desc>${frame.svg}${boundary}<g clip-path="url(#plotClip)">${curves}${loadLine}${qMarkup}${loadLabel}</g>${frame.closing}`;

    $("chartTitle").textContent = "Drain characteristics of an NMOS transistor";
    $("chartDesc").textContent = `Drain current versus drain-source voltage for gate voltages from 2.5 to 6 volts. The selected gate voltage is ${fmt(state.vgs, 1)} volts and the quiescent point is ${fmtSmart(q.id)} milliamps at ${fmt(q.vds)} volts.`;
    $("chartMode").innerHTML = "Output family: I<sub>D</sub> vs V<sub>DS</sub> at fixed V<sub>GS</sub>";
    $("chartStatus").innerHTML = `V<sub>DD</sub> = ${fmt(state.vdd, 0)} V · R<sub>D</sub> = ${fmt(state.rd, 2)} kΩ · Q in ${q.region.toLowerCase()}`;
    $("legend").innerHTML = `
      <span class="legend-item"><span class="legend-swatch" style="background:${selectedColor()}"></span>Selected V<sub>GS</sub> = ${fmt(state.vgs, 1)} V</span>
      <span class="legend-item"><span class="legend-swatch" style="background:#7ddcd5"></span>V<sub>GS</sub> family</span>
      <span class="legend-item"><span class="legend-swatch dashed"></span>DC load line</span>
      <span class="legend-item"><span class="legend-swatch dot" style="background:#071426;border:2px solid #2dd4bf"></span>Quiescent point Q</span>`;
    return q;
  }

  /* ---------- transfer characteristics ---------- */
  function renderTransfer() {
    const vdsT = vdsTransfer();
    const curveMax = drainCurrent(6, vdsT);
    const yMax = niceMax(Math.max(curveMax, 1));
    const yT = yTicks(yMax);
    const xT = xTicks(6);
    const frame = chartFrame({
      title: "Transfer characteristics",
      subtitle: `I<tspan baseline-shift="sub" font-size="9">D</tspan> vs V<tspan baseline-shift="sub" font-size="9">GS</tspan> at V<tspan baseline-shift="sub" font-size="9">DS</tspan> = ${fmt(vdsT, 0)} V · square-law region`,
      xMax: 6,
      yMax,
      xLabel: "Gate–source voltage, V<tspan baseline-shift=\"sub\" font-size=\"9\">GS</tspan> (V)",
      yLabel: "Drain current, I<tspan baseline-shift=\"sub\" font-size=\"9\">D</tspan> (mA)",
      xTickList: xT,
      yTickList: yT
    });
    const { m, pw, ph, sx, sy } = frame;

    const points = [];
    const steps = 220;
    for (let i = 0; i <= steps; i += 1) {
      const vgs = (i / steps) * 6;
      points.push([sx(vgs), sy(drainCurrent(vgs, vdsT))]);
    }
    const d = points.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(2)},${y.toFixed(2)}`).join(" ");

    const cutoffWidth = Math.max(0, sx(state.vth) - sx(0));
    const cutoffBand = cutoffWidth > 1
      ? `<rect x="${sx(0)}" y="${m.t}" width="${cutoffWidth}" height="${ph}" fill="#eef2f8" opacity=".8"/>`
      : "";

    const vthLine = state.vth < 6
      ? `<line class="boundary" x1="${sx(state.vth)}" y1="${m.t}" x2="${sx(state.vth)}" y2="${m.t + ph}"/>
         <text class="tick-text" x="${sx(state.vth) + 6}" y="${m.t + 15}" fill="#8a99ad">V\u209c\u2095 = ${fmt(state.vth, 1)} V</text>`
      : "";

    const idT = drainCurrent(state.vgs, vdsT);
    const gmT = gmAt(state.vgs, vdsT);
    const tangentRange = 0.55;
    const tx1 = Math.max(0, state.vgs - tangentRange);
    const tx2 = Math.min(6, state.vgs + tangentRange);
    const ty1 = idT + gmT * (tx1 - state.vgs);
    const ty2 = idT + gmT * (tx2 - state.vgs);
    const tangent = Math.abs(gmT) > 0.001
      ? `<line class="tangent" x1="${sx(tx1)}" y1="${sy(ty1)}" x2="${sx(tx2)}" y2="${sy(ty2)}" clip-path="url(#plotClip)"/>`
      : "";

    const qMarkup = idT > 0.0001
      ? `<line class="qguide" x1="${sx(0)}" y1="${sy(idT)}" x2="${sx(state.vgs)}" y2="${sy(idT)}" clip-path="url(#plotClip)"/>
         <line class="qguide" x1="${sx(state.vgs)}" y1="${m.t + ph}" x2="${sx(state.vgs)}" y2="${sy(idT)}" clip-path="url(#plotClip)"/>
         <circle class="qpoint" cx="${sx(state.vgs)}" cy="${sy(idT)}" r="6.5"/>
         <text class="q-label" x="${Math.min(sx(state.vgs) + 12, m.l + pw - 72)}" y="${Math.max(sy(idT) - 12, m.t + 14)}">Q</text>`
      : "";

    chart.innerHTML = `<title id="chartTitle"></title><desc id="chartDesc"></desc>${frame.svg}${cutoffBand}${vthLine}
      <path d="${d} L${sx(6)},${m.t + ph} L${sx(0)},${m.t + ph} Z" fill="url(#selectedFill)" clip-path="url(#plotClip)"/>
      <path class="series selected" d="${d}" stroke="${selectedColor()}" clip-path="url(#plotClip)"/>
      ${tangent}${qMarkup}${frame.closing}`;

    $("chartTitle").textContent = "Transfer characteristics of an NMOS transistor";
    $("chartDesc").textContent = `Drain current versus gate-source voltage at a drain-source voltage of ${fmt(vdsT, 0)} volts. The selected gate voltage is ${fmt(state.vgs, 1)} volts, giving ${fmtSmart(idT)} milliamps and a transconductance of ${fmt(gmT, 2)} millisiemens.`;
    $("chartMode").innerHTML = "Transfer curve: I<sub>D</sub> vs V<sub>GS</sub> at fixed V<sub>DS</sub>";
    $("chartStatus").innerHTML = `V<sub>DS</sub> = ${fmt(vdsT, 0)} V · V<sub>th</sub> = ${fmt(state.vth, 1)} V · g<sub>m</sub> = ${fmt(gmT, 2)} mS`;
    $("legend").innerHTML = `
      <span class="legend-item"><span class="legend-swatch" style="background:${selectedColor()}"></span>Transfer curve</span>
      <span class="legend-item"><span class="legend-swatch" style="background:#f59e0b"></span>Tangent at Q (slope g<sub>m</sub>)</span>
      <span class="legend-item"><span class="legend-swatch dot" style="background:#071426;border:2px solid #2dd4bf"></span>Selected bias point</span>`;
    return { idT, gmT, region: regionAt(state.vgs, vdsT) };
  }

  /* ---------- readout ---------- */
  function updateReadout() {
    let id;
    let vds;
    let region;
    let gm;
    let vov;

    if (state.tab === "output") {
      const q = computeQ(state.vgs);
      id = q.id;
      vds = q.vds;
      region = q.region;
      gm = gmAt(state.vgs, q.vds);
      vov = state.vgs - state.vth;
    } else {
      vds = vdsTransfer();
      id = drainCurrent(state.vgs, vds);
      region = regionAt(state.vgs, vds);
      gm = gmAt(state.vgs, vds);
      vov = state.vgs - state.vth;
    }

    $("idValue").textContent = fmtSmart(id);
    $("vdsValue").textContent = `${fmt(vds)} V`;
    $("vovValue").textContent = `${vov > 0 ? fmt(vov) : "—"} V`;
    $("gmValue").textContent = `${fmt(gm)} mS`;
    $("powerValue").textContent = `${fmt(id * vds, 1)} mW`;

    const pill = $("regionPill");
    pill.textContent = region;
    pill.className = "region-pill" + (region === "Triode" ? " triode" : region === "Cutoff" ? " cutoff" : "");

    const conditionClass = (name) => (region === name ? "condition is-on" : "condition");
    $("conditionList").innerHTML = `
      <div class="${conditionClass("Cutoff")}"><i></i>Cut-off: V<sub>GS</sub> ≤ V<sub>th</sub></div>
      <div class="${conditionClass("Triode")}"><i></i>Triode: V<sub>DS</sub> &lt; V<sub>GS</sub> − V<sub>th</sub></div>
      <div class="${conditionClass("Saturation")}"><i></i>Saturation: V<sub>DS</sub> ≥ V<sub>GS</sub> − V<sub>th</sub></div>`;
  }

  /* ---------- data table ---------- */
  function tableData() {
    if (state.tab === "output") {
      return FAMILY.map((vgs) => {
        const q = computeQ(vgs);
        return [vgs, q.vds, q.id, q.region, gmAt(vgs, q.vds)];
      });
    }
    const vdsT = vdsTransfer();
    return FAMILY.map((vgs) => [
      vgs,
      drainCurrent(vgs, vdsT),
      gmAt(vgs, vdsT),
      regionAt(vgs, vdsT)
    ]);
  }

  function renderTable() {
    if (state.tab === "output") {
      $("tableHead").innerHTML = "<th>V<sub>GS</sub> (V)</th><th>V<sub>DS,Q</sub> (V)</th><th>I<sub>D,Q</sub> (mA)</th><th>Region</th><th>g<sub>m</sub> (mS)</th>";
      $("tableBody").innerHTML = tableData().map(([vgs, vds, id, region, gm]) => {
        const selected = Math.abs(vgs - state.vgs) < 0.001 ? " class=\"is-selected\"" : "";
        return `<tr${selected}><td>${fmt(vgs, 1)}</td><td>${fmt(vds)}</td><td>${fmt(id)}</td><td><span class="tag ${region.toLowerCase()}">${region}</span></td><td>${fmt(gm)}</td></tr>`;
      }).join("");
      $("tableCaption").innerHTML = "Quiescent points for the common-source stage. Q is the intersection of the device curve and the DC load line I<sub>D</sub> = (V<sub>DD</sub> − V<sub>DS</sub>)/R<sub>D</sub>.";
    } else {
      $("tableHead").innerHTML = "<th>V<sub>GS</sub> (V)</th><th>I<sub>D</sub> at V<sub>DS</sub> (mA)</th><th>g<sub>m</sub> (mS)</th><th>Region</th>";
      $("tableBody").innerHTML = tableData().map(([vgs, id, gm, region]) => {
        const selected = Math.abs(vgs - state.vgs) < 0.001 ? " class=\"is-selected\"" : "";
        return `<tr${selected}><td>${fmt(vgs, 1)}</td><td>${fmt(id)}</td><td>${fmt(gm)}</td><td><span class="tag ${region.toLowerCase()}">${region}</span></td></tr>`;
      }).join("");
      $("tableCaption").innerHTML = `Transfer readings at V<sub>DS</sub> = ${fmt(vdsTransfer(), 0)} V. The slope of this curve is the device transconductance g<sub>m</sub>.`;
    }
  }

  /* ---------- controls ---------- */
  function updateFill(input) {
    const min = Number(input.min);
    const max = Number(input.max);
    const value = Number(input.value);
    const percent = ((value - min) / (max - min)) * 100;
    input.style.setProperty("--fill", `${percent}%`);
  }

  function syncControlLabels() {
    $("vgsOut").textContent = `${fmt(state.vgs, 1)} V`;
    $("vddOut").textContent = `${fmt(state.vdd, 0)} V`;
    $("rdOut").textContent = `${fmt(state.rd, 2)} kΩ`;
    $("vthOut").textContent = `${fmt(state.vth, 1)} V`;
    $("knOut").textContent = `${fmt(state.kn, 2)} mA/V²`;
    $("lambdaOut").textContent = `${fmt(state.lambda, 3)} V⁻¹`;
    document.querySelectorAll('input[type="range"]').forEach(updateFill);
  }

  function render() {
    syncControlLabels();
    if (state.tab === "output") renderOutput();
    else renderTransfer();
    updateReadout();
    renderTable();
  }

  const rangeBindings = [
    ["vgs", "vgs", (v) => v],
    ["vdd", "vdd", (v) => v],
    ["rd", "rd", (v) => v],
    ["vth", "vth", (v) => v],
    ["kn", "kn", (v) => v],
    ["lambda", "lambda", (v) => v]
  ];

  rangeBindings.forEach(([id, key]) => {
    const el = $(id);
    el.addEventListener("input", () => {
      if (id === "vgs") stopSweep();
      state[key] = Number(el.value);
      render();
    });
    updateFill(el);
  });

  $("resetBtn").addEventListener("click", () => {
    stopSweep();
    Object.assign(state, NOMINAL);
    $("vgs").value = NOMINAL.vgs;
    $("vdd").value = NOMINAL.vdd;
    $("rd").value = NOMINAL.rd;
    $("vth").value = NOMINAL.vth;
    $("kn").value = NOMINAL.kn;
    $("lambda").value = NOMINAL.lambda;
    render();
    chartPanel.classList.remove("is-drawing");
    void chartPanel.offsetWidth;
    chartPanel.classList.add("is-drawing");
  });

  /* ---------- tabs ---------- */
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((t) => {
        t.classList.remove("is-active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("is-active");
      tab.setAttribute("aria-selected", "true");
      state.tab = tab.dataset.tab;
      chartPanel.classList.remove("is-drawing");
      void chartPanel.offsetWidth;
      chartPanel.classList.add("is-drawing");
      tooltip.hidden = true;
      render();
    });
  });

  /* ---------- sweep ---------- */
  function startSweep() {
    sweepDir = 1;
    runBtn.classList.add("is-running");
    runBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg> Stop sweep';
    sweepTimer = window.setInterval(() => {
      let next = Number((state.vgs + sweepDir * 0.1).toFixed(1));
      if (next >= 6) { next = 6; sweepDir = -1; }
      if (next <= 2) { next = 2; sweepDir = 1; }
      state.vgs = next;
      $("vgs").value = next;
      render();
    }, 90);
  }

  function stopSweep() {
    if (sweepTimer) {
      window.clearInterval(sweepTimer);
      sweepTimer = null;
    }
    runBtn.classList.remove("is-running");
    runBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg> Run sweep';
  }

  runBtn.addEventListener("click", () => {
    if (sweepTimer) stopSweep();
    else startSweep();
  });

  /* ---------- tooltip ---------- */
  chart.addEventListener("mousemove", (event) => {
    const wrapRect = chart.getBoundingClientRect();
    const scaleX = 760 / wrapRect.width;
    const scaleY = 470 / wrapRect.height;
    const x = (event.clientX - wrapRect.left) * scaleX;
    const y = (event.clientY - wrapRect.top) * scaleY;
    const m = { l: 74, r: 26, t: 48, b: 60 };
    const pw = 760 - m.l - m.r;
    const ph = 470 - m.t - m.b;
    if (x < m.l || x > m.l + pw || y < m.t || y > m.t + ph) {
      tooltip.hidden = true;
      return;
    }

    if (state.tab === "output") {
      const vds = ((x - m.l) / pw) * state.vdd;
      const id = drainCurrent(state.vgs, vds);
      tooltip.innerHTML = `V<sub>DS</sub> <strong>${fmt(vds)} V</strong><br>I<sub>D</sub> <strong>${fmtSmart(id)} mA</strong>`;
    } else {
      const vgs = ((x - m.l) / pw) * 6;
      const id = drainCurrent(vgs, vdsTransfer());
      tooltip.innerHTML = `V<sub>GS</sub> <strong>${fmt(vgs)} V</strong><br>I<sub>D</sub> <strong>${fmtSmart(id)} mA</strong>`;
    }

    tooltip.hidden = false;
    const localX = event.clientX - wrapRect.left;
    const localY = event.clientY - wrapRect.top;
    tooltip.style.left = `${localX}px`;
    tooltip.style.top = `${localY}px`;
  });
  chart.addEventListener("mouseleave", () => { tooltip.hidden = true; });

  /* ---------- table export ---------- */
  function tableAsMatrix() {
    const rows = tableData();
    if (state.tab === "output") {
      return {
        header: ["VGS (V)", "VDS_Q (V)", "ID_Q (mA)", "Region", "gm (mS)"],
        rows
      };
    }
    return {
      header: ["VGS (V)", "ID at VDS=10V (mA)", "gm (mS)", "Region"],
      rows
    };
  }

  $("csvBtn").addEventListener("click", () => {
    const { header, rows } = tableAsMatrix();
    const csv = [header, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `mosfet-${state.tab}-characteristics.csv`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });

  $("copyBtn").addEventListener("click", async () => {
    const { header, rows } = tableAsMatrix();
    const tsv = [header, ...rows].map((row) => row.join("\t")).join("\n");
    const button = $("copyBtn");
    try {
      await navigator.clipboard.writeText(tsv);
      button.textContent = "Copied";
      window.setTimeout(() => { button.textContent = "Copy table"; }, 1600);
    } catch {
      button.textContent = "Copy failed";
      window.setTimeout(() => { button.textContent = "Copy table"; }, 1600);
    }
  });

  /* ---------- boot ---------- */
  window.addEventListener("resize", () => {
    tooltip.hidden = true;
  });

  render();
  chartPanel.classList.add("is-drawing");
})();
