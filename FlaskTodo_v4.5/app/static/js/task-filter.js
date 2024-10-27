// static/filter_tasks.js
function filterTasksByDeadline(selectElement) {
    const selectedDeadline = selectElement.value;
    
    // Redirect to apply the selected deadline filter
    const url = `${window.location.origin}${selectElement.dataset.url}?deadline=${selectedDeadline}`;
    window.location.href = url;
}
