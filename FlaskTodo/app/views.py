from datetime import datetime
from flask import redirect, render_template, flash, request, url_for
from app import web_blog, db
from app.forms import CalculatorForm, RegistrationForm, LoginForm
from app.models import User, Post, Todo


@web_blog.route('/calculator', methods=['GET', 'POST']) # decorator to tell Flask what URL should trigger the function
def calculator():
    form = CalculatorForm()
    if form.validate_on_submit():
        flash('Succesfully received form data. %s + %s  = %s'%(form.number1.data, form.number2.data, form.number1.data+form.number2.data))
    return render_template('calculator.html',
                           title='Calculator',
                           form=form)

@web_blog.route('/')
def index():
    user = {'name': 'Homer Simpson'}
    fruits = ["Apple", "Banana", "Orange", "Kiwi"]
    return render_template('index.html', title='Simple template example', user=user, fruits=fruits)

@web_blog.route('/fruit')
def fruit():
    fruits = [{"name": "apple", "color": "red", "shape": "round"}, {"name": "banana", "color": "yellow", "shape": "crescent"}, {"name": "orange", "color": "orange", "shape": "round"}, {"name": "kiwi", "color": "brown", "shape": "oval"}]
    return render_template("fruit_with_inheritance.html",fruits=fruits)

@web_blog.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success') # success is a bootstrap class
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@web_blog.route('/login', methods=['GET', 'POST'])
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
@web_blog.route("/todo")
def todo():
    # Get filter parameter from URL, default to 'all'
    filter_type = request.args.get('filter', 'all')
    
    # Base query
    base_query = Todo.query
    
    # Apply filters
    if filter_type == 'completed':
        todos = base_query.filter_by(completed=True)
    elif filter_type == 'active':
        todos = base_query.filter_by(completed=False)
    else:
        todos = base_query
    
    # Get counts for each category
    todos_count = {
        'all': base_query.count(),
        'active': base_query.filter_by(completed=False).count(),
        'completed': base_query.filter_by(completed=True).count()
    }
    
    # Get the filtered and ordered todos
    todos = todos.order_by(Todo.date_created.desc()).all()
    
    return render_template('todo.html', 
                         todos=todos, 
                         filter=filter_type,
                         todos_count=todos_count,
                         title='Todo List')

@web_blog.route("/todo/add", methods=['POST'])
def add_todo():
    content = request.form.get('todo_item')
    if content:
        todo = Todo(
            content=content,
            user_id=1  # Replace with current_user.id if using Flask-Login
        )
        try:
            db.session.add(todo)
            db.session.commit()
            flash('Todo added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the todo.', 'danger')
    else:
        flash('Todo content cannot be empty!', 'warning')
    
    # Preserve the current filter when redirecting
    filter_type = request.args.get('filter', 'all')
    return redirect(url_for('todo', filter=filter_type))

@web_blog.route("/todo/toggle/<int:todo_id>", methods=['POST'])
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        todo.completed = not todo.completed
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the todo.', 'danger')
    
    # Preserve the current filter when redirecting
    filter_type = request.args.get('filter', 'all')
    return redirect(url_for('todo', filter=filter_type))

@web_blog.route("/todo/edit/<int:todo_id>", methods=['POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    new_content = request.form.get('edited_todo')
    
    if new_content:
        try:
            todo.content = new_content
            db.session.commit()
            flash('Todo updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the todo.', 'danger')
    else:
        flash('Todo content cannot be empty!', 'warning')
    
    # Preserve the current filter when redirecting
    filter_type = request.args.get('filter', 'all')
    return redirect(url_for('todo', filter=filter_type))

@web_blog.route("/todo/delete/<int:todo_id>", methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    try:
        db.session.delete(todo)
        db.session.commit()
        flash('Todo deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the todo.', 'danger')
    
    # Preserve the current filter when redirecting
    filter_type = request.args.get('filter', 'all')
    return redirect(url_for('todo', filter=filter_type))