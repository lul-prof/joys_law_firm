from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.models import db, User, Client, Appointment, Document, Message, Attorney, Testimonial
from app.routes.admin import admin_required

client = Blueprint('client', __name__, url_prefix='/client')

# Decorator to restrict access to client users only
def client_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'client':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@client.route('/portal')
@client_required
def portal():
    # Get client information
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.query.filter_by(
        client_id=client_info.id
    ).filter(
        Appointment.date >= datetime.now().date()
    ).order_by(Appointment.date, Appointment.time).limit(5).all()
    
    # Get recent documents
    recent_documents = Document.query.filter_by(
        client_id=client_info.id
    ).order_by(Document.uploaded_at.desc()).limit(5).all()
    
    # Get unread messages
    unread_messages = Message.query.filter_by(
        recipient_id=current_user.id,
        read=False
    ).count()
    
    return render_template('client/portal.html', 
                          client=client_info,
                          upcoming_appointments=upcoming_appointments,
                          recent_documents=recent_documents,
                          unread_messages=unread_messages)

@client.route('/profile', methods=['GET', 'POST'])
@client_required
def profile():
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update user information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        
        # Update client information
        client_info.full_name = request.form.get('full_name')
        client_info.phone = request.form.get('phone')
        client_info.address = request.form.get('address')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('client.profile'))
    
    return render_template('client/profile.html', client=client_info)

@client.route('/appointments')
@client_required
def appointments():
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    appointments = Appointment.query.filter_by(client_id=client_info.id).order_by(Appointment.date.desc()).all()
    return render_template('client/appointments.html', appointments=appointments)

@client.route('/appointments/new', methods=['GET', 'POST'])
@client_required
def new_appointment():
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    attorneys = Attorney.query.all()
    
    if request.method == 'POST':
        attorney_id = request.form.get('attorney_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        purpose = request.form.get('purpose')
        
        # Convert strings to date and time objects
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        new_appointment = Appointment(
            client_id=client_info.id,
            attorney_id=attorney_id,
            date=date_obj,
            time=time_obj,
            purpose=purpose,
            status='pending'
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash('Appointment request submitted successfully!', 'success')
        return redirect(url_for('client.appointments'))
    
    return render_template('client/new_appointment.html', attorneys=attorneys)

@client.route('/documents')
@client_required
def documents():
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    documents = Document.query.filter_by(client_id=client_info.id).order_by(Document.uploaded_at.desc()).all()
    return render_template('client/documents.html', documents=documents)

@client.route('/documents/upload', methods=['GET', 'POST'])
@client_required
def upload_document():
    client_info = Client.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        # Handle document upload
        file = request.files.get('file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'client_documents', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            
            new_document = Document(
                title=title,
                description=description,
                filename=filename,
                client_id=client_info.id,
                uploaded_by=current_user.id
            )
            
            db.session.add(new_document)
            db.session.commit()
            
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('client.documents'))
        else:
            flash('No file selected!', 'danger')
    
    return render_template('client/upload_document.html')

@client.route('/messages')
@client_required
def messages():
    # Get all messages where current user is either sender or recipient
    messages_sent = Message.query.filter_by(sender_id=current_user.id).all()
    messages_received = Message.query.filter_by(recipient_id=current_user.id).all()
    
    # Mark all received messages as read
    for message in messages_received:
        if not message.read:
            message.read = True
    
    db.session.commit()
    
    # Get all attorneys for messaging
    attorneys = Attorney.query.all()
    
    return render_template('client/messages.html', 
                          messages_sent=messages_sent,
                          messages_received=messages_received,
                          attorneys=attorneys)

@client.route('/messages/send', methods=['POST'])
@client_required
def send_message():
    recipient_id = request.form.get('recipient_id')
    content = request.form.get('content')
    
    new_message = Message(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        content=content
    )
    
    db.session.add(new_message)
    db.session.commit()
    
    flash('Message sent successfully!', 'success')
    return redirect(url_for('client.messages'))

@client.route('/testimonial', methods=['GET', 'POST'])
@login_required
def submit_testimonial():
    if request.method == 'POST':
        content = request.form.get('content')
        rating = request.form.get('rating')
        photo = request.files.get('photo')
        
        # Handle photo upload if provided
        photo_filename = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_filename = f"{current_user.id}_{int(time.time())}_{filename}"
            photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], 'testimonials', photo_filename))
        
        # Create new testimonial
        testimonial = Testimonial(
            client_name=current_user.username,
            content=content,
            rating=int(rating),
            photo=photo_filename,
            approved=False  # Testimonials need admin approval before being displayed
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        flash('Thank you for your testimonial! It will be reviewed and published soon.', 'success')
        return redirect(url_for('client.portal'))
        
    return render_template('client/testimonial.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
