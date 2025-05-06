from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import send_file
from app.models import db, User, Attorney, BlogPost, Testimonial, Case, Appointment, Document, FAQ

# Create admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to restrict access to admin users only
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Admin dashboard
@admin.route('/')
@admin_required
def dashboard():
    attorneys_count = Attorney.query.count()
    blog_posts_count = BlogPost.query.count()
    testimonials_count = Testimonial.query.count()
    appointments_count = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='pending').count()
    
    return render_template('admin/dashboard.html', 
                          attorneys_count=attorneys_count,
                          blog_posts_count=blog_posts_count,
                          testimonials_count=testimonials_count,
                          appointments_count=appointments_count,
                          pending_appointments=pending_appointments)

# User management
@admin.route('/users')
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/users/new', methods=['GET', 'POST'])
@admin_required
def new_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin'))
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.new_user'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('admin.new_user'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            is_admin=is_admin
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/new_user.html')

@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.is_admin = True if request.form.get('is_admin') else False
        
        if request.form.get('password'):
            user.password = generate_password_hash(request.form.get('password'), method='sha256')
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin.route('/users/delete/<int:id>')
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

# Attorney management
@admin.route('/attorneys')
@admin_required
def attorneys():
    attorneys = Attorney.query.all()
    return render_template('admin/manage_attorneys.html', attorneys=attorneys)

@admin.route('/attorneys/new', methods=['GET', 'POST'])
@admin_required
def new_attorney():
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        bio = request.form.get('bio')
        education = request.form.get('education')
        experience = request.form.get('experience')
        specializations = request.form.get('specializations')
        email = request.form.get('email')
        phone = request.form.get('phone')
        linkedin = request.form.get('linkedin')
        twitter = request.form.get('twitter')
        
        # Handle photo upload
        photo = request.files.get('photo')
        photo_filename = None
        if photo and photo.filename:
            photo_filename = secure_filename(photo.filename)
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', photo_filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            photo.save(photo_path)
        
        # Handle video upload
        video = request.files.get('video')
        video_filename = None
        if video and video.filename:
            video_filename = secure_filename(video.filename)
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', video_filename)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            video.save(video_path)
        
        new_attorney = Attorney(
            name=name,
            title=title,
            bio=bio,
            education=education,
            experience=experience,
            specializations=specializations,
            email=email,
            phone=phone,
            linkedin=linkedin,
            twitter=twitter,
            photo=photo_filename,
            video=video_filename
        )
        
        db.session.add(new_attorney)
        db.session.commit()
        
        flash('Attorney added successfully!', 'success')
        return redirect(url_for('admin.attorneys'))
    
    return render_template('admin/new_attorney.html')

@admin.route('/attorneys/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_attorney(id):
    attorney = Attorney.query.get_or_404(id)
    
    if request.method == 'POST':
        attorney.name = request.form.get('name')
        attorney.title = request.form.get('title')
        attorney.bio = request.form.get('bio')
        attorney.education = request.form.get('education')
        attorney.experience = request.form.get('experience')
        attorney.specializations = request.form.get('specializations')
        attorney.email = request.form.get('email')
        attorney.phone = request.form.get('phone')
        attorney.linkedin = request.form.get('linkedin')
        attorney.twitter = request.form.get('twitter')
        
        # Handle photo upload
        photo = request.files.get('photo')
        if photo and photo.filename:
            # Delete old photo if exists
            if attorney.photo:
                old_photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', attorney.photo)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            
            photo_filename = secure_filename(photo.filename)
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', photo_filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            photo.save(photo_path)
            attorney.photo = photo_filename
        
        # Handle video upload
        video = request.files.get('video')
        if video and video.filename:
            # Delete old video if exists
            if attorney.video:
                old_video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', attorney.video)
                if os.path.exists(old_video_path):
                    os.remove(old_video_path)
            
            video_filename = secure_filename(video.filename)
            video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', video_filename)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            video.save(video_path)
            attorney.video = video_filename
        
        db.session.commit()
        flash('Attorney updated successfully!', 'success')
        return redirect(url_for('admin.attorneys'))
    
    return render_template('admin/edit_attorney.html', attorney=attorney)

@admin.route('/attorneys/delete/<int:id>')
@admin_required
def delete_attorney(id):
    attorney = Attorney.query.get_or_404(id)
    
    # Delete photo if exists
    if attorney.photo:
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', attorney.photo)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    # Delete video if exists
    if attorney.video:
        video_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attorneys', attorney.video)
        if os.path.exists(video_path):
            os.remove(video_path)
    
    db.session.delete(attorney)
    db.session.commit()
    flash('Attorney deleted successfully!', 'success')
    return redirect(url_for('admin.attorneys'))

# Practice Areas management
@admin.route('/practices')
@admin_required
def practices():
    practices = Practice.query.all()
    return render_template('admin/practices.html', practices=practices)

@admin.route('/practices/new', methods=['GET', 'POST'])
@admin_required
def new_practice():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon')
        
        new_practice = Practice(
            name=name,
            description=description,
            icon=icon
        )
        
        db.session.add(new_practice)
        db.session.commit()
        
        flash('Practice area added successfully!', 'success')
        return redirect(url_for('admin.practices'))
    
    return render_template('admin/new_practice.html')

@admin.route('/practices/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_practice(id):
    practice = Practice.query.get_or_404(id)
    
    if request.method == 'POST':
        practice.name = request.form.get('name')
        practice.description = request.form.get('description')
        practice.icon = request.form.get('icon')
        
        db.session.commit()
        flash('Practice area updated successfully!', 'success')
        return redirect(url_for('admin.practices'))
    
    return render_template('admin/edit_practice.html', practice=practice)

@admin.route('/practices/delete/<int:id>')
@admin_required
def delete_practice(id):
    practice = Practice.query.get_or_404(id)
    
    db.session.delete(practice)
    db.session.commit()
    flash('Practice area deleted successfully!', 'success')
    return redirect(url_for('admin.practices'))

# Blog management
@admin.route('/blog')
@admin_required
def blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/blog.html', posts=posts)

@admin.route('/blog/new', methods=['GET', 'POST'])
@admin_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        # Handle featured image upload
        image = request.files.get('image')
        image_filename = None
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog', image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        
        new_post = BlogPost(
            title=title,
            content=content,
            image=image_filename,
            author_id=current_user.id
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/new_post.html')

@admin.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_post(id):
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        
        # Handle featured image upload
        image = request.files.get('image')
        if image and image.filename:
            # Delete old image if exists
            if post.image:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog', post.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog', image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            post.image = image_filename
        
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('admin.blog'))
    
    return render_template('admin/edit_post.html', post=post)

@admin.route('/blog/delete/<int:id>')
@admin_required
def delete_post(id):
    post = BlogPost.query.get_or_404(id)
    
    # Delete image if exists
    if post.image:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog', post.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('admin.blog'))

# Testimonial management
@admin.route('/testimonials')
@admin_required
def testimonials():
    testimonials = Testimonial.query.all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@admin.route('/testimonials/new', methods=['GET', 'POST'])
@admin_required
def new_testimonial():
    if request.method == 'POST':
        client_name = request.form.get('client_name')
        content = request.form.get('content')
        rating = request.form.get('rating')
        
        new_testimonial = Testimonial(
            client_name=client_name,
            content=content,
            rating=rating
        )
        
        db.session.add(new_testimonial)
        db.session.commit()
        
        flash('Testimonial added successfully!', 'success')
        return redirect(url_for('admin.testimonials'))
    
    return render_template('admin/new_testimonial.html')

@admin.route('/testimonials/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    
    if request.method == 'POST':
        testimonial.client_name = request.form.get('client_name')
        testimonial.content = request.form.get('content')
        testimonial.rating = request.form.get('rating')
        
        db.session.commit()
        flash('Testimonial updated successfully!', 'success')
        return redirect(url_for('admin.testimonials'))
    
    return render_template('admin/edit_testimonial.html', testimonial=testimonial)

@admin.route('/testimonials/delete/<int:id>')
@admin_required
def delete_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    
    db.session.delete(testimonial)
    db.session.commit()
    flash('Testimonial deleted successfully!', 'success')
    return redirect(url_for('admin.testimonials'))

# Case management
@admin.route('/cases')
@admin_required
def cases():
    cases = Case.query.all()
    return render_template('admin/cases.html', cases=cases)

@admin.route('/cases/new', methods=['GET', 'POST'])
@admin_required
def new_case():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        outcome = request.form.get('outcome')
        
        new_case = Case(
            title=title,
            description=description,
            outcome=outcome
        )
        
        db.session.add(new_case)
        db.session.commit()
        
        flash('Case added successfully!', 'success')
        return redirect(url_for('admin.cases'))
    
    return render_template('admin/new_case.html')

@admin.route('/cases/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_case(id):
    case = Case.query.get_or_404(id)
    
    if request.method == 'POST':
        case.title = request.form.get('title')
        case.description = request.form.get('description')
        case.outcome = request.form.get('outcome')
        
        db.session.commit()
        flash('Case updated successfully!', 'success')
        return redirect(url_for('admin.cases'))
    
    return render_template('admin/edit_case.html', case=case)

@admin.route('/cases/delete/<int:id>')
@admin_required
def delete_case(id):
    case = Case.query.get_or_404(id)
    
    db.session.delete(case)
    db.session.commit()
    flash('Case deleted successfully!', 'success')
    return redirect(url_for('admin.cases'))

# Appointment management
@admin.route('/appointments')
@admin_required
def appointments():
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)

@admin.route('/appointments/update/<int:id>', methods=['POST'])
@admin_required
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    appointment.status = status
    appointment.notes = notes
    
    db.session.commit()
    flash('Appointment updated successfully!', 'success')
    return redirect(url_for('admin.appointments'))

@admin.route('/appointments/confirm/<int:id>', methods=['POST'])
@admin_required
def confirm_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        db.session.commit()
        flash('Appointment confirmed successfully!', 'success')
    else:
        flash('Appointment is already confirmed or cannot be confirmed.', 'warning')
    return redirect(url_for('admin.appointments'))

@admin.route('/appointments/delete/<int:id>', methods=['POST'])
@admin_required
def delete_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('admin.appointments'))

# Document management
@admin.route('/documents')
@admin_required
def documents():
    documents = Document.query.order_by(Document.uploaded_at.desc()).all()
    return render_template('admin/documents.html', documents=documents)

@admin.route('/documents/upload', methods=['GET', 'POST'])
@admin_required
def upload_document():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        client_id = request.form.get('client_id')
        
        # Handle document upload
        file = request.files.get('file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            new_document = Document(
                title=title,
                description=description,
                filename=filename,
                client_id=client_id,
                uploaded_by=current_user.id
            )
            
            db.session.add(new_document)
            db.session.commit()
            
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('admin.documents'))
        else:
            flash('No file selected!', 'danger')
    
    clients = User.query.filter_by(is_admin=False).all()
    return render_template('admin/upload_document.html', clients=clients)

@admin.route('/documents/delete/<int:id>')
@admin_required
def delete_document(id):
    document = Document.query.get_or_404(id)
    
    # Delete file if exists
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(document)
    db.session.commit()
    flash('Document deleted successfully!', 'success')
    return redirect(url_for('admin.documents'))

# FAQ management
@admin.route('/faqs')
@admin_required
def faqs():
    faqs = FAQ.query.all()
    return render_template('admin/faqs.html', faqs=faqs)

@admin.route('/faqs/new', methods=['GET', 'POST'])
@admin_required
def new_faq():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category')
        
        new_faq = FAQ(
            question=question,
            answer=answer,
            category=category
        )
        
        db.session.add(new_faq)
        db.session.commit()
        
        flash('FAQ added successfully!', 'success')
        return redirect(url_for('admin.faqs'))
    
    return render_template('admin/new_faq.html')

@admin.route('/faqs/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_faq(id):
    faq = FAQ.query.get_or_404(id)
    
    if request.method == 'POST':
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        faq.category = request.form.get('category')
        
        db.session.commit()
        flash('FAQ updated successfully!', 'success')
        return redirect(url_for('admin.faqs'))
    
    return render_template('admin/edit_faq.html', faq=faq)

@admin.route('/faqs/delete/<int:id>')
@admin_required
def delete_faq(id):
    faq = FAQ.query.get_or_404(id)
    
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!', 'success')
    return redirect(url_for('admin.faqs'))

# CLI commands for admin creation
def create_admin_cli(app):
    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user from the command line."""
        from models import User
        
        print("Creating admin user...")
        email = input("Email: ")
        name = input("Name: ")
        password = input("Password: ")
        
        user = User.query.filter_by(email=email).first()
        if user:
            print("User with this email already exists!")
            return
        
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='sha256'),
            is_admin=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"Admin user {name} created successfully!")

@admin.route('/documents/download/<int:id>')
@admin_required
def download_document(id):
    document = Document.query.get_or_404(id)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', document.filename)
    
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=document.filename
        )
    else:
        flash('Document file not found!', 'error')
        return redirect(url_for('admin.documents'))

@admin.route('/testimonials/approve/<int:id>')
@admin_required
def approve_testimonial(id):
    testimonial = Testimonial.query.get_or_404(id)
    testimonial.approved = True
    db.session.commit()
    flash('Testimonial approved successfully!', 'success')
    return redirect(url_for('admin.testimonials'))