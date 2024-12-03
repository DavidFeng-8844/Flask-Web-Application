document.addEventListener("DOMContentLoaded", function () {
    // Retrieve the chart data from the dataset attributes
    var statusData = JSON.parse(document.getElementById('statusChartData').textContent);
    var priorityData = JSON.parse(document.getElementById('priorityChartData').textContent);
    var deadlineData = JSON.parse(document.getElementById('deadlineChartData').textContent);

    // Initial Chart Setup (Status as default)
    var ctx = document.getElementById('projectStatusChart').getContext('2d');
    var noDataMessage = document.getElementById('noDataMessage');
    var chartContainer = document.getElementById('projectStatusChart');

    function renderChart(chartData) {
        if (chartData.data.every(val => val === 0)) {
            // No data, hide the chart and show the message
            chartContainer.style.display = 'none';
            noDataMessage.style.display = 'block';
        } else {
            // There is data, show the chart and hide the message
            chartContainer.style.display = 'block';
            noDataMessage.style.display = 'none';

            chart.data.labels = chartData.labels;
            chart.data.datasets[0].data = chartData.data;
            chart.data.datasets[0].backgroundColor = chartData.backgroundColors;

            chart.update();
        }
    }

    var chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: statusData.labels,
            datasets: [{
                data: statusData.data,
                backgroundColor: statusData.backgroundColors
            }]
        }
    });

    // Handle Chart Toggle
    document.getElementById('chartSelector').addEventListener('change', function () {
        var selectedChart = this.value;
        var chartData;
        if (selectedChart === 'status') {
            chartData = statusData;
        } else if (selectedChart === 'priority') {
            chartData = priorityData;
        } else if (selectedChart === 'deadline') {
            chartData = deadlineData;
        }

        // Render the appropriate chart or show "no data" message
        renderChart(chartData);
    });

    // Render the initial chart (status by default)
    renderChart(statusData);
});
