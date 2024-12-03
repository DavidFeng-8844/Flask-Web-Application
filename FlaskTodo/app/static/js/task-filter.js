// static/filter_tasks.js
function filterTasksByDeadline() {
    const selectElement = document.getElementById('deadline-filter');
    const selectedDeadline = selectElement.value;
    
    // Check if a valid option is selected
    if (selectedDeadline) {
        // Construct the URL and redirect
        const url = `${window.location.origin}${selectElement.dataset.url}?deadline=${selectedDeadline}`;
        window.location.href = url;
    } else {
        alert('Please select a deadline filter.');
    }
}

function filterTasksByModuleCode() {
    const selectElement = document.getElementById('module-code-filter');
    const selectedModuleCode = selectElement.value;
    
    // Check if a valid option is selected
    if (selectedModuleCode) {
        // Construct the URL and redirect
        const url = `${window.location.origin}${selectElement.dataset.url}?module_code=${selectedModuleCode}`;
        window.location.href = url;
    } else {
        alert('Please select a module code filter.');
    }
}