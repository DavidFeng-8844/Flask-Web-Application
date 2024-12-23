from datetime import datetime, date, timedelta
from unittest import case
from flask import redirect, render_template, flash, request, url_for
from app import flask_todo, db
from app.forms import CalculatorForm, RegistrationForm, LoginForm
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

# To do Route Handlers
############################################################################################################

@flask_todo.route("/")
def todo():
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    importance_filter = request.args.get('importance', 'all')
    deadline_filter = request.args.get('deadline', 'all')
    sort_by = request.args.get('sort_by', 'all')  # deadline, importance, created

    # Base query
    base_query = Todo.query

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
            'all': Todo.query.count(),
            'active': Todo.query.filter_by(completed=False).count(),
            'completed': Todo.query.filter_by(completed=True).count()
        },
        'importance': {
            'all': Todo.query.count(),
            'high': Todo.query.filter_by(importance='high').count(),
            'medium': Todo.query.filter_by(importance='medium').count(),
            'low': Todo.query.filter_by(importance='low').count()
        },
        'deadline': {
            'all': Todo.query.filter(Todo.deadline != None).count(),
            'overdue': Todo.query.filter(Todo.deadline < today, Todo.completed == False).count(),
            'today': Todo.query.filter(Todo.deadline == today).count(),
            'week': Todo.query.filter(Todo.deadline >= today, Todo.deadline <= today + timedelta(days=7)).count()
        }
    }


    todos = base_query.all()

    return render_template('todo.html',
                         todos=todos,
                         status_filter=status_filter,
                         importance_filter=importance_filter,
                         deadline_filter=deadline_filter,
                         sort_by=sort_by,
                         counts=counts,
                         title='Todo List')

@flask_todo.route("/todo/add", methods=['POST'])
def add_todo():
    content = request.form.get('todo_item')
    deadline_str = request.form.get('deadline')
    importance=request.form.get('importance')

    if content:
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None
            todo = Todo(
                content=content,
                deadline=deadline,
                importance=importance,
                user_id=1  
            )
            db.session.add(todo)
            db.session.commit()
            flash('Todo added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the todo.', 'danger')
    else:
        flash('Todo content cannot be empty!', 'warning')

    # Preserve filters when redirecting
    return redirect(url_for('todo', 
                          status=request.args.get('status', 'all'),
                          importance=request.args.get('importance', 'all'),
                          deadline=request.args.get('deadline', 'all'),
                          sort=request.args.get('sort', 'deadline')))

@flask_todo.route("/todo/edit/<int:todo_id>", methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_content = request.form.get('edited_todo')
    new_deadline = request.form.get('edited_deadline')
    new_importance = int(request.form.get('edited_importance'))

    if new_content:
        try:
            todo.content = new_content
            todo.deadline = datetime.strptime(new_deadline, '%Y-%m-%d').date() if new_deadline else None
            todo.importance = new_importance
            db.session.commit()
            flash('Todo updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the todo.', 'danger')
    else:
        flash('Todo content cannot be empty!', 'warning')

    return redirect(url_for('todo', 
                          status=request.args.get('status'),
                          importance=request.args.get('importance'),
                          deadline=request.args.get('deadline'),
                          sort=request.args.get('sort')))

# Toggle and Delete routes 

@flask_todo.route("/todo/delete/<int:todo_id>", methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('todo', 
                          status=request.args.get('status', 'all'),
                          importance=request.args.get('importance', 'all'),
                          deadline=request.args.get('deadline', 'all'),
                          sort=request.args.get('sort', 'deadline')))

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


