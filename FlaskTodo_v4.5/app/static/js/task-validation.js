// console.log("task_validation.js loaded");
document.addEventListener('DOMContentLoaded', function () {
    // Select the forms for both add and edit modals
    const addTaskForm = document.querySelector('#addTodoModal form');
    const editTaskForms = document.querySelectorAll('.editTodoModal form'); // Assuming multiple edit forms
    const newTaskForm = document.querySelector('form');  // Select the form element


    // Regular expression for module code validation (e.g., XJCO2011)
    const moduleCodeRegex = /^[A-Z]{4}[0-9]{4}$/;

    function validateTaskForm(form) {
        const title = form.querySelector('input[name="title"]').value.trim(); // Make sure to remove the leading and trailing whitespaces
        const moduleCode = form.querySelector('input[name="module_code"]').value;
        const deadline = form.querySelector('input[name="deadline"]').value;
        let valid = true;

        // Clear previous error messages
        form.querySelectorAll('.error-message').forEach(error => error.remove());

        // Title validation must not be empty and longer than 3 characters
        if (!title || title.length < 3) {
            showError(form.querySelector('input[name="title"]'), 'Title must be longer than 3 characters.');
            valid = false;
        }

        // Module code validation
        if (!moduleCodeRegex.test(moduleCode)) {
            showError(form.querySelector('input[name="module_code"]'), 'Module code must be in the format like XJCO2011.');
            valid = false;
        }

        // Deadline validation
        if (!deadline) {
            showError(form.querySelector('input[name="deadline"]'), 'Deadline is required.');
            valid = false;
        }

        return valid;
    }

    function showError(input, message) {
        const error = document.createElement('div');
        error.classList.add('error-message', 'text-danger');
        error.textContent = message;
        input.parentNode.appendChild(error);
    }

    // Add validation for add task form
    if (addTaskForm) {
        addTaskForm.addEventListener('submit', function (event) {
            if (!validateTaskForm(addTaskForm)) {
                event.preventDefault(); // Stop form submission if validation fails
            }
        });
    }

    // Add validation for each edit task form
    if (editTaskForms) {
        editTaskForms.forEach(form => {
            form.addEventListener('submit', function (event) {
                if (!validateTaskForm(form)) {
                    event.preventDefault(); // Stop form submission if validation fails
                }
            });
        });
    }

    if (newTaskForm) {
        newTaskForm.addEventListener('submit', function (event) {
            if (!validateTaskForm(newTaskForm)) {
                event.preventDefault();  // Stop form submission if validation fails
            }
        });
    }

});
