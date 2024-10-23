from datetime import datetime, date, timedelta
from unittest import case
from flask import jsonify, redirect, render_template, flash, request, url_for
from app import flask_todo, db
from app.forms import CalculatorForm, RegistrationForm, LoginForm, TaskForm
from app.models import User, Post, Todo


@flask_todo.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success') # success is a bootstrap class
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@flask_todo.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'el22y2f@leeds.ac.uk' and form.password.data == '123456':
            flash(f'Account logged in for {form.email.data}!', 'success')
        else:
            flash(f'Login Unsuccessful. Please check username and password', 'danger')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


def get_counts():
    today = date.today()
    return {
        'status': {
            'all': Todo.query.filter_by(soft_delete=False).count(),
            'active': Todo.query.filter_by(completed=False, soft_delete=False).count(),
            'completed': Todo.query.filter_by(completed=True, soft_delete=False).count()
        },
        'importance': {
            'all': Todo.query.filter_by(soft_delete=False).count(),
            'high': Todo.query.filter_by(importance='high', soft_delete=False).count(),
            'medium': Todo.query.filter_by(importance='medium', soft_delete=False).count(),
            'low': Todo.query.filter_by(importance='low', soft_delete=False).count()
        },
        'deadline': {
            'all': Todo.query.filter(Todo.deadline != None).filter_by(soft_delete=False).count(),
            'overdue': Todo.query.filter(Todo.deadline < today, Todo.completed == False).filter_by(soft_delete=False).count(),
            'today': Todo.query.filter(Todo.deadline == today).filter_by(soft_delete=False).count(),
            'week': Todo.query.filter(Todo.deadline >= today, Todo.deadline <= today + timedelta(days=7)).filter_by(soft_delete=False).count()
        }
    }


@flask_todo.route("/")
def todo():
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    importance_filter = request.args.get('importance', 'all')
    deadline_filter = request.args.get('deadline', 'all')
    sort_by = request.args.get('sort_by', 'all')  # deadline, importance, created

    # Base query
    base_query = Todo.query.filter_by(soft_delete=False)

    # Status filter
    if status_filter == 'completed':
        base_query = base_query.filter_by(completed=True)
    elif status_filter == 'active':
        base_query = base_query.filter_by(completed=False)

    # Importance filter 
    if importance_filter in ['high', 'medium', 'low']:
        base_query = base_query.filter_by(importance=importance_filter)


    # Deadline filter
    today = date.today()
    if deadline_filter == 'overdue':
        base_query = base_query.filter(Todo.deadline < today, Todo.completed == False)
    elif deadline_filter == 'today':
        base_query = base_query.filter(Todo.deadline == today)
    elif deadline_filter == 'week':
        base_query = base_query.filter(Todo.deadline <= today + timedelta(days=7))

    # Sorting for three different filter
    if sort_by == 'deadline':
        base_query = base_query.order_by(Todo.deadline.asc().nulls_last())
    elif sort_by == 'importance':
        importance_order = db.case(
            (Todo.importance == 'high', 1),
            (Todo.importance == 'medium', 2),
            (Todo.importance == 'low', 3)
        )
        base_query = base_query.order_by(importance_order)
    else:
        base_query = base_query.order_by(Todo.date_created.desc())

    # Get counts for filters
    counts = {
        'status': {
            'all': Todo.query.filter_by(soft_delete=False).count(),
            'active': Todo.query.filter_by(completed=False, soft_delete=False).count(),
            'completed': Todo.query.filter_by(completed=True, soft_delete=False).count()
        },
        'importance': {
            'all': Todo.query.filter_by(soft_delete=False).count(),
            'high': Todo.query.filter_by(importance='high', soft_delete=False).count(),
            'medium': Todo.query.filter_by(importance='medium', soft_delete=False).count(),
            'low': Todo.query.filter_by(importance='low', soft_delete=False).count()
        },
        'deadline': {
            'all': Todo.query.filter(Todo.deadline != None).filter_by(soft_delete=False).count(),
            'overdue': Todo.query.filter(Todo.deadline < today, Todo.completed == False).filter_by(soft_delete=False).count(),
            'today': Todo.query.filter(Todo.deadline == today).filter_by(soft_delete=False).count(),
            'week': Todo.query.filter(Todo.deadline >= today, Todo.deadline <= today + timedelta(days=7)).filter_by(soft_delete=False).count()
        }
    }
    todos = base_query.all()
    
    # Check if the request is an AJAX request
    # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    #     # Render only the todo list part if it's an AJAX request
    #     return render_template('_todo_list.html', todos=todos)
    
    return render_template('todo.html',
                         form = TaskForm(),
                         todos=todos,
                         status_filter=status_filter,
                         importance_filter=importance_filter,
                         deadline_filter=deadline_filter,
                         sort_by=sort_by,
                         counts=counts,
                         title='Todo List')


@flask_todo.route("/todo/add", methods=['GET', 'POST'])
def add_todo():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            todo = Todo(
                title=form.title.data,
                module_code=form.module_code.data,
                description=form.description.data,
                deadline=form.deadline.data,
                importance=form.importance.data,
                user_id=1  # Assuming the user is logged in with user_id=1 for example
            )
            db.session.add(todo)
            db.session.commit()
            flash('New task has been added!', 'success')
            return redirect(url_for('todo'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the todo.', 'danger')

    return redirect(url_for('todo', form=form, title='Add Task'))


@flask_todo.route("/todo/edit/<int:todo_id>", methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    form = TaskForm()

    if form.validate_on_submit():
        try:
            todo.title = form.title.data
            todo.module_code = form.module_code.data
            todo.description = form.description.data
            todo.deadline = form.deadline.data
            todo.importance = form.importance.data
            db.session.commit()
            flash('Todo updated successfully!', 'success')
            return redirect(url_for('todo'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the todo.', 'danger')
    elif request.method == 'GET':
        # Pre-populate the form with existing data
        form.title.data = todo.title
        form.module_code.data = todo.module_code
        form.description.data = todo.description
        form.deadline.data = todo.deadline
        form.importance.data = todo.importance

    return redirect(url_for('todo', form=form, title='Edit Task'))

# Toggle and Delete routes 

# @flask_todo.route("/todo/delete/<int:todo_id>", methods=['POST'])
# def delete_todo(todo_id):
#     todo = Todo.query.get_or_404(todo_id)
#     db.session.delete(todo)
#     db.session.commit()
#     flash('Todo deleted successfully!', 'success')
#     return redirect(url_for('todo', 
#                           status=request.args.get('status', 'all'),
#                           importance=request.args.get('importance', 'all'),
#                           deadline=request.args.get('deadline', 'all'),
#                           sort=request.args.get('sort', 'deadline')))

# Soft Delete route
@flask_todo.route('/todo/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    # Mark the task as soft-deleted
    todo.soft_delete = True
    db.session.commit()
    flash('Task moved to Recycle Bin.', 'success')
    return redirect(url_for('todo'))

@flask_todo.route('/recycle_bin')
def recycle_bin():
    # Fetch all tasks that are soft-deleted
    deleted_todos = Todo.query.filter_by(soft_delete=True).all()
    return render_template('recycle_bin.html', todos=deleted_todos, title="Recycle Bin", counts=get_counts())


# Restore and Permanent Delete routes
# @flask_todo.route('/todo/restore/<int:todo_id>', methods=['POST'])
# def restore_todo(todo_id):
#     todo = Todo.query.get_or_404(todo_id)
#     # Mark the task as not deleted
#     todo.soft_delete = False
#     db.session.commit()
#     flash('Task restored successfully!', 'success')
#     return redirect(url_for('recycle_bin'))

# @flask_todo.route('/todo/permanent_delete/<int:todo_id>', methods=['POST'])
# def permanent_delete(todo_id):
#     todo = Todo.query.get_or_404(todo_id)
#     db.session.delete(todo)
#     db.session.commit()
#     flash('Task permanently deleted.', 'danger')
#     return redirect(url_for('recycle_bin'))

# using ajax to delete
@flask_todo.route('/todo/restore/<int:todo_id>', methods=['POST'])
def restore_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.soft_delete = False
    db.session.commit()
    return '', 204  # No content, just a success response for AJAX

@flask_todo.route('/todo/permanent_delete/<int:todo_id>', methods=['POST'])
def permanent_delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return '', 204  # No content, just a success response for AJAX



@flask_todo.route("/todo/toggle/<int:todo_id>", methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    flash(f'Task {"completed" if todo.completed else "reopened"}!', 'success')
    return redirect(url_for('todo', 
                          status=request.args.get('status', 'all'),
                          importance=request.args.get('importance', 'all'),
                          deadline=request.args.get('deadline', 'all'),
                          sort=request.args.get('sort', 'deadline')))


# New Task Route Handler

@flask_todo.route('/task/new', methods=['GET', 'POST'])
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            todo = Todo(
                title=form.title.data,
                module_code=form.module_code.data,
                description=form.description.data,
                deadline=form.deadline.data,
                importance=form.importance.data,
                user_id=1  # Assuming a logged-in user with ID 1 for this example
            )
            db.session.add(todo)
            db.session.commit()
            flash('New task has been added!', 'success')
            return redirect(url_for('todo'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding task.', 'danger')
    return render_template('new_task.html', title='Add Task', form=form, counts = get_counts())

# Copy Task button 
@flask_todo.route('/todo/copy/<int:todo_id>', methods=['POST'])
def copy_todo(todo_id):
    # Fetch the original todo item
    original_todo = Todo.query.get_or_404(todo_id)
    
    # Create a new todo item by copying fields from the original one
    new_todo = Todo(
        title=original_todo.title + " (Copy)",  # Modify title to indicate it's a copy
        module_code=original_todo.module_code,
        description=original_todo.description,
        deadline=original_todo.deadline,
        importance=original_todo.importance,
        user_id=original_todo.user_id  # Keep the same user ID
    )
    
    # Add the new todo to the database
    db.session.add(new_todo)
    db.session.commit()
    
    flash(f'Task "{original_todo.title}" copied successfully!', 'success')
    return redirect(url_for('todo'))

# routes for calender
@flask_todo.route('/calendar')
def calendar():
    return render_template('calendar.html', counts = get_counts())

@flask_todo.route('/api/tasks')
def get_tasks():
    tasks = Todo.query.filter(Todo.deadline != None, Todo.soft_delete == False).all()
    
    # Convert tasks to a JSON-friendly format
    events = []
    for task in tasks:
        events.append({
            'title': task.title,
            'start': task.deadline.strftime('%Y-%m-%d'),
            'description': task.description,
        })
    
    return jsonify(events)
