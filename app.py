#!/usr/bin/env python3
"""
Nextwave Company Website - Flask Application
A dynamic and fully responsive corporate website for Nextwave
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
import os
import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'nextwave_secret_key_2024'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Database setup
DATABASE = 'nextwave.db'

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Users table for admin authentication
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Blog posts table
    c.execute('''CREATE TABLE IF NOT EXISTS blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    category TEXT,
                    featured_image TEXT,
                    published BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Services table
    c.execute('''CREATE TABLE IF NOT EXISTS services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    icon TEXT,
                    featured BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Job listings table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    department TEXT NOT NULL,
                    location TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requirements TEXT,
                    salary_range TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Job applications table
    c.execute('''CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    resume_path TEXT,
                    cover_letter TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )''')
    
    # Contact messages table
    c.execute('''CREATE TABLE IF NOT EXISTS contact_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'unread',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Events table (optional feature)
    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date_time TEXT NOT NULL,
                    location TEXT,
                    category TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Create default admin user
    admin_exists = c.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',)).fetchone()[0]
    if admin_exists == 0:
        password_hash = generate_password_hash('admin123')
        c.execute('INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)',
                 ('admin', password_hash, 'admin@nextwave.com', 'admin'))
    
    # Insert sample data
    insert_sample_data(c)
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def insert_sample_data(cursor):
    """Insert sample data for demonstration"""
    
    # Sample services
    services = [
        ('Web Development', 'Full-stack web development using modern technologies like React, Node.js, and Python.', 'fas fa-code', 1),
        ('Mobile App Development', 'Native and cross-platform mobile applications for iOS and Android.', 'fas fa-mobile-alt', 1),
        ('Cloud Solutions', 'Cloud infrastructure setup and management with AWS, Azure, and Google Cloud.', 'fas fa-cloud', 1),
        ('AI & Machine Learning', 'Custom AI solutions and machine learning model development.', 'fas fa-brain', 1),
        ('Digital Marketing', 'SEO, social media marketing, and digital advertising campaigns.', 'fas fa-chart-line', 0),
        ('Consulting', 'Technology consulting and digital transformation services.', 'fas fa-handshake', 0)
    ]
    
    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO services (title, description, icon, featured) VALUES (?, ?, ?, ?)', services)
    
    # Sample blog posts
    blog_posts = [
        ('The Future of Web Development', 'Exploring emerging trends in web development including AI integration, serverless architecture, and modern frameworks.', 'John Smith', 'Technology', None, 1),
        ('Digital Transformation Guide', 'A comprehensive guide to help businesses navigate their digital transformation journey.', 'Sarah Johnson', 'Business', None, 1),
        ('Cloud Computing Best Practices', 'Essential best practices for implementing cloud solutions in enterprise environments.', 'Mike Chen', 'Technology', None, 1),
        ('Mobile-First Design Strategy', 'Why mobile-first design is crucial for modern web applications and how to implement it.', 'Emily Davis', 'Design', None, 1)
    ]
    
    cursor.execute('SELECT COUNT(*) FROM blog_posts')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO blog_posts (title, content, author, category, featured_image, published) VALUES (?, ?, ?, ?, ?, ?)', blog_posts)
    
    # Sample jobs
    jobs = [
        ('Senior Full-Stack Developer', 'Engineering', 'San Francisco, CA', 'Full-time', 
         'We are looking for a senior full-stack developer to join our growing team. You will work on cutting-edge projects using modern technologies.', 
         'Bachelor\'s degree in Computer Science or related field, 5+ years of experience in full-stack development, proficiency in React, Node.js, and Python', 
         '$120,000 - $150,000', 1),
        ('UI/UX Designer', 'Design', 'Remote', 'Full-time', 
         'Join our design team to create intuitive and beautiful user experiences for our web and mobile applications.', 
         'Bachelor\'s degree in Design or related field, 3+ years of UI/UX experience, proficiency in Figma, Adobe Creative Suite', 
         '$80,000 - $110,000', 1),
        ('DevOps Engineer', 'Engineering', 'New York, NY', 'Full-time', 
         'We need a DevOps engineer to help us scale our infrastructure and improve our deployment processes.', 
         'Bachelor\'s degree in Computer Science or related field, 4+ years of DevOps experience, AWS/Azure certification preferred', 
         '$100,000 - $130,000', 1)
    ]
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('INSERT INTO jobs (title, department, location, type, description, requirements, salary_range, active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', jobs)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Authentication decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page"""
    conn = get_db_connection()
    
    # Get featured services
    featured_services = conn.execute('SELECT * FROM services WHERE featured = 1 LIMIT 4').fetchall()
    
    # Get recent blog posts
    recent_posts = conn.execute('SELECT * FROM blog_posts WHERE published = 1 ORDER BY created_at DESC LIMIT 3').fetchall()
    
    # Get statistics
    stats = {
        'total_projects': 150,
        'happy_clients': 75,
        'team_members': 25,
        'years_experience': 8
    }
    
    conn.close()
    
    return render_template('index.html', 
                         featured_services=featured_services,
                         recent_posts=recent_posts,
                         stats=stats)

@app.route('/about')
def about():
    """About page"""
    team_members = [
        {'name': 'John Smith', 'position': 'CEO & Founder', 'image': 'team1.jpg'},
        {'name': 'Sarah Johnson', 'position': 'CTO', 'image': 'team2.jpg'},
        {'name': 'Mike Chen', 'position': 'Lead Developer', 'image': 'team3.jpg'},
        {'name': 'Emily Davis', 'position': 'Design Director', 'image': 'team4.jpg'}
    ]
    
    return render_template('about.html', team_members=team_members)

@app.route('/services')
def services():
    """Services page"""
    conn = get_db_connection()
    all_services = conn.execute('SELECT * FROM services ORDER BY featured DESC, title').fetchall()
    conn.close()
    
    return render_template('services.html', services=all_services)

@app.route('/blog')
def blog():
    """Blog page"""
    conn = get_db_connection()
    
    # Get search and category filters
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    
    query = 'SELECT * FROM blog_posts WHERE published = 1'
    params = []
    
    if search_query:
        query += ' AND (title LIKE ? OR content LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
    
    query += ' ORDER BY created_at DESC'
    
    posts = conn.execute(query, params).fetchall()
    
    # Get categories for filter
    categories = conn.execute('SELECT DISTINCT category FROM blog_posts WHERE published = 1').fetchall()
    
    conn.close()
    
    return render_template('blog.html', 
                         posts=posts, 
                         categories=categories,
                         search_query=search_query,
                         category_filter=category_filter)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    """Individual blog post page"""
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM blog_posts WHERE id = ? AND published = 1', (post_id,)).fetchone()
    
    if not post:
        conn.close()
        return render_template('404.html'), 404
    
    # Get related posts
    related_posts = conn.execute(
        'SELECT * FROM blog_posts WHERE id != ? AND category = ? AND published = 1 ORDER BY created_at DESC LIMIT 3',
        (post_id, post['category'])
    ).fetchall()
    
    conn.close()
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@app.route('/careers')
def careers():
    """Careers page"""
    conn = get_db_connection()
    
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    department_filter = request.args.get('department', '')
    location_filter = request.args.get('location', '')
    
    query = 'SELECT * FROM jobs WHERE active = 1'
    params = []
    
    if search_query:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search_query}%', f'%{search_query}%'])
    
    if department_filter:
        query += ' AND department = ?'
        params.append(department_filter)
    
    if location_filter:
        query += ' AND location LIKE ?'
        params.append(f'%{location_filter}%')
    
    query += ' ORDER BY created_at DESC'
    
    jobs = conn.execute(query, params).fetchall()
    
    # Get departments and locations for filters
    departments = conn.execute('SELECT DISTINCT department FROM jobs WHERE active = 1').fetchall()
    locations = conn.execute('SELECT DISTINCT location FROM jobs WHERE active = 1').fetchall()
    
    conn.close()
    
    return render_template('careers.html', 
                         jobs=jobs,
                         departments=departments,
                         locations=locations,
                         search_query=search_query,
                         department_filter=department_filter,
                         location_filter=location_filter)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ? AND active = 1', (job_id,)).fetchone()
    
    if not job:
        conn.close()
        return render_template('404.html'), 404
    
    conn.close()
    
    return render_template('job_detail.html', job=job)

@app.route('/apply/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    """Job application form"""
    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ? AND active = 1', (job_id,)).fetchone()
    
    if not job:
        conn.close()
        return render_template('404.html'), 404
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        cover_letter = request.form.get('cover_letter', '')
        
        # Handle file upload (resume)
        resume_path = None
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename:
                filename = secure_filename(file.filename)
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(resume_path)
        
        # Save application
        conn.execute(
            'INSERT INTO job_applications (job_id, name, email, phone, resume_path, cover_letter) VALUES (?, ?, ?, ?, ?, ?)',
            (job_id, name, email, phone, resume_path, cover_letter)
        )
        conn.commit()
        conn.close()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('careers'))
    
    conn.close()
    return render_template('apply.html', job=job)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
            (name, email, subject, message)
        )
        conn.commit()
        conn.close()
        
        flash('Message sent successfully! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db_connection()
    
    # Get statistics
    stats = {
        'total_posts': conn.execute('SELECT COUNT(*) FROM blog_posts').fetchone()[0],
        'published_posts': conn.execute('SELECT COUNT(*) FROM blog_posts WHERE published = 1').fetchone()[0],
        'total_services': conn.execute('SELECT COUNT(*) FROM services').fetchone()[0],
        'active_jobs': conn.execute('SELECT COUNT(*) FROM jobs WHERE active = 1').fetchone()[0],
        'pending_applications': conn.execute('SELECT COUNT(*) FROM job_applications WHERE status = "pending"').fetchone()[0],
        'unread_messages': conn.execute('SELECT COUNT(*) FROM contact_messages WHERE status = "unread"').fetchone()[0]
    }
    
    # Get recent activities
    recent_messages = conn.execute('SELECT * FROM contact_messages ORDER BY created_at DESC LIMIT 5').fetchall()
    recent_applications = conn.execute(
        'SELECT ja.*, j.title as job_title FROM job_applications ja JOIN jobs j ON ja.job_id = j.id ORDER BY ja.created_at DESC LIMIT 5'
    ).fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                         stats=stats,
                         recent_messages=recent_messages,
                         recent_applications=recent_applications)

# API routes for theme toggle and search
@app.route('/api/toggle-theme', methods=['POST'])
def toggle_theme():
    """Toggle dark/light theme"""
    theme = request.json.get('theme', 'light')
    session['theme'] = theme
    return jsonify({'success': True, 'theme': theme})

@app.route('/api/search')
def api_search():
    """Global search API"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'results': []})
    
    conn = get_db_connection()
    results = []
    
    # Search blog posts
    blog_results = conn.execute(
        'SELECT title, "blog" as type, id FROM blog_posts WHERE (title LIKE ? OR content LIKE ?) AND published = 1 LIMIT 3',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    
    for post in blog_results:
        results.append({
            'title': post['title'],
            'type': 'Blog Post',
            'url': f'/blog/{post["id"]}'
        })
    
    # Search services
    service_results = conn.execute(
        'SELECT title, "service" as type, id FROM services WHERE title LIKE ? OR description LIKE ? LIMIT 3',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    
    for service in service_results:
        results.append({
            'title': service['title'],
            'type': 'Service',
            'url': '/services'
        })
    
    # Search jobs
    job_results = conn.execute(
        'SELECT title, "job" as type, id FROM jobs WHERE (title LIKE ? OR description LIKE ?) AND active = 1 LIMIT 3',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    
    for job in job_results:
        results.append({
            'title': job['title'],
            'type': 'Job Opening',
            'url': f'/job/{job["id"]}'
        })
    
    conn.close()
    
    return jsonify({'results': results})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create required directories
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('templates/admin', exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)