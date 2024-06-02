from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from .models import db, User, Group, Ticket
from .forms import LoginForm, RegistrationForm, TicketForm, GroupForm
from werkzeug.security import generate_password_hash

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Якщо користувач залогінений і не є адміністратором, забороняємо доступ
    if current_user.is_authenticated and current_user.role not in ['Admin']:
        abort(403)  # Доступ заборонено

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        
        # Якщо користувач не залогінений, здійснюємо автологін
        if not current_user.is_authenticated:
            login_user(new_user)  # Логін після реєстрації
            flash('User registered and logged in successfully!')
            return redirect(url_for('main.index'))  # Редірект на головну сторінку
        else:
            flash('User registered successfully!')
            return redirect(url_for('main.index'))  # Редірект на головну сторінку

    return render_template('register.html', form=form)



@bp.route('/tickets', methods=['GET', 'POST'])
@login_required
def tickets():
    form = TicketForm()
    if form.validate_on_submit():
        assignee_data = form.assignee.data.split('_')
        user_id = None
        group_id = None
        if assignee_data[0] == 'user':
            user_id = int(assignee_data[1])
        elif assignee_data[0] == 'group':
            group_id = int(assignee_data[1])
        
        ticket = Ticket(
            status=form.status.data,
            note=form.note.data,
            user_id=user_id,
            group_id=group_id
        )
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully!')
    tickets = Ticket.query.all()
    return render_template('tickets.html', form=form, tickets=tickets)

@bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != 'Admin':
        flash('Access denied!')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully!')

    users = User.query.all()
    return render_template('manage_users.html', form=form, users=users)


@bp.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    if current_user.role != 'Admin':
        flash('Access denied!')
        return redirect(url_for('main.index'))
    
    form = GroupForm()
    if form.validate_on_submit():
        new_group = Group(name=form.name.data)
        db.session.add(new_group)
        db.session.commit()
        
        # Додаємо користувачів до групи
        selected_users = User.query.filter(User.id.in_(form.users.data)).all()
        for user in selected_users:
            user.group_id = new_group.id
        db.session.commit()
        
        flash('Group created successfully!')
        return redirect(url_for('main.index'))
    return render_template('create_group.html', form=form)



@bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def edit_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # RBAC: Admin can edit any ticket, Manager can edit any ticket assigned to a group,
    # Analyst can edit any ticket assigned to a user
    if current_user.role == 'Admin':
        pass
    elif current_user.role == 'Manager' and ticket.group_id is not None:
        pass
    elif current_user.role == 'Analyst' and ticket.user_id is not None:
        pass
    else:
        flash('Access denied!')
        return redirect(url_for('main.index'))

    form = TicketForm(obj=ticket)
    if form.validate_on_submit():
        assignee_data = form.assignee.data.split('_')
        user_id = None
        group_id = None
        if assignee_data[0] == 'user':
            user_id = int(assignee_data[1])
        elif assignee_data[0] == 'group':
            group_id = int(assignee_data[1])

        ticket.status = form.status.data
        ticket.note = form.note.data
        ticket.user_id = user_id
        ticket.group_id = group_id
        db.session.commit()
        flash('Ticket updated successfully!')
        return redirect(url_for('main.tickets'))
    return render_template('edit_ticket.html', form=form, ticket=ticket)