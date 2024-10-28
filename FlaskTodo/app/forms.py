from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    module_code = StringField('Module Code', validators=[
        DataRequired(),
        Regexp(r'^[A-Z]{4}[0-9]{4}$', message="Module code must be in the format: XJCO2011")
    ])
    description = TextAreaField('Description')
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[DataRequired()])
    importance = SelectField('Importance', choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], validators=[DataRequired()])
    submit = SubmitField('Add Task')
    id = StringField('ID')  # Hidden field to store the ID of the task

    # Validation to ensure title != module_code
    def validate_title(self, field):
        if field.data == self.module_code.data:
            raise ValidationError("Title cannot be the same as Module Code.")
