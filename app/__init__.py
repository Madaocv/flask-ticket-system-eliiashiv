from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .models import User
    with app.app_context():
        db.create_all()

    from . import routes
    app.register_blueprint(routes.bp)

    from .commands import create_admin
    app.cli.add_command(create_admin)

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_template('401.html'), 401

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Імпортуємо модель User тут
    return User.query.get(int(user_id))
