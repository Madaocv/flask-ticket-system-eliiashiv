from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired
from .models import User, Group


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TicketForm(FlaskForm):
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('In review', 'In review'), ('Closed', 'Closed')])
    assignee = SelectField('Assign to User/Group', choices=[], coerce=str, validators=[DataRequired()])
    note = TextAreaField('Note', validators=[DataRequired()])
    submit = SubmitField('Create Ticket')

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.assignee.choices = [("user_" + str(user.id), "User: " + user.username) for user in User.query.all()] + \
                                [("group_" + str(group.id), "Group: " + group.name) for group in Group.query.all()]


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('Admin', 'Admin'), ('Manager', 'Manager'), ('Analyst', 'Analyst')], validators=[DataRequired()])
    submit = SubmitField('Register')


class GroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired()])
    users = SelectMultipleField('Add Users', choices=[], coerce=int)
    submit = SubmitField('Create Group')

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.users.choices = [(user.id, user.username) for user in User.query.all()]