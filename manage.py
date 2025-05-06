import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app.models import db, User

def register_commands(app):
    @app.cli.command('create-admin')
    @click.option('--email', prompt=True, help='Admin email address')
    @click.option('--username', prompt=True, help='Admin username')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin password')
    @with_appcontext
    def create_admin(email, username, password):
        """Create an admin user from the command line."""
        user = User.query.filter_by(email=email).first()
        if user:
            click.echo("User with this email already exists!")
            return
        
        user = User.query.filter_by(username=username).first()
        if user:
            click.echo("User with this username already exists!")
            return
        
        new_user = User(
            email=email,
            username=username,
            role='admin',
            is_admin=True
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        click.echo(f"Admin user {username} created successfully!")
    
    @app.cli.command('create-practice-areas')
    @with_appcontext
    def create_practice_areas():
        """Create default practice areas."""
        from app.models import PracticeArea
        
        practice_areas = [
            {
                'name': 'Family Law',
                'description': 'We handle divorce, child custody, adoption, and other family-related legal matters.',
                'icon': 'fa-users'
            },
            {
                'name': 'Criminal Defense',
                'description': 'Our experienced attorneys provide defense for all criminal charges.',
                'icon': 'fa-gavel'
            },
            {
                'name': 'Personal Injury',
                'description': 'We help victims of accidents get the compensation they deserve.',
                'icon': 'fa-ambulance'
            },
            {
                'name': 'Real Estate',
                'description': 'Our firm handles property transactions, disputes, and related legal matters.',
                'icon': 'fa-home'
            },
            {
                'name': 'Corporate Law',
                'description': 'We provide legal services for businesses of all sizes.',
                'icon': 'fa-building'
            },
            {
                'name': 'Intellectual Property',
                'description': 'Protect your ideas, inventions, and creative works with our IP services.',
                'icon': 'fa-lightbulb'
            }
        ]
        
        for area in practice_areas:
            existing = PracticeArea.query.filter_by(name=area['name']).first()
            if not existing:
                new_area = PracticeArea(
                    name=area['name'],
                    description=area['description'],
                    icon=area['icon']
                )
                db.session.add(new_area)
        
        db.session.commit()
        click.echo("Default practice areas created successfully!")
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db():
        """Initialize the database."""
        db.create_all()
        click.echo("Database tables created!")