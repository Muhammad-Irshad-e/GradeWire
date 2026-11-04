function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    const activeSection = document.getElementById(sectionId);
    if (activeSection) {
        activeSection.classList.add('active');
    }
}





function searchStudent() {
    const searchInput = document.getElementById('searchStudent');
    const tableBody = document.getElementById('studentTableBody');
    if (!searchInput || !tableBody) return;

    const searchValue = searchInput.value.toLowerCase();
    const tableRows = tableBody.querySelectorAll('tr');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const cancelSearchButton = document.getElementById('cancelSearch');
    let matchFound = false;

    tableRows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length === 0) return;
        const searchableCells = cells.slice(0, cells.length - 1);
        const rowText = searchableCells.map(cell => cell.textContent.toLowerCase()).join(' ');

        if (rowText.includes(searchValue)) {
            row.style.display = '';
            matchFound = true;
        } else {
            row.style.display = 'none';
        }
    });

    if (noResultsMessage) {
        noResultsMessage.style.display = (!matchFound && searchValue !== '') ? 'block' : 'none';
    }
    if (cancelSearchButton) {
        cancelSearchButton.style.display = (searchValue !== '') ? 'inline' : 'none';
    }
}

function searchTeacher() {
    const searchInput = document.getElementById('searchTeacher');
    const tableBody = document.getElementById('teacherTableBody');
    if (!searchInput || !tableBody) return;

    const searchValue = searchInput.value.toLowerCase();
    const tableRows = tableBody.querySelectorAll('tr');
    const noResultsMessage = document.getElementById('noTeacherResultsMessage');
    const cancelSearchButton = document.getElementById('cancelTeacherSearch');
    let matchFound = false;

    tableRows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length === 0) return;
        const searchableCells = cells.slice(0, cells.length - 1);
        const rowText = searchableCells.map(cell => cell.textContent.toLowerCase()).join(' ');

        if (rowText.includes(searchValue)) {
            row.style.display = '';
            matchFound = true;
        } else {
            row.style.display = 'none';
        }
    });

    if (noResultsMessage) {
        noResultsMessage.style.display = (!matchFound && searchValue !== '') ? 'block' : 'none';
    }
    if (cancelSearchButton) {
        cancelSearchButton.style.display = (searchValue !== '') ? 'inline' : 'none';
    }
}

// Initializing the charts safely only if the canvas element exists
const studentsCourseChartEl = document.getElementById('studentsCourseChart');
if (studentsCourseChartEl && typeof Chart !== 'undefined') {
    const studentsCourseChartCtx = studentsCourseChartEl.getContext('2d');
    new Chart(studentsCourseChartCtx, {
        type: 'bar',
        data: {
            labels: ['Course 1', 'Course 2', 'Course 3', 'Course 4'],
            datasets: [{
                label: 'Number of Students',
                data: [30, 25, 40, 25],
                backgroundColor: '#1e90ff',
            }]
        }
    });
}