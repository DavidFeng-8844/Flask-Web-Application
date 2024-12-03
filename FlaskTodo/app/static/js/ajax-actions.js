$(document).ready(function() {
    // Handle AJAX form submission for tasks (like delete or copy)
    $(".ajax-form").on("submit", function(event) {
        event.preventDefault(); // Prevent default form submission

        var form = $(this);
        var taskId = form.data("id");
        var formAction = form.attr("action");

        // Send AJAX request for form submission
        $.ajax({
            type: "POST",
            url: formAction,
            success: function(response) {
                // Remove the task from the list dynamically
                $("#todo-" + taskId).fadeOut(300, function() {
                    $(this).remove();
                });
            },
            error: function(xhr, status, error) {
                // Handle errors if necessary
                alert("An error occurred: " + error);
            }
        });
    });

    // Handle filter clicks with AJAX (for status, importance, and deadline)
    $(".filter-link").on("click", function(event) {
        event.preventDefault();  // Prevent default link behavior

        var status = $("#status-filter .active").data("filter-status") || 'all';
        var importance = $("#importance-filter .active").data("filter-importance") || 'all';
        var deadline = $("#deadline-filter .active").data("filter-deadline") || 'all';
        var sort_by = $("#sort-by-filter .active").data("filter-sort") || 'all';

        // Send AJAX request for filtering
        $.ajax({
            type: "GET",
            url: "/",  // Send the request to the root route
            data: {
                status: status,
                importance: importance,
                deadline: deadline,
                sort_by: sort_by
            },
            success: function(response) {
                // Update the task list with the new filtered content
                $("#todo-list").html(response);
            },
            error: function(xhr, status, error) {
                console.log("Error fetching tasks: " + error);
            }
        });

        // Update active class on the clicked filter
        $(this).siblings().removeClass('active');
        $(this).addClass('active');
    });
});
