document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        dateCellDidMount: function(info) {
            // Hide cells for dates outside the current month
            if (info.date.getMonth() !== new Date().getMonth()) {
              info.el.setAttribute('aria-hidden', 'true');
            }
        },
        events: '/api/tasks',  // Fetch task events from your Flask route
        eventClick: function (info) {
            // Prevent the default alert popup
            info.jsEvent.preventDefault();
            // Display the custom popup
            var popup = document.getElementById("taskPopup");
            document.getElementById("popupTitle").querySelector("span").textContent = info.event.title;
            document.getElementById("popupModuleCode").querySelector("span").textContent = info.event.extendedProps.module_code;
            document.getElementById("popupDescription").textContent =
                "Description: " + (info.event.extendedProps.description || "No description available");
            document.getElementById("popupDeadline").querySelector("span").textContent = info.event.startStr;
            document.getElementById("popupImportance").querySelector("span").textContent = info.event.extendedProps.importance;

            // Handle importance text and color
            var importanceElement = document.getElementById("popupImportance").querySelector("span");
            importanceElement.textContent = info.event.extendedProps.importance;

            // Remove any existing importance classes
            importanceElement.classList.remove("text-high", "text-medium", "text-low");

            // Add class based on importance level
            if (info.event.extendedProps.importance === 'high') {
                importanceElement.classList.add("text-high");
            } else if (info.event.extendedProps.importance === 'medium') {
                importanceElement.classList.add("text-medium");
            } else {
                importanceElement.classList.add("text-low");
            }

            popup.style.display = "block";
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,dayGridWeek,listMonth'
        },
        eventDidMount: function (info) {
            // Change color based on importance
            if (info.event.extendedProps.importance === 'high') {
                info.el.style.backgroundColor = '#dc3545';
            } else if (info.event.extendedProps.importance === 'medium') {
                info.el.style.backgroundColor = '#ffc107';
            } else {
                info.el.style.backgroundColor = '#17A2B8';
            }
        }
    });
    calendar.render();
    // Close the popup
    document.getElementById("closePopup").onclick = function () {
        document.getElementById("taskPopup").style.display = "none";
    }
});