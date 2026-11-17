let chartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    loadStudents();
    loadAnalysis();

    document.getElementById('studentForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const studentData = {
            roll_no: document.getElementById('roll_no').value,
            name: document.getElementById('name').value,
            python: document.getElementById('python').value,
            dbms: document.getElementById('dbms').value,
            java: document.getElementById('java').value,
            web: document.getElementById('web').value,
            ai: document.getElementById('ai').value,
            classes_held: document.getElementById('classes_held').value,
            classes_attended: document.getElementById('classes_attended').value
        };

        const res = await fetch('/api/add_student', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(studentData)
        });

        const result = await res.json();
        alert(result.message);
        if (result.success) {
            document.getElementById('studentForm').reset();
            loadStudents();
            loadAnalysis();
        }
    });
});

async function loadStudents() {
    const res = await fetch('/api/students');
    const students = await res.json();
    
    const tbody = document.querySelector('#studentsTable tbody');
    tbody.innerHTML = '';

    const names = [];
    const percentages = [];

    students.forEach(s => {
        names.push(s['Name']);
        percentages.push(s['Percentage']);

        const row = `<tr>
            <td>${s['Roll No']}</td>
            <td>${s['Name']}</td>
            <td>${s['Total']}</td>
            <td>${s['Average']}</td>
            <td>${s['Percentage']}%</td>
            <td>${s['Grade']}</td>
            <td>${s['Attendance']}%</td>
        </tr>`;
        tbody.innerHTML += row;
    });

    renderChart(names, percentages);
}

async function loadAnalysis() {
    const res = await fetch('/api/analysis');
    const data = await res.json();
    const statsGrid = document.getElementById('statsGrid');
    
    if (!data.has_data) return;

    statsGrid.innerHTML = `
        <div class="stat-box"><h3>Total Students</h3><p>${data.total_students}</p></div>
        <div class="stat-box"><h3>Class Average</h3><p>${data.class_avg}%</p></div>
        <div class="stat-box"><h3>Topper</h3><p>${data.topper}</p></div>
        <div class="stat-box"><h3>Passed / Failed</h3><p>${data.passed} / ${data.failed}</p></div>
    `;
}

function renderChart(labels, data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Student Percentage (%)',
                data: data,
                backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}