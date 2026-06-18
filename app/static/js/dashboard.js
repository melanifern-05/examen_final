(function () {
    const chartPalette = ["#E63946", "#A31621", "#7A1F2B", "#C1666B", "#BB4430", "#FF8A8A", "#5C0B14", "#FF6B6B"];
    const chartInstances = {};
    const monthNames = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];
 
    const ALL_ROWS = DATA_ROWS.map(r => {
        const o = {};
        DATA_FIELDS.forEach((f, i) => o[f] = r[i]);
        o.anio = o.fecha.slice(0, 4);
        o.mes = String(parseInt(o.fecha.slice(5, 7), 10));
        return o;
    });
 
    document.addEventListener("DOMContentLoaded", () => {
        bindSidebar();
        loadFilters();
        renderAll(ALL_ROWS);
        const form = document.getElementById("filtersForm");
        form.addEventListener("submit", (e) => e.preventDefault());
        form.querySelectorAll("select").forEach((input) => input.addEventListener("change", applyFilters));
        document.getElementById("clearFilters").addEventListener("click", () => {
            form.querySelectorAll("select").forEach((s) => s.value = "all");
            applyFilters();
        });
    });
 
    function bindSidebar() {
        const button = document.getElementById("sidebarToggle");
        if (!button) return;
        button.addEventListener("click", () => document.body.classList.toggle("sidebar-collapsed"));
    }
 
    function uniqueSorted(values) {
        return Array.from(new Set(values)).sort((a, b) => String(a).localeCompare(String(b), "es"));
    }
 
    function loadFilters() {
        const filterFields = {
            anio: uniqueSorted(ALL_ROWS.map(r => r.anio)),
            mes: uniqueSorted(ALL_ROWS.map(r => r.mes)).sort((a, b) => Number(a) - Number(b)),
            sucursal: uniqueSorted(ALL_ROWS.map(r => r.sucursal)),
            ciudad: uniqueSorted(ALL_ROWS.map(r => r.ciudad)),
            categoria: uniqueSorted(ALL_ROWS.map(r => r.categoria)),
            metodo: uniqueSorted(ALL_ROWS.map(r => r.metodo)),
            vendedor: uniqueSorted(ALL_ROWS.map(r => r.vendedor))
        };
        document.querySelectorAll("select[data-filter]").forEach((select) => {
            const key = select.dataset.filter;
            const values = filterFields[key] || [];
            select.innerHTML = '<option value="all">Todos</option>';
            values.forEach((value) => {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = key === "mes" ? (monthNames[Number(value) - 1] || value) : value;
                select.appendChild(option);
            });
        });
    }
 
    function applyFilters() {
        showLoader(true);
        const form = document.getElementById("filtersForm");
        const params = new FormData(form);
        const filtered = ALL_ROWS.filter((row) => {
            for (const [key, value] of params.entries()) {
                if (value && value !== "all" && String(row[key]) !== String(value)) return false;
            }
            return true;
        });
        setTimeout(() => {
            renderAll(filtered);
            showLoader(false);
        }, 80);
    }
 
    function renderAll(rows) {
        renderKpis(buildKpis(rows));
        renderCharts(buildCharts(rows));
        renderTable(rows);
    }
 
    function sum(rows, field) { return rows.reduce((acc, r) => acc + r[field], 0); }
 
    function topLabel(rows, field) {
        const totals = {};
        rows.forEach((r) => { totals[r[field]] = (totals[r[field]] || 0) + r.total; });
        let best = "Sin datos", bestVal = -Infinity;
        Object.entries(totals).forEach(([k, v]) => { if (v > bestVal) { bestVal = v; best = k; } });
        return best;
    }
 
    function money(value) {
        return new Intl.NumberFormat("es-BO", { style: "currency", currency: "BOB" }).format(value || 0);
    }
 
    function numberFmt(value) {
        return new Intl.NumberFormat("es-BO", { maximumFractionDigits: 0 }).format(value || 0);
    }
 
    function buildKpis(rows) {
        const totalVentas = sum(rows, "total");
        const cantidadTotal = sum(rows, "cantidad");
        const numVentas = rows.length;
        const ticketProm = numVentas ? totalVentas / numVentas : 0;
        const sucursalTop = topLabel(rows, "sucursal");
        const categoriaTop = topLabel(rows, "categoria");
        return [
            { title: "Ventas totales", value: money(totalVentas), icon: "fa-chart-line", tone: "crimson" },
            { title: "N\u00ba de ventas", value: numberFmt(numVentas), icon: "fa-receipt", tone: "coral" },
            { title: "Cantidad vendida", value: numberFmt(cantidadTotal), icon: "fa-boxes-stacked", tone: "rust" },
            { title: "Ticket promedio", value: money(ticketProm), icon: "fa-money-bill-wave", tone: "rose" },
            { title: "Sucursal top", value: sucursalTop, icon: "fa-store", tone: "wine" },
            { title: "Categoria top", value: categoriaTop, icon: "fa-tags", tone: "maroon" }
        ];
    }
 
    function renderKpis(kpis) {
        const grid = document.getElementById("kpiGrid");
        grid.innerHTML = "";
        kpis.forEach((kpi) => {
            const card = document.createElement("article");
            card.className = `kpi-card tone-${kpi.tone || "crimson"}`;
            card.innerHTML = `
                <div class="kpi-icon"><i class="fa-solid ${kpi.icon}"></i></div>
                <div><span>${escapeHtml(kpi.title)}</span><strong>${escapeHtml(kpi.value)}</strong></div>
            `;
            grid.appendChild(card);
        });
    }
 
    function groupSum(rows, field, limit) {
        const totals = {};
        rows.forEach((r) => { totals[r[field]] = (totals[r[field]] || 0) + r.total; });
        let entries = Object.entries(totals).sort((a, b) => b[1] - a[1]);
        if (limit) entries = entries.slice(0, limit);
        return { labels: entries.map(e => e[0]), data: entries.map(e => e[1]) };
    }
 
    function monthlyChart(rows) {
        const totals = {};
        rows.forEach((r) => {
            const key = `${r.anio}-${String(r.mes).padStart(2, "0")}`;
            totals[key] = (totals[key] || 0) + r.total;
        });
        const labels = Object.keys(totals).sort();
        return { labels, data: labels.map(l => totals[l]) };
    }
 
    function buildCharts(rows) {
        return [
            { title: "Ventas por mes", type: "line", ...monthlyChart(rows) },
            { title: "Ventas por sucursal", type: "bar", ...groupSum(rows, "sucursal") },
            { title: "Ventas por categoria", type: "doughnut", ...groupSum(rows, "categoria") },
            { title: "Ventas por metodo de pago", type: "bar", ...groupSum(rows, "metodo") }
        ];
    }
 
    function renderCharts(charts) {
        charts.forEach((chart, index) => {
            const canvas = document.getElementById(`chart-${index}`);
            if (!canvas) return;
            if (chartInstances[index]) chartInstances[index].destroy();
            chartInstances[index] = new Chart(canvas, {
                type: chart.type,
                data: {
                    labels: chart.labels,
                    datasets: [{
                        label: "Ventas",
                        data: chart.data,
                        borderColor: "#A31621",
                        backgroundColor: chartPalette,
                        borderWidth: 2,
                        tension: 0.35,
                        fill: chart.type === "line"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    resizeDelay: 120,
                    animation: { duration: 450 },
                    layout: { padding: 4 },
                    plugins: {
                        legend: { display: ["pie", "doughnut"].includes(chart.type), position: "bottom" },
                        tooltip: { callbacks: { label: (c) => ` ${money(c.parsed.y ?? c.parsed)}` } }
                    },
                    scales: ["pie", "doughnut"].includes(chart.type) ? {} : {
                        y: { beginAtZero: true, ticks: { callback: (v) => numberFmt(v) }, grid: { color: "rgba(92,11,20,0.08)" } },
                        x: { ticks: { color: "#A31621" }, grid: { display: false } }
                    }
                }
            });
        });
    }
 
    function summaryTable(rows) {
        const groups = {};
        rows.forEach((r) => {
            const key = `${r.sucursal}|||${r.ciudad}|||${r.categoria}`;
            if (!groups[key]) groups[key] = { sucursal: r.sucursal, ciudad: r.ciudad, categoria: r.categoria, ventas: 0, cantidad: 0, n: 0 };
            groups[key].ventas += r.total;
            groups[key].cantidad += r.cantidad;
            groups[key].n += 1;
        });
        const data = Object.values(groups)
            .sort((a, b) => b.ventas - a.ventas)
            .map((g) => ({
                sucursal: g.sucursal,
                ciudad: g.ciudad,
                categoria: g.categoria,
                ventas_totales: money(g.ventas),
                cantidad: numberFmt(g.cantidad),
                n_ventas: numberFmt(g.n),
                ticket_promedio: money(g.ventas / g.n)
            }));
        const columns = [
            { title: "Sucursal", data: "sucursal" },
            { title: "Ciudad", data: "ciudad" },
            { title: "Categoria", data: "categoria" },
            { title: "Ventas totales", data: "ventas_totales" },
            { title: "Cantidad", data: "cantidad" },
            { title: "N\u00ba Ventas", data: "n_ventas" },
            { title: "Ticket promedio", data: "ticket_promedio" }
        ];
        return { columns, data };
    }
 
    function renderTable(rows) {
        const { columns, data } = summaryTable(rows);
        const selector = "#analyticsTable";
        const table = $(selector);
        if ($.fn.DataTable.isDataTable(selector)) table.DataTable().clear().destroy();
        table.empty();
        table.DataTable({
            data: data,
            columns: columns,
            pageLength: 10,
            order: [],
            scrollX: true,
            dom: '<"dt-toolbar"Bf>rt<"dt-footer"lip>',
            buttons: [
                { extend: "csvHtml5", text: '<i class="fa-solid fa-file-csv"></i> CSV', className: "btn btn-sm btn-export" },
                { extend: "excelHtml5", text: '<i class="fa-solid fa-file-excel"></i> Excel', className: "btn btn-sm btn-export" }
            ],
            language: {
                search: "Buscar:", lengthMenu: "Mostrar _MENU_ registros", info: "Mostrando _START_ a _END_ de _TOTAL_",
                infoEmpty: "Sin registros", zeroRecords: "No se encontraron datos",
                paginate: { first: "Primero", last: "Ultimo", next: "Siguiente", previous: "Anterior" }
            }
        });
    }
 
    function showLoader(show) {
        const loader = document.getElementById("loaderOverlay");
        if (loader) loader.classList.toggle("visible", show);
    }
 
    function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));
    }
})();