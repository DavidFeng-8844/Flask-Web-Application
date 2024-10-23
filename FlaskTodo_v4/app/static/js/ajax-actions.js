$(document).ready(function() {
    // Handle AJAX form submission
    $(".ajax-form").on("submit", function(event) {
        event.preventDefault(); // Prevent the default form submission

        var form = $(this);
        var taskId = form.data("id");
        var formAction = form.attr("action");

        // Send the AJAX request
        $.ajax({
            type: "POST",
            url: formAction,
            success: function(response) {
                // Remove the task from the recycle bin list dynamically
                $("#todo-" + taskId).fadeOut(300, function() {
                    $(this).remove();
                });
            },
            error: function(xhr, status, error) {
                // Optionally handle errors here
                alert("An error occurred: " + error);
            }
        });
    });
});
