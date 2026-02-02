const API_BASE = '';
let statusChart = null;
let outletRiskChart = null;
let allOutlets = [];

function formatNumber(num) {
    return new Intl.NumberFormat('id-ID').format(num);
}

function formatCurrency(num) {
    return 'Rp ' + new Intl.NumberFormat('id-ID').format(num);
}

function formatPercent(num) {
    return num.toFixed(1) + '%';
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

async function fetchSummary() {
    const response = await fetch(`${API_BASE}/api/summary`);
    const data = await response.json();
    document.getElementById('totalTransaksi').textContent = formatNumber(data.total_transaksi);
    document.getElementById('totalOutlet').textContent = formatNumber(data.total_outlet);
    document.getElementById('transaksiBerisiko').textContent = formatNumber(data.transaksi_berisiko);
    document.getElementById('persenBerisiko').textContent = formatPercent(data.persen_berisiko);
    document.getElementById('lastUpdated').textContent = data.last_updated;
}

async function fetchOutlets() {
    const response = await fetch(`${API_BASE}/api/outlets`);
    allOutlets = await response.json();
    renderOutletsTable(allOutlets);
}

function renderOutletsTable(outlets) {
    const tbody = document.getElementById('outletsTableBody');
    tbody.innerHTML = '';
    
    outlets.forEach((outlet, index) => {
        const row = document.createElement('tr');
        const risk = outlet.persen_berisiko || 0;
        
        let badge = '';
        let rowClass = '';
        
        if (risk < 10) {
            badge = '<span class="badge badge-success">Aman</span>';
            rowClass = 'risk-low';
        } else if (risk < 30) {
            badge = '<span class="badge badge-warning">Perhatian</span>';
            rowClass = 'risk-medium';
        } else {
            badge = '<span class="badge badge-danger">Berisiko</span>';
            rowClass = 'risk-high';
        }
        
        row.className = rowClass;
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${outlet.outlet}</strong></td>
            <td>${formatNumber(outlet.total_transaksi)}</td>
            <td>${formatCurrency(outlet.total_pinjaman)}</td>
            <td><strong>${formatPercent(risk)}</strong></td>
            <td>${badge}</td>
        `;
        tbody.appendChild(row);
    });
}

async function fetchStatusChart() {
    const response = await fetch(`${API_BASE}/api/charts/status`);
    const data = await response.json();
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    if (statusChart) statusChart.destroy();
    
    statusChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels.map(l => l.charAt(0).toUpperCase() + l.slice(1).replace('_', ' ')),
            datasets: [{
                data: data.values,
                backgroundColor: ['#10b981', '#3b82f6', '#ef4444'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

async function fetchOutletRiskChart() {
    const response = await fetch(`${API_BASE}/api/charts/outlet-risk`);
    const data = await response.json();
    const ctx = document.getElementById('outletRiskChart').getContext('2d');
    
    if (outletRiskChart) outletRiskChart.destroy();
    
    outletRiskChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '% Berisiko',
                data: data.values,
                backgroundColor: '#ef4444'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: v => v + '%' }
                },
                x: {
                    ticks: { maxRotation: 45, minRotation: 45 }
                }
            }
        }
    });
}

async function runAnalysis() {
    if (!confirm('Jalankan analisis ulang?')) return;
    
    showLoading();
    const response = await fetch(`${API_BASE}/api/analyze`, { method: 'POST' });
    const data = await response.json();
    hideLoading();
    
    if (data.success) {
        alert('✓ Analisis berhasil!');
        loadAllData();
    }
}

function filterOutlets() {
    const search = document.getElementById('searchOutlet').value.toLowerCase();
    const filtered = allOutlets.filter(o => o.outlet.toLowerCase().includes(search));
    renderOutletsTable(filtered);
}

function sortOutlets() {
    const sortBy = document.getElementById('sortBy').value;
    const sorted = [...allOutlets].sort((a, b) => b[sortBy] - a[sortBy]);
    renderOutletsTable(sorted);
}

async function loadAllData() {
    showLoading();
    await Promise.all([
        fetchSummary(),
        fetchOutlets(),
        fetchStatusChart(),
        fetchOutletRiskChart()
    ]);
    hideLoading();
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    document.getElementById('btnAnalyze').addEventListener('click', runAnalysis);
    document.getElementById('searchOutlet').addEventListener('input', filterOutlets);
    document.getElementById('sortBy').addEventListener('change', sortOutlets);
});
