const API_URL = window.location.origin + '/api';
let charts = {};
let allStudents = [];

// Initialize
// Initialize
window.onload = async function () {
    // Configure Chart.js Defaults for Glassmorphism
    Chart.defaults.font.family = "'Outfit', sans-serif";
    Chart.defaults.color = '#64748b';
    Chart.defaults.scale.grid.color = 'rgba(255, 255, 255, 0.1)';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(255, 255, 255, 0.9)';
    Chart.defaults.plugins.tooltip.titleColor = '#0f172a';
    Chart.defaults.plugins.tooltip.bodyColor = '#475569';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.5)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 10;

    await checkConnection();
    loadDashboard();
};

// --- Connection & Tabs ---

async function checkConnection() {
    try {
        const response = await fetch(`${API_URL}/dashboard`); // Using dashboard as health check
        if (response.ok) {
            updateStatus(true);
            return true;
        }
    } catch (error) {
        updateStatus(false);
        return false;
    }
}

function updateStatus(isConnected) {
    const el = document.getElementById('connectionStatus');
    if (isConnected) {
        el.innerHTML = '✅ Connected';
        el.className = 'status-badge status-connected';
    } else {
        el.innerHTML = '❌ disconnected';
        el.className = 'status-badge status-disconnected';
    }
}

window.showTab = function (tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    // Find button that triggers this tab and make active
    const buttons = document.getElementsByClassName('tab-btn');
    for (let btn of buttons) {
        if (btn.getAttribute('onclick').includes(tabName)) {
            btn.classList.add('active');
        }
    }

    if (tabName === 'dashboard') loadDashboard();
    if (tabName === 'analytics') loadAnalytics();
    if (tabName === 'students') loadStudents();
}

// --- Dashboard ---

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/dashboard`);
        const data = await response.json();

        if (data.stats && data.stats.total_students > 0) {
            animateValue('totalStudents', data.stats.total_students);
            animateValue('avgPerformance', data.stats.average_performance, '%');
            animateValue('atRiskStudents', data.stats.at_risk_students);
            animateValue('highPerformers', data.stats.high_performers);

            // New Stats
            animateValue('avgAttendance', data.stats.average_attendance, '%');
            animateValue('avgStudyHours', data.stats.average_study_hours, 'h');

            createPerformanceChart(data.performance_distribution);
            createRiskChart(data.risk_distribution);

            document.getElementById('dashboardAlert').innerHTML = '';
        } else {
            document.getElementById('dashboardAlert').innerHTML =
                '<div class="alert alert-warning">⚠️ No data available. Please get started by uploading student data.</div>';
        }
    } catch (error) {
        console.error(error);
        document.getElementById('dashboardAlert').innerHTML =
            '<div class="alert alert-danger">❌ Failed to load dashboard data. Make sure backend is running.</div>';
    }
}

function animateValue(id, value, suffix = '') {
    const el = document.getElementById(id);
    el.textContent = value + suffix;
    // Simple improvement: could add counting animation here
}

// --- Upload ---

window.uploadFile = async function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const statusEl = document.getElementById('uploadStatus');
    statusEl.innerHTML = '<div class="alert alert-info"><div class="loading"></div> Uploading and processing data...</div>';

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            statusEl.innerHTML = `
                <div class="alert alert-success">
                    ✅ Success! Uploaded ${data.total_students} students. Model has been retrained.
                </div>`;
            // Refresh dashboard
            loadDashboard();
        } else {
            statusEl.innerHTML = `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        statusEl.innerHTML = `<div class="alert alert-danger">❌ Connection failed: ${error.message}</div>`;
    }
}

// --- Prediction ---

window.predictPerformance = async function (event) {
    event.preventDefault();

    const data = {
        attendance: parseFloat(document.getElementById('attendance').value),
        study_hours: parseFloat(document.getElementById('studyHours').value),
        previous_grades: parseFloat(document.getElementById('previousGrades').value),
        assignments_completed: parseFloat(document.getElementById('assignments').value),
        participation: parseInt(document.getElementById('participation').value)
    };

    const btn = document.getElementById('predictBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<div class="loading"></div> Analyzing...';

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (response.ok) {
            // Enhanced Smart Alerts
            const alerts = generateSmartAlerts(data, result.predicted_score);
            let insightsHtml = '';

            if (alerts.length > 0) {
                insightsHtml = `
                    <div style="margin-top: 24px;">
                        <h4 style="margin-bottom: 12px; color: var(--dark); display: flex; align-items: center; gap: 8px;">
                            <span>🧠</span> AI Insights
                        </h4>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            ${alerts.map(a => `
                                <div class="alert ${a.type}" style="margin-bottom: 0; padding: 12px; font-size: 0.95em;">
                                    ${a.message}
                                </div>
                            `).join('')}
                        </div>
                    </div>`;
            }

            document.getElementById('predictionResult').innerHTML = `
                <div class="alert alert-${result.color}" style="display: block; text-align: center; border: 2px solid ${result.color === 'success' ? '#10b981' : result.color === 'warning' ? '#f59e0b' : '#ef4444'}; background: rgba(255,255,255,0.9);">
                    <div style="font-size: 1.25em; font-weight: 700; margin-bottom: 8px; color: var(--dark);">${result.status}</div>
                    <div style="font-size: 3.5em; font-weight: 800; margin: 10px 0; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${result.predicted_score}%</div>
                    <div style="font-size: 1.05em; color: var(--gray-text); font-weight: 500;">${result.recommendation}</div>
                    <div style="margin-top: 16px;">
                        <span class="risk-badge risk-${result.risk_level.toLowerCase()}" style="font-size: 1em; padding: 8px 16px;">
                            ${result.risk_level} Risk
                        </span>
                    </div>
                </div>
                ${insightsHtml}
            `;
        } else {
            document.getElementById('predictionResult').innerHTML =
                `<div class="alert alert-danger">❌ ${result.error}</div>`;
        }
    } catch (error) {
        document.getElementById('predictionResult').innerHTML =
            `<div class="alert alert-danger">❌ Failed to connect: ${error.message}</div>`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

// --- Analytics ---

async function loadAnalytics() {
    try {
        const response = await fetch(`${API_URL}/analytics`);
        const data = await response.json();

        if (data.attendance_vs_performance) {
            createScatterChart('attendanceChart', 'Attendance vs Performance',
                data.attendance_vs_performance, 'Attendance %', 'Performance %');

            createScatterChart('studyChart', 'Study Hours vs Performance',
                data.study_hours_vs_performance, 'Study Hours', 'Performance %');

            if (data.participation_distribution) {
                createDoughnutChart('participationChart', data.participation_distribution);
            }

            if (data.grades_vs_assignments) {
                createScatterChart('assignmentChart', 'Grades vs Assignments Completed',
                    data.grades_vs_assignments, 'Previous Grades %', 'Assignments Completed %');
            }

            if (data.feature_importance) {
                createFeatureImportanceChart(data.feature_importance);
            }

            if (data.major_distribution) {
                createHorizontalBarChart('majorChart', 'Students by Major', data.major_distribution);
            }

            document.getElementById('analyticsAlert').innerHTML = '';
        } else {
            document.getElementById('analyticsAlert').innerHTML =
                '<div class="alert alert-warning">⚠️ No analytics data available</div>';
        }
    } catch (error) {
        console.error(error);
        document.getElementById('analyticsAlert').innerHTML =
            '<div class="alert alert-danger">❌ Failed to load analytics</div>';
    }
}

// --- Students List ---

async function loadStudents() {
    try {
        const response = await fetch(`${API_URL}/students`);
        const data = await response.json();

        if (data.students && data.students.length > 0) {
            allStudents = data.students;
            renderStudentTable(allStudents);
        } else {
            document.getElementById('studentTable').innerHTML =
                '<div class="alert alert-warning">⚠️ No student data available</div>';
        }
    } catch (error) {
        document.getElementById('studentTable').innerHTML =
            '<div class="alert alert-danger">❌ Failed to load students</div>';
    }
}

function renderStudentTable(students) {
    const tableContainer = document.getElementById('studentTable');

    // Pagination logic could go here, but for now we render all (capped or virtualized in real app)
    // Limiting to first 100 for performance if list is huge
    const displayStudents = students.slice(0, 500);

    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Major</th>
                    <th>Year</th>
                    <th>Attendance</th>
                    <th>Study Hours</th>
                    <th>Prev. Grades</th>
                    <th>Performance</th>
                    <th>Risk Level</th>
                </tr>
            </thead>
            <tbody>
    `;

    displayStudents.forEach(s => {
        html += `
            <tr>
                <td style="font-family: monospace; font-weight: 600;">${s.student_id}</td>
                <td>${s.major || '-'}</td>
                <td>${s.year_of_study || '-'}</td>
                <td>${s.attendance.toFixed(1)}%</td>
                <td>${s.study_hours.toFixed(1)}h</td>
                <td>${s.previous_grades.toFixed(1)}%</td>
                <td style="font-weight: bold;">${s.performance.toFixed(1)}%</td>
                <td><span class="risk-badge risk-${s.risk_level.toLowerCase()}">${s.risk_level}</span></td>
            </tr>
        `;
    });

    html += '</tbody></table>';

    if (students.length > 500) {
        html += `<div style="padding: 10px; text-align: center; color: #666;">Showing first 500 of ${students.length} students</div>`;
    }

    tableContainer.innerHTML = html;
}

window.filterStudents = function () {
    const searchTerm = document.getElementById('searchStudent').value.toLowerCase();
    const riskFilter = document.getElementById('riskFilter').value;

    const filtered = allStudents.filter(s => {
        const matchesSearch = s.student_id.toLowerCase().includes(searchTerm) ||
            (s.major && s.major.toLowerCase().includes(searchTerm));
        const matchesRisk = riskFilter === '' || s.risk_level === riskFilter;
        return matchesSearch && matchesRisk;
    });

    renderStudentTable(filtered);
}

window.exportData = function () {
    window.location.href = `${API_URL}/export`;
}

// --- Charts ---

function createPerformanceChart(dist) {
    const ctx = document.getElementById('performanceChart');
    if (charts.performance) charts.performance.destroy();

    charts.performance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(dist),
            datasets: [{
                label: 'Students',
                data: Object.values(dist),
                backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#6366f1'],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, grid: { display: true, color: '#f1f5f9' } }, x: { grid: { display: false } } }
        }
    });
}

function createRiskChart(dist) {
    const ctx = document.getElementById('riskChart');
    if (charts.risk) charts.risk.destroy();

    // Define colors for each risk level
    const riskColors = {
        'High': '#ef4444',
        'Medium': '#eab308',
        'Low': '#10b981'
    };

    charts.risk = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(dist),
            datasets: [{
                data: Object.values(dist),
                // Map the labels (keys) to their corresponding colors
                backgroundColor: Object.keys(dist).map(key => riskColors[key] || '#cccccc'),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right' } }
        }
    });
}

function createDoughnutChart(canvasId, dist) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(dist),
            datasets: [{
                data: Object.values(dist),
                backgroundColor: ['#cbd5e1', '#6366f1', '#4338ca'], // Light, Main, Dark Blue for levels
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'right' } }
        }
    });
}

function createScatterChart(canvasId, title, data, xLabel, yLabel) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) charts[canvasId].destroy();

    charts[canvasId] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: title,
                data: data,
                backgroundColor: 'rgba(99, 102, 241, 0.5)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { title: { display: true, text: xLabel }, grid: { color: '#f1f5f9' } },
                y: { title: { display: true, text: yLabel }, grid: { color: '#f1f5f9' } }
            }
        }
    });
}

function createHorizontalBarChart(canvasId, title, data) {
    const ctx = document.getElementById(canvasId);
    if (charts[canvasId]) charts[canvasId].destroy();

    // Sort data
    const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(i => i[0]),
            datasets: [{
                label: 'Students',
                data: sorted.map(i => i[1]),
                backgroundColor: '#3b82f6',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function createFeatureImportanceChart(data) {
    const ctx = document.getElementById('featureChart');
    if (charts.features) charts.features.destroy();

    // Sort data
    const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);

    charts.features = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(i => formatLabel(i[0])),
            datasets: [{
                label: 'Importance',
                data: sorted.map(i => i[1]),
                backgroundColor: '#8b5cf6',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function formatLabel(str) {
    return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function generateSmartAlerts(inputs, score) {
    const alerts = [];

    // Attendance Checking
    if (inputs.attendance < 70) {
        alerts.push({
            type: 'alert-danger',
            message: '🚨 <strong>Critical Attendance:</strong> Below 70% threshold. Immediate counseling required.'
        });
    } else if (inputs.attendance < 85) {
        alerts.push({
            type: 'alert-warning',
            message: '⚠️ <strong>Attendance Warning:</strong> Falling behind. Monitor closely.'
        });
    }

    // Study Efficiency (High Hours but Low Performance)
    if (inputs.study_hours > 15 && score < 60) {
        alerts.push({
            type: 'alert-info',
            message: '💡 <strong>Efficiency Check:</strong> Student is studying a lot (>15h) but performance is low. Review study methods.'
        });
    }

    // High Performer Check
    if (score > 90) {
        alerts.push({
            type: 'alert-success',
            message: '🌟 <strong>Top Talent:</strong> Potential candidate for mentorship programs or advanced placement.'
        });
    }

    // Assignments
    if (inputs.assignments_completed < 80) {
        alerts.push({
            type: 'alert-warning',
            message: '📝 <strong>Missing Work:</strong> Assignment completion is low. Check for blockers.'
        });
    }

    return alerts;
}
