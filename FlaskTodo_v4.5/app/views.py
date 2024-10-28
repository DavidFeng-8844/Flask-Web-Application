from datetime import date, timedelta
from flask import jsonify, redirect, render_template, flash, request, url_for
from app import flask_todo, db
from app.forms import RegistrationForm, LoginForm, TaskForm
from app.models import Todo
from sqlalchemy.exc import SQLAlchemyError

def get_counts():

    today = date.today()

    # Calculate the start (Monday) and end (Sunday) of the current week
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)  # Sunday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Move to the first day of the next month, then subtract a day to get the last day of the current month
    first_day_next_month = (today.replace(day=1) + timedelta(days=31)).replace(day=1)
    end_of_month = first_day_next_month - timedelta(days=1)

    return {    
        'status': {
            'all': Todo.query.filter_by(soft_delete=False).count(),
            'active': Todo.query.filter_by(completed=False, soft_delete=False).count(),
            'completed': Todo.query.filter_by(completed=True, soft_delete=False).count()
        },
        'importance': {
            'all': Todo.query.filter(Todo.completed == False).filter_by(soft_delete=False).count(),
            'high': Todo.query.filter(Todo.completed == False).filter_by(importance='high', soft_delete=False).count(),
            'medium': Todo.query.filter(Todo.completed == False).filter_by(importance='medium', soft_delete=False).count(),
            'low': Todo.query.filter(Todo.completed == False).filter_by(importance='low', soft_delete=False).count()
        },
        'deadline': {
            'all': Todo.query.filter(Todo.deadline != None, Todo.completed == False).filter_by(soft_delete=False).count(),
            'overdue': Todo.query.filter(Todo.deadline < today, Todo.completed == False).filter_by(soft_delete=False).count(),
            'today': Todo.query.filter(Todo.deadline == today, Todo.completed == False).filter_by(soft_delete=False).count(),
            'week': Todo.query.filter(Todo.deadline > today, Todo.deadline <= end_of_week, Todo.completed == False).filter_by(soft_delete=False).count(),
            'month': Todo.query.filter(Todo.deadline >= end_of_week, Todo.deadline <= end_of_month, Todo.completed == False).filter_by(soft_delete=False).count(),
            'future': Todo.query.filter(Todo.deadline > end_of_month, Todo.completed == False).filter_by(soft_delete=False).count()
        }
    }

def filter_redirect(todo):
    current_status = request.form.get('status')
    current_importance = request.form.get('importance')
    current_deadline = request.form.get('deadline')
    print(f'----------------{current_status}------------------', flush=True) 
    print(f'----------------{current_importance}---------------', flush=True)
    print(f'----------------{current_deadline}------------------', flush=True)
    if current_status == 'completed':
        return redirect(url_for('todo', status='completed'))
    elif current_status == 'active' and current_importance == '' and current_deadline == '':
        return redirect(url_for('todo', status='active'))
    elif current_status == 'all' and current_importance == '' and current_deadline == '':
        return redirect(url_for('todo', status='all'))
    elif current_importance == 'all' and current_deadline == '':
        return redirect(url_for('todo', importance='all'))
    elif current_importance == 'high':
        return redirect(url_for('todo', importance='high'))
    elif current_importance == 'medium':
        return redirect(url_for('todo', importance='medium'))
    elif current_importance == 'low':
        return redirect(url_for('todo', importance='low'))
    elif current_deadline == 'all':
        return redirect(url_for('todo', deadline='all'))
    elif current_deadline == 'overdue':
        return redirect(url_for('todo', deadline='overdue'))
    elif current_deadline == 'today':
        return redirect(url_for('todo', deadline='today'))
    elif current_deadline == 'week':
        return redirect(url_for('todo', deadline='week'))
    elif current_deadline == 'month':
        return redirect(url_for('todo', deadline='month'))
    elif current_deadline == 'future':
        return redirect(url_for('todo', deadline='future'))
    else:   
        return redirect(url_for('todo'))

@flask_todo.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success') # success is a bootstrap class
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form, counts = get_counts())

@flask_todo.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'el22y2f@leeds.ac.uk' and form.password.data == '123456':
            flash(f'Account logged in for {form.email.data}!', 'success')
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form, counts = get_counts())


@flask_todo.route("/")
def todo():
    # Get filter parameters
    status_filter = request.args.get('status', 'active')
    importance_filter = request.args.get('importance', 'all')
    deadline_filter = request.args.get('deadline', '')
    sort_by = request.args.get('sort_by', 'all')  # importance, created

    # Base query
    base_query = Todo.query.filter_by(soft_delete=False)

    # Status filter
    if status_filter == 'all':
        base_query = base_query
    elif status_filter == 'completed':
        base_query = base_query.filter_by(completed=True)
    elif status_filter == 'active':
        base_query = base_query.filter_by(completed=False)

    # Importance filter
    if importance_filter in ['high', 'medium', 'low']:
        base_query = base_query.filter(Todo.completed == False)
        base_query = base_query.filter_by(importance=importance_filter)
        base_query = base_query.order_by(Todo.deadline)

    # Deadline filter
    today = date.today()

    # Calculate the start (Monday) and end (Sunday) of the current week
    start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)  # Sunday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    # Move to the first day of the next month, then subtract a day to get the last day of the current month
    first_day_next_month = (today.replace(day=1) + timedelta(days=31)).replace(day=1)
    end_of_month = first_day_next_month - timedelta(days=1)

    if deadline_filter == 'all':
        base_query = base_query.filter(Todo.deadline != None, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)
    elif deadline_filter == 'overdue':
        base_query = base_query.filter(Todo.deadline < today, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)
    elif deadline_filter == 'today':
        base_query = base_query.filter(Todo.deadline == today, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)
    elif deadline_filter == 'week':
        base_query = base_query.filter(Todo.deadline > today, Todo.deadline <= end_of_week, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)
    elif deadline_filter == 'month':
        base_query = base_query.filter(Todo.deadline > end_of_week, Todo.deadline <= end_of_month, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)
    elif deadline_filter == 'future':
        base_query = base_query.filter(Todo.deadline > end_of_month, Todo.completed == False)
        base_query = base_query.order_by(Todo.deadline)


    # Sorting for three different filter
    if sort_by == 'importance':
        importance_order = db.case(
            (Todo.importance == 'high', 1),
            (Todo.importance == 'medium', 2),
            (Todo.importance == 'low', 3)
        )
        base_query = base_query.filter(Todo.completed == False)
        base_query = base_query.order_by(importance_order)
    else:
        base_query = base_query.order_by(Todo.date_created.desc())

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
                         counts=get_counts(),
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
                user_id=1  # Assuming the user is logged in with user_id=1
            )
            db.session.add(todo)
            db.session.commit()
            flash('New task has been added!', 'success')
            return redirect(url_for('todo'))
        except SQLAlchemyError:
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
        except SQLAlchemyError:
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

# Soft Delete route
@flask_todo.route('/todo/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    # Mark the task as soft-deleted
    todo.soft_delete = True
    db.session.commit()
    flash(f'Task "{todo.title}" moved to Recycle Bin.', 'success')
    return filter_redirect(todo)

@flask_todo.route('/recycle_bin')
def recycle_bin():
    # Fetch all tasks that are soft-deleted
    deleted_todos = Todo.query.filter_by(soft_delete=True).all()
    return render_template('recycle_bin.html', todos=deleted_todos, title="Recycle Bin", counts=get_counts())

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

# Delete all tasks in recycle bin using ajax
@flask_todo.route('/todo/delete_all', methods=['POST'])
def delete_all():
    Todo.query.filter_by(soft_delete=True).delete()
    db.session.commit()
    return redirect(url_for('recycle_bin'))

# delete all completed tasks
@flask_todo.route('/todo/delete_completed', methods=['POST'])
def delete_completed():
    Todo.query.filter_by(completed=True).delete()
    db.session.commit()
    flash('All completed tasks have been deleted.', 'success')
    return redirect(url_for('todo'))

@flask_todo.route("/todo/toggle/<int:todo_id>", methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    flash(f'Task "{todo.title}" {"completed" if todo.completed else "reopened"}!', 'success')
    return filter_redirect(todo)

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
        user_id=original_todo.user_id,  # Keep the same user ID
        completed=original_todo.completed
    )

    # Add the new todo to the database
    db.session.add(new_todo)
    db.session.commit()

    flash(f'Task "{original_todo.title}" copied successfully!', 'success')
    return filter_redirect(original_todo)

# routes for calender
@flask_todo.route('/calendar')
def calendar():
    return render_template('calendar.html', counts = get_counts(), title='Calendar')

@flask_todo.route('/api/tasks')
def get_tasks():
    tasks = Todo.query.filter(Todo.deadline != None, Todo.soft_delete == False).all()

    # Convert tasks to a JSON-friendly format
    events = []
    for task in tasks:
        events.append({
            'title': task.title,
            'start': task.deadline.strftime('%Y-%m-%d'),
            'module_code': task.module_code,
            'description': task.description,
            'importance': task.importance
        })

    return jsonify(events)