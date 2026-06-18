/* dashboard.js — Sistema de Análisis de Ventas */
"use strict";

const PALETTE = {
  bar:      ["#e2b96f","#c4873a","#7c5c3e","#6b8f71","#0f3460","#16213e","#4a4a8a","#a07850"],
  line:     "#e2b96f",
  doughnut: ["#e2b96f","#c4873a","#7c5c3e","#6b8f71","#0f3460","#4a4a8a","#a07850","#b0c4de"],
};

function renderChart(canvasId, cfg) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  const ctx = el.getContext("2d");

  const type   = cfg.type;
  const labels = cfg.labels;
  const data   = cfg.data;

  let dataset = {};

  if (type === "bar") {
    dataset = {
      data,
      backgroundColor: PALETTE.bar.slice(0, labels.length),
      borderRadius: 6,
      borderSkipped: false,
    };
  } else if (type === "line") {
    dataset = {
      data,
      borderColor: PALETTE.line,
      backgroundColor: "rgba(226,185,111,.15)",
      borderWidth: 2.5,
      pointBackgroundColor: PALETTE.line,
      pointRadius: 4,
      fill: true,
      tension: 0.35,
    };
  } else if (type === "doughnut") {
    dataset = {
      data,
      backgroundColor: PALETTE.doughnut.slice(0, labels.length),
      borderWidth: 2,
      borderColor: "#fff",
      hoverOffset: 8,
    };
  }

  new Chart(ctx, {
    type,
    data: { labels, datasets: [{ label: cfg.label, ...dataset }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: type === "doughnut",
          position: "bottom",
          labels: { font: { size: 11 }, padding: 12, boxWidth: 12 },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.parsed.y ?? ctx.parsed;
              if (type === "doughnut") return ` Bs ${v.toLocaleString("es-BO", { minimumFractionDigits: 2 })}`;
              return ` Bs ${v.toLocaleString("es-BO", { minimumFractionDigits: 2 })}`;
            },
          },
        },
      },
      scales: type !== "doughnut" ? {
        y: {
          beginAtZero: true,
          grid: { color: "rgba(0,0,0,.05)" },
          ticks: {
            font: { size: 10 },
            callback: (v) => "Bs " + v.toLocaleString("es-BO"),
          },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 10 }, maxRotation: 30 },
        },
      } : {},
    },
  });
}

/* Inicializa todos los gráficos embebidos en la página */
document.addEventListener("DOMContentLoaded", function () {
  if (typeof CHARTS_DATA === "undefined") return;
  CHARTS_DATA.forEach(function (cfg, i) {
    renderChart("chart" + i, cfg);
  });
});
