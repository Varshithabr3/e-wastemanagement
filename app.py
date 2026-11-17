import os
import secrets
from datetime import datetime, date, timedelta
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request, redirect, 
    url_for, flash, session, jsonify, abort
)
from sqlalchemy import create_engine, func, desc
from sqlalchemy.orm import sessionmaker, scoped_session

from config import Config, SQLALCHEMY_DATABASE_URI, DB_ENGINE_LABEL
from models import (
    Base, User, Admin, EwasteItem, CollectionRequest,
    RecyclingCentre, DisposalGuideline, AwarenessContent,
    collection_request_items
)

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Engine & Session
engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Context Processor for Global Variables
@app.context_processor
def inject_global_context():
    user = None
    admin = None
    if 'user_id' in session:
        user = db_session.get(User, session['user_id'])
    if 'admin_id' in session:
        admin = db_session.get(Admin, session['admin_id'])
    return dict(
        current_user=user,
        current_admin=admin,
        current_year=datetime.now().year,
        categories=[
            'Mobile Phones', 'Laptops', 'Computers', 
            'Batteries', 'Chargers', 'Televisions', 'Other Electronics'
        ]
    )

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Administrator authentication required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_request_code():
    today_str = datetime.now().strftime('%Y%m')
    random_hex = secrets.token_hex(2).upper()
    return f"EWC-{today_str}-{random_hex}"

# ----------------------------------------------------------------------------
# PUBLIC ROUTES
# ----------------------------------------------------------------------------

@app.route('/')
def index():
    # Fetch public statistics
    total_users = db_session.query(User).count()
    total_items = db_session.query(EwasteItem).count()
    total_requests = db_session.query(CollectionRequest).count()
    completed_requests = db_session.query(CollectionRequest).filter_by(status='Completed').count()
    verified_centres = db_session.query(RecyclingCentre).filter_by(is_official_verified=True).count()
    
    # Recent verified centres preview
    recent_centres = db_session.query(RecyclingCentre).order_by(RecyclingCentre.id.desc()).limit(3).all()
    
    # Guidelines preview
    guidelines = db_session.query(DisposalGuideline).limit(4).all()

    return render_template(
        'index.html',
        total_users=total_users,
        total_items=total_items,
        total_requests=total_requests,
        completed_requests=completed_requests,
        verified_centres=verified_centres,
        recent_centres=recent_centres,
        guidelines=guidelines
    )

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guidelines')
def guidelines():
    all_guidelines = db_session.query(DisposalGuideline).all()
    selected_category = request.args.get('category')
    return render_template('guidance/index.html', guidelines=all_guidelines, selected_category=selected_category)

@app.route('/centres')
def centres():
    search_query = request.args.get('search', '').strip()
    city_query = request.args.get('city', '').strip()
    district_query = request.args.get('district', '').strip()
    pincode_query = request.args.get('pincode', '').strip()
    facility_type_query = request.args.get('facility_type', '').strip()
    category_query = request.args.get('category', '').strip()
    verification_filter = request.args.get('verified', '').strip()

    query = db_session.query(RecyclingCentre)

    if search_query:
        query = query.filter(
            (RecyclingCentre.centre_name.ilike(f"%{search_query}%")) |
            (RecyclingCentre.complete_address.ilike(f"%{search_query}%")) |
            (RecyclingCentre.city.ilike(f"%{search_query}%")) |
            (RecyclingCentre.district.ilike(f"%{search_query}%")) |
            (RecyclingCentre.pincode.ilike(f"%{search_query}%")) |
            (RecyclingCentre.facility_type.ilike(f"%{search_query}%"))
        )

    if city_query:
        query = query.filter(RecyclingCentre.city.ilike(f"%{city_query}%"))

    if district_query:
        query = query.filter(RecyclingCentre.district.ilike(f"%{district_query}%"))

    if pincode_query:
        query = query.filter(RecyclingCentre.pincode.ilike(f"%{pincode_query}%"))

    if facility_type_query:
        query = query.filter(RecyclingCentre.facility_type.ilike(f"%{facility_type_query}%"))

    if category_query:
        query = query.filter(RecyclingCentre.accepted_categories.ilike(f"%{category_query}%"))

    if verification_filter == '1':
        query = query.filter_by(is_official_verified=True)
    elif verification_filter == '0':
        query = query.filter_by(is_official_verified=False)

    all_centres = query.order_by(desc(RecyclingCentre.is_official_verified), RecyclingCentre.centre_name).all()
    
    # Get unique filter options for dropdowns
    cities = [r[0] for r in db_session.query(RecyclingCentre.city).distinct().order_by(RecyclingCentre.city).all() if r[0]]
    districts = [r[0] for r in db_session.query(RecyclingCentre.district).distinct().order_by(RecyclingCentre.district).all() if r[0]]
    facility_types = ['Authorized Recycler', 'Authorized Dismantler', 'Collection Centre', 'Authorized Refurbisher']

    return render_template(
        'centres/index.html',
        centres=all_centres,
        cities=cities,
        districts=districts,
        facility_types=facility_types,
        search_query=search_query,
        search_city=city_query,
        search_district=district_query,
        search_pincode=pincode_query,
        search_facility_type=facility_type_query,
        search_category=category_query,
        search_verified=verification_filter
    )

@app.route('/awareness')
def awareness():
    articles = db_session.query(AwarenessContent).all()
    return render_template('awareness/index.html', articles=articles)

@app.route('/quiz')
def quiz():
    return render_template('awareness/quiz.html')

# ----------------------------------------------------------------------------
# USER AUTHENTICATION & PROFILE
# ----------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', 'Bengaluru').strip()
        pincode = request.form.get('pincode', '').strip()

        if not full_name or not email or not phone or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/register.html')

        existing_user = db_session.query(User).filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please login.', 'warning')
            return redirect(url_for('login'))

        new_user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            address=address,
            city=city,
            pincode=pincode
        )
        db_session.add(new_user)
        db_session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = db_session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_email'] = user.email
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))

    reset_url = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your registered email address.', 'danger')
            return render_template('auth/forgot_password.html')

        user = db_session.query(User).filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.now() + timedelta(hours=2)
            db_session.commit()
            reset_url = url_for('reset_password', token=token, _external=True)
            flash('Password reset verification link generated successfully.', 'success')
        else:
            flash('No account registered with that email address. Please verify your email or register.', 'warning')

    return render_template('auth/forgot_password.html', reset_url=reset_url)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))

    user = db_session.query(User).filter_by(reset_token=token).first()
    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.now():
        flash('The password reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/reset_password.html', token=token, user=user)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token, user=user)

        user.password_hash = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db_session.commit()

        flash('Your password has been reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/reset_password.html', token=token, user=user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = db_session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        pincode = request.form.get('pincode', '').strip()
        new_password = request.form.get('new_password', '')

        if not full_name or not phone:
            flash('Name and Phone cannot be empty.', 'danger')
            return render_template('auth/profile.html', user=user)

        user.full_name = full_name
        user.phone = phone
        user.address = address
        user.city = city
        user.pincode = pincode

        if new_password:
            if len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'warning')
                return render_template('auth/profile.html', user=user)
            user.password_hash = generate_password_hash(new_password)
            flash('Password updated successfully.', 'info')

        db_session.commit()
        session['user_name'] = user.full_name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('auth/profile.html', user=user)

# ----------------------------------------------------------------------------
# USER DASHBOARD & E-WASTE MANAGEMENT
# ----------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def user_dashboard():
    user_id = session['user_id']
    items = db_session.query(EwasteItem).filter_by(user_id=user_id).order_by(EwasteItem.id.desc()).all()
    requests = db_session.query(CollectionRequest).filter_by(user_id=user_id).order_by(CollectionRequest.id.desc()).all()

    total_items = len(items)
    pending_requests = sum(1 for r in requests if r.status == 'Pending')
    approved_requests = sum(1 for r in requests if r.status in ['Approved', 'In Progress'])
    completed_requests = sum(1 for r in requests if r.status == 'Completed')

    return render_template(
        'user/dashboard.html',
        items=items,
        requests=requests,
        total_items=total_items,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        completed_requests=completed_requests
    )

@app.route('/ewaste/register', methods=['GET', 'POST'])
@login_required
def register_ewaste():
    user = db_session.get(User, session['user_id'])
    
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        item_name = request.form.get('item_name', '').strip()
        quantity = request.form.get('quantity', 1)
        item_condition = request.form.get('item_condition', 'Not Working').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip() or user.city

        if not category or not item_name:
            flash('Category and Item Name are required.', 'danger')
            return render_template('user/register_ewaste.html', user=user)

        try:
            quantity = int(quantity)
            if quantity < 1:
                quantity = 1
        except ValueError:
            quantity = 1

        # Handle optional image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                safe_name = secure_filename(file.filename)
                unique_name = f"{secrets.token_hex(4)}_{safe_name}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(file_path)
                image_filename = unique_name

        new_item = EwasteItem(
            user_id=user.id,
            category=category,
            item_name=item_name,
            quantity=quantity,
            item_condition=item_condition,
            description=description,
            location=location,
            image_filename=image_filename,
            status='Available'
        )
        db_session.add(new_item)
        db_session.commit()

        flash(f'E-waste item "{item_name}" registered successfully!', 'success')
        return redirect(url_for('my_ewaste_items'))

    return render_template('user/register_ewaste.html', user=user)

@app.route('/ewaste/my-items')
@login_required
def my_ewaste_items():
    user_id = session['user_id']
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = db_session.query(EwasteItem).filter_by(user_id=user_id)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    items = query.order_by(EwasteItem.id.desc()).all()
    return render_template('user/my_items.html', items=items, selected_category=category_filter, selected_status=status_filter)

@app.route('/ewaste/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_ewaste_item(item_id):
    item = db_session.get(EwasteItem, item_id)
    if not item or item.user_id != session['user_id']:
        flash('Item not found or unauthorized.', 'danger')
        return redirect(url_for('my_ewaste_items'))

    if item.status == 'In Request':
        flash('Cannot delete item that is currently linked to an active collection request.', 'warning')
        return redirect(url_for('my_ewaste_items'))

    db_session.delete(item)
    db_session.commit()
    flash('E-waste record removed successfully.', 'info')
    return redirect(url_for('my_ewaste_items'))

# ----------------------------------------------------------------------------
# COLLECTION REQUEST MODULE
# ----------------------------------------------------------------------------

@app.route('/request/new', methods=['GET', 'POST'])
@login_required
def submit_request():
    user = db_session.get(User, session['user_id'])
    
    # Available items that are not already assigned to an ongoing request
    available_items = db_session.query(EwasteItem).filter_by(
        user_id=user.id, 
        status='Available'
    ).all()

    if request.method == 'POST':
        selected_item_ids = request.form.getlist('item_ids')
        pickup_address = request.form.get('pickup_address', '').strip() or user.address
        city = request.form.get('city', '').strip() or user.city
        pincode = request.form.get('pincode', '').strip() or user.pincode
        preferred_date_str = request.form.get('preferred_date', '')
        preference_type = request.form.get('preference_type', 'Doorstep Pickup')
        notes = request.form.get('notes', '').strip()

        if not selected_item_ids:
            flash('Please select at least one registered e-waste item for collection.', 'danger')
            return render_template('user/submit_request.html', user=user, available_items=available_items)

        if not pickup_address or not city or not pincode or not preferred_date_str:
            flash('Please complete all collection address and preferred date fields.', 'danger')
            return render_template('user/submit_request.html', user=user, available_items=available_items)

        try:
            preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
            if preferred_date < date.today():
                flash('Preferred collection date must be today or in the future.', 'warning')
                return render_template('user/submit_request.html', user=user, available_items=available_items)
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('user/submit_request.html', user=user, available_items=available_items)

        # Generate unique Request Code
        request_code = generate_request_code()

        new_request = CollectionRequest(
            request_code=request_code,
            user_id=user.id,
            pickup_address=pickup_address,
            city=city,
            pincode=pincode,
            preferred_date=preferred_date,
            preference_type=preference_type,
            status='Pending',
            admin_notes=notes if notes else 'Request received. Awaiting admin review.'
        )

        # Attach items and update item status
        for item_id_str in selected_item_ids:
            try:
                iid = int(item_id_str)
                item = db_session.get(EwasteItem, iid)
                if item and item.user_id == user.id:
                    new_request.items.append(item)
                    item.status = 'In Request'
            except ValueError:
                pass

        db_session.add(new_request)
        db_session.commit()

        flash(f'Collection request submitted successfully! Your Request ID is {request_code}', 'success')
        return redirect(url_for('request_confirmation', request_code=request_code))

    return render_template('user/submit_request.html', user=user, available_items=available_items)

@app.route('/request/confirmation/<request_code>')
@login_required
def request_confirmation(request_code):
    req = db_session.query(CollectionRequest).filter_by(
        request_code=request_code, 
        user_id=session['user_id']
    ).first()
    if not req:
        abort(404)
    return render_template('user/confirmation.html', request=req)

@app.route('/request/receipt/<request_code>')
def request_receipt(request_code):
    req = db_session.query(CollectionRequest).filter_by(request_code=request_code).first()
    if not req:
        abort(404)
    # Check permissions: if logged in as user, must own it; or if admin; or public if viewing receipt
    if 'user_id' in session and req.user_id != session['user_id'] and 'admin_id' not in session:
        abort(403)
    return render_template('user/receipt.html', req=req)

@app.route('/request/track', methods=['GET', 'POST'])
def track_request():
    searched_code = request.args.get('code', '').strip().upper()
    req = None
    if searched_code:
        req = db_session.query(CollectionRequest).filter_by(request_code=searched_code).first()
        if not req:
            flash(f'No collection request found with Request ID "{searched_code}". Please check and try again.', 'warning')
    
    return render_template('user/track_request.html', req=req, searched_code=searched_code)

@app.route('/request/track/<request_code>')
def track_request_direct(request_code):
    req = db_session.query(CollectionRequest).filter_by(request_code=request_code.upper()).first()
    if not req:
        abort(404)
    return render_template('user/track_request.html', req=req, searched_code=req.request_code)

# ----------------------------------------------------------------------------
# ADMIN PORTAL & MANAGEMENT
# ----------------------------------------------------------------------------

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        admin = db_session.query(Admin).filter_by(email=email).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = admin.id
            session['admin_name'] = admin.full_name
            session['admin_email'] = admin.email
            session['admin_role'] = admin.role
            flash(f'Welcome back, Administrator {admin.full_name}!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid administrator credentials.', 'danger')

    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('admin_role', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_users = db_session.query(User).count()
    total_items = db_session.query(EwasteItem).count()
    total_requests = db_session.query(CollectionRequest).count()
    pending_requests = db_session.query(CollectionRequest).filter_by(status='Pending').count()
    approved_requests = db_session.query(CollectionRequest).filter_by(status='Approved').count()
    in_progress_requests = db_session.query(CollectionRequest).filter_by(status='In Progress').count()
    completed_requests = db_session.query(CollectionRequest).filter_by(status='Completed').count()
    rejected_requests = db_session.query(CollectionRequest).filter_by(status='Rejected').count()
    total_centres = db_session.query(RecyclingCentre).count()

    recent_requests = db_session.query(CollectionRequest).order_by(CollectionRequest.id.desc()).limit(8).all()

    # Category counts for Chart.js
    category_counts = db_session.query(
        EwasteItem.category, func.count(EwasteItem.id)
    ).group_by(EwasteItem.category).all()
    categories_data = {cat: count for cat, count in category_counts}

    # Condition counts for Chart.js
    condition_counts = db_session.query(
        EwasteItem.item_condition, func.count(EwasteItem.id)
    ).group_by(EwasteItem.item_condition).all()
    conditions_data = {cond: count for cond, count in condition_counts}

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_items=total_items,
        total_requests=total_requests,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        in_progress_requests=in_progress_requests,
        completed_requests=completed_requests,
        rejected_requests=rejected_requests,
        total_centres=total_centres,
        recent_requests=recent_requests,
        categories_data=categories_data,
        conditions_data=conditions_data
    )

@app.route('/admin/requests')
@admin_required
def admin_requests():
    status_filter = request.args.get('status', '').strip()
    query = db_session.query(CollectionRequest)
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests_list = query.order_by(CollectionRequest.id.desc()).all()
    return render_template('admin/requests.html', requests=requests_list, selected_status=status_filter)

@app.route('/admin/requests/update/<int:req_id>', methods=['POST'])
@admin_required
def admin_update_request(req_id):
    req = db_session.get(CollectionRequest, req_id)
    if not req:
        flash('Request not found.', 'danger')
        return redirect(url_for('admin_requests'))

    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes', '').strip()

    if new_status in ['Pending', 'Approved', 'In Progress', 'Completed', 'Rejected']:
        req.status = new_status
        req.admin_notes = admin_notes
        
        # If completed or rejected, update item statuses accordingly
        if new_status == 'Completed':
            for item in req.items:
                item.status = 'Collected'
        elif new_status == 'Rejected':
            for item in req.items:
                item.status = 'Available'
        elif new_status in ['Approved', 'In Progress']:
            for item in req.items:
                item.status = 'In Request'

        db_session.commit()
        flash(f'Request {req.request_code} status updated to {new_status}.', 'success')
    else:
        flash('Invalid status provided.', 'warning')

    return redirect(url_for('admin_requests'))

@app.route('/admin/items')
@admin_required
def admin_items():
    category_filter = request.args.get('category', '').strip()
    condition_filter = request.args.get('condition', '').strip()
    search_query = request.args.get('q', '').strip()

    query = db_session.query(EwasteItem)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if condition_filter:
        query = query.filter_by(item_condition=condition_filter)
    if search_query:
        query = query.filter(
            (EwasteItem.item_name.ilike(f"%{search_query}%")) |
            (EwasteItem.location.ilike(f"%{search_query}%"))
        )

    items = query.order_by(EwasteItem.id.desc()).all()
    return render_template('admin/ewaste_items.html', items=items, selected_category=category_filter, selected_condition=condition_filter, search_query=search_query)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = db_session.query(User).order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/centres')
@admin_required
def admin_centres():
    centres = db_session.query(RecyclingCentre).order_by(RecyclingCentre.id.desc()).all()
    return render_template('admin/centres.html', centres=centres)

@app.route('/admin/centres/add', methods=['GET', 'POST'])
@admin_required
def admin_add_centre():
    if request.method == 'POST':
        centre_name = request.form.get('centre_name', '').strip()
        facility_type = request.form.get('facility_type', 'Authorized Recycler').strip()
        complete_address = request.form.get('complete_address', '').strip()
        city = request.form.get('city', 'Bengaluru').strip()
        district = request.form.get('district', '').strip()
        pincode = request.form.get('pincode', '').strip()
        state = request.form.get('state', 'Karnataka').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        contact_email = request.form.get('contact_email', '').strip()
        website_url = request.form.get('website_url', '').strip()
        services_offered = request.form.get('services_offered', '').strip()
        accepted_categories = request.form.get('accepted_categories', '').strip()
        source_url = request.form.get('source_url', '').strip()
        last_verified_str = request.form.get('last_verified_date', '')
        is_official = True if request.form.get('is_official_verified') == '1' else False
        directions_url = request.form.get('directions_url', '').strip()

        if not centre_name or not complete_address or not city or not source_url:
            flash('Centre Name, Address, City, and Official Source URL are required.', 'danger')
            return render_template('admin/centre_form.html', centre=None, action='Add')

        try:
            last_verified_date = datetime.strptime(last_verified_str, '%Y-%m-%d').date() if last_verified_str else date.today()
        except ValueError:
            last_verified_date = date.today()

        new_centre = RecyclingCentre(
            centre_name=centre_name,
            facility_type=facility_type,
            complete_address=complete_address,
            city=city,
            district=district,
            pincode=pincode,
            state=state,
            contact_phone=contact_phone,
            contact_email=contact_email,
            website_url=website_url,
            services_offered=services_offered,
            accepted_categories=accepted_categories,
            source_url=source_url,
            last_verified_date=last_verified_date,
            is_official_verified=is_official,
            directions_url=directions_url or (f"https://www.google.com/maps/search/?api=1&query={centre_name}+{city}" if is_official else None)
        )
        db_session.add(new_centre)
        db_session.commit()

        flash(f'Recycling Centre "{centre_name}" added successfully.', 'success')
        return redirect(url_for('admin_centres'))

    return render_template('admin/centre_form.html', centre=None, action='Add')

@app.route('/admin/centres/edit/<int:centre_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_centre(centre_id):
    centre = db_session.get(RecyclingCentre, centre_id)
    if not centre:
        flash('Centre not found.', 'danger')
        return redirect(url_for('admin_centres'))

    if request.method == 'POST':
        centre.centre_name = request.form.get('centre_name', '').strip()
        centre.facility_type = request.form.get('facility_type', centre.facility_type).strip()
        centre.complete_address = request.form.get('complete_address', '').strip()
        centre.city = request.form.get('city', '').strip()
        centre.district = request.form.get('district', '').strip()
        centre.pincode = request.form.get('pincode', '').strip()
        centre.state = request.form.get('state', '').strip()
        centre.contact_phone = request.form.get('contact_phone', '').strip()
        centre.contact_email = request.form.get('contact_email', '').strip()
        centre.website_url = request.form.get('website_url', '').strip()
        centre.services_offered = request.form.get('services_offered', '').strip()
        centre.accepted_categories = request.form.get('accepted_categories', '').strip()
        centre.source_url = request.form.get('source_url', '').strip()
        centre.directions_url = request.form.get('directions_url', '').strip()
        centre.is_official_verified = True if request.form.get('is_official_verified') == '1' else False
        
        last_verified_str = request.form.get('last_verified_date', '')
        if last_verified_str:
            try:
                centre.last_verified_date = datetime.strptime(last_verified_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        db_session.commit()
        flash(f'Recycling Centre "{centre.centre_name}" updated successfully.', 'success')
        return redirect(url_for('admin_centres'))

    return render_template('admin/centre_form.html', centre=centre, action='Edit')

@app.route('/admin/centres/delete/<int:centre_id>', methods=['POST'])
@admin_required
def admin_delete_centre(centre_id):
    centre = db_session.get(RecyclingCentre, centre_id)
    if centre:
        name = centre.centre_name
        db_session.delete(centre)
        db_session.commit()
        flash(f'Recycling Centre "{name}" deleted.', 'info')
    return redirect(url_for('admin_centres'))

@app.route('/admin/guidelines', methods=['GET', 'POST'])
@admin_required
def admin_guidelines():
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        step_by_step = request.form.get('step_by_step', '').strip()
        dos_and_donts = request.form.get('dos_and_donts', '').strip()
        hazards_prevented = request.form.get('hazards_prevented', '').strip()
        icon_class = request.form.get('icon_class', 'fa-recycle').strip()

        if category and title and summary:
            existing = db_session.query(DisposalGuideline).filter_by(category=category).first()
            if existing:
                existing.title = title
                existing.summary = summary
                existing.step_by_step = step_by_step
                existing.dos_and_donts = dos_and_donts
                existing.hazards_prevented = hazards_prevented
                existing.icon_class = icon_class
                flash(f'Guideline for "{category}" updated successfully.', 'success')
            else:
                new_guide = DisposalGuideline(
                    category=category,
                    title=title,
                    summary=summary,
                    step_by_step=step_by_step,
                    dos_and_donts=dos_and_donts,
                    hazards_prevented=hazards_prevented,
                    icon_class=icon_class
                )
                db_session.add(new_guide)
                flash(f'Guideline for "{category}" created successfully.', 'success')
            db_session.commit()
            return redirect(url_for('admin_guidelines'))

    guidelines = db_session.query(DisposalGuideline).all()
    return render_template('admin/guidance_mgmt.html', guidelines=guidelines)

@app.route('/api/stats')
def api_stats():
    # Return JSON stats for dynamic dashboard charts
    category_counts = db_session.query(
        EwasteItem.category, func.count(EwasteItem.id)
    ).group_by(EwasteItem.category).all()

    status_counts = db_session.query(
        CollectionRequest.status, func.count(CollectionRequest.id)
    ).group_by(CollectionRequest.status).all()

    condition_counts = db_session.query(
        EwasteItem.item_condition, func.count(EwasteItem.id)
    ).group_by(EwasteItem.item_condition).all()

    return jsonify({
        'categories': {c[0]: c[1] for c in category_counts},
        'statuses': {s[0]: s[1] for s in status_counts},
        'conditions': {cond[0]: cond[1] for cond in condition_counts}
    })

# 404 & 500 Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Default to port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
