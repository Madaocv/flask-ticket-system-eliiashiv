from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
import click
from .models import db, User

@click.command(name='create_admin')
@with_appcontext
def create_admin():
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'), role='Admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully.')
    else:
        print('Admin user already exists.')
