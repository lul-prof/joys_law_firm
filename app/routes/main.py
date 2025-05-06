from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import PracticeArea, Attorney, BlogPost, Testimonial, Appointment,User,Client, Message, db
from app import db
from datetime import datetime
import secrets 

main = Blueprint('main', __name__)

@main.route('/')
def home():
    practice_areas = PracticeArea.query.limit(6).all()
    attorneys = Attorney.query.limit(4).all()
    testimonials = Testimonial.query.filter_by(approved=True).limit(3).all()
    recent_posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    return render_template('public/home.html', 
                          practice_areas=practice_areas, 
                          attorneys=attorneys,
                          testimonials=testimonials,
                          recent_posts=recent_posts)

@main.route('/about')
def about():
    attorneys = Attorney.query.all()
    return render_template('public/about.html', attorneys=attorneys)

@main.route('/services')
def services():
    practice_areas = PracticeArea.query.all()
    return render_template('public/services.html', practice_areas=practice_areas)

@main.route('/attorneys')
def attorneys():
    attorneys_list = Attorney.query.all()
    return render_template('public/attorneys.html', attorneys=attorneys_list)

@main.route('/attorney/<int:attorney_id>')
def attorney_profile(attorney_id):
    attorney = Attorney.query.get_or_404(attorney_id)
    return render_template('public/attorney_profile.html', attorney=attorney)

@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=5)
    return render_template('public/blog.html', posts=posts)

@main.route('/blog/<string:slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('public/blog_post.html', post=post)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        flash('Your message has been sent. We will contact you shortly!', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('public/contact.html')

'''
@main.route('/booking', methods=['GET', 'POST'])
def booking():
    attorneys = Attorney.query.all()
    
    if request.method == 'POST':
        # Process booking form
        client_name = request.form.get('name')
        client_email = request.form.get('email')
        client_phone = request.form.get('phone')
        attorney_id = request.form.get('attorney_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        purpose = request.form.get('purpose')
        
        # Convert strings to date and time objects
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Here you would create an appointment in the database
        # For now, just show a success message
        flash('Your appointment request has been submitted. We will confirm shortly!', 'success')
        return redirect(url_for('main.booking'))
        
    return render_template('public/booking.html', attorneys=attorneys)

    '''


@main.route('/booking', methods=['GET', 'POST'])
def booking():
    attorneys = Attorney.query.all()
    
    if request.method == 'POST':
        # Process booking form
        client_name = request.form.get('name')
        client_email = request.form.get('email')
        client_phone = request.form.get('phone')
        attorney_id = request.form.get('attorney_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        purpose = request.form.get('purpose')
        
        # Convert strings to date and time objects
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Check if user exists with this email
        user = User.query.filter_by(email=client_email).first()
        if not user:
            # Create new user
            user = User(
                email=client_email,
                username=client_email,  # Using email as username
                role='client'
            )
            user.set_password(secrets.token_urlsafe(8))  # Generate random password
            db.session.add(user)
            db.session.flush()  # To get the user.id
            
            # Create new client
            client = Client(
                user_id=user.id,
                full_name=client_name,
                phone=client_phone
            )
            db.session.add(client)
            db.session.flush()  # To get the client.id
        else:
            client = Client.query.filter_by(user_id=user.id).first()
        
        # Create new appointment
        new_appointment = Appointment(
            client_id=client.id,
            attorney_id=attorney_id,
            date=date_obj,
            time=time_obj,
            purpose=purpose,
            status='pending'
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Your appointment request has been submitted. We will confirm shortly!', 'success')
        return redirect(url_for('main.booking'))
        
    return render_template('public/booking.html', attorneys=attorneys)