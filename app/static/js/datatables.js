/* datatables.js — inicialización de DataTables */
"use strict";

document.addEventListener("DOMContentLoaded", function () {
  const el = document.getElementById("tablaResumen");
  if (!el) return;

  $(el).DataTable({
    pageLength: 10,
    lengthMenu: [10, 25, 50],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.8/i18n/es-ES.json",
    },
    dom: "Bfrtip",
    buttons: [
      {
        extend: "csv",
        text: '<i class="fa fa-download me-1"></i>Exportar CSV',
        className: "btn btn-sm btn-outline-secondary",
        filename: "ventas_resumen",
      },
    ],
    order: [[3, "desc"]],
  });
});
