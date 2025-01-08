from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toke.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'replace_with_your_randomly_generated_key'
db = SQLAlchemy(app)

# Database Models
class Toke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    toke_count = db.Column(db.Float, nullable=False)
    added_by = db.Column(db.String(50), nullable=False)

class CasinoUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'luckys' and password == 'windcreek1111':  # Dealer login
            session['user_role'] = 'dealer'
            flash('Login successful as Dealer!', 'success')
            return redirect('/toke')
        elif username == 'admin' and password == '1111WindCreek$2024':  # Admin login
            session['user_role'] = 'admin'
            flash('Login successful as Admin!', 'success')
            return redirect('/toke')
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_role', None)
    flash('You have been logged out.', 'info')
    return redirect('/login')

# Toke Management Routes
@app.route('/toke', methods=['GET', 'POST'])
def toke():
    user_role = session.get('user_role')
    
    if not user_role:
        flash('Please log in to access the Toke page.', 'danger')
        return redirect('/login')
    
    if request.method == 'POST' and user_role == 'admin':
        new_toke_count = request.form.get('toke_count')
        try:
            new_toke = Toke(date=date.today(), toke_count=float(new_toke_count), added_by="Admin")
            db.session.add(new_toke)
            db.session.commit()
        except Exception as e:
            return f"An error occurred: {e}"
    
    toke_data = Toke.query.order_by(Toke.date.desc()).all()
    total_toke_count = db.session.query(func.sum(Toke.toke_count)).scalar() or 0.0
    current_week_tokes = Toke.query.filter(Toke.date >= (date.today() - timedelta(days=7))).all()
    weekly_tip_rate = sum([toke.toke_count for toke in current_week_tokes])
    
    return render_template(
        'toke.html', 
        toke_data=toke_data, 
        total_toke_count=total_toke_count, 
        weekly_tip_rate=weekly_tip_rate if user_role == 'dealer' else None, 
        is_admin=(user_role == 'admin')
    )

@app.route('/toke/delete/<int:toke_id>', methods=['POST'])
def delete_toke(toke_id):
    try:
        toke_entry = Toke.query.get_or_404(toke_id)
        db.session.delete(toke_entry)
        db.session.commit()
        return redirect('/toke')
    except Exception as e:
        return f"An error occurred: {e}"

# Casino Updates Routes
@app.route('/updates')
def updates():
    updates = CasinoUpdate.query.order_by(CasinoUpdate.date_posted.desc()).all()
    is_admin = session.get('user_role') == 'admin'
    return render_template('updates.html', updates=updates, is_admin=is_admin)

@app.route('/admin/updates', methods=['GET', 'POST'])
def manage_updates():
    if session.get('user_role') != 'admin':
        flash('Access denied. Please log in as admin.', 'danger')
        return redirect('/login')
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        if title and content:
            new_update = CasinoUpdate(title=title, content=content)
            db.session.add(new_update)
            db.session.commit()
            flash('Casino update added successfully!', 'success')
        else:
            flash('Both title and content are required.', 'danger')

    updates = CasinoUpdate.query.order_by(CasinoUpdate.date_posted.desc()).all()
    return render_template('manage_updates.html', updates=updates)

@app.route('/admin/updates/delete/<int:update_id>', methods=['POST'])
def delete_update(update_id):
    if session.get('user_role') != 'admin':
        flash('Access denied. Please log in as admin.', 'danger')
        return redirect('/login')

    update = CasinoUpdate.query.get_or_404(update_id)
    db.session.delete(update)
    db.session.commit()
    flash('Casino update deleted successfully!', 'success')
    return redirect('/admin/updates')

# Miscellaneous Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tricks')
def tricks():
    return render_template('tricks.html')

@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/stores')
def stores():
    return render_template('stores.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')

# Organize remaining "Tips" routes by category
@app.route('/tips/<string:game>')
@app.route('/tips/<string:game>/manual')
def main_game(game):
    valid_games = ["craps", "roulette", "blackjack", "baccarat"]
    # Check if the game is valid
    if game not in valid_games:
        flash("Invalid game selected.", "danger")
        return redirect('/tips')

    # Check if the user requested the manual
    if request.path.endswith('/manual'):
        template = f'{game}_manual.html'
    else:
        template = f'{game}.html'

    # Render the appropriate template
    try:
        return render_template(template)
    except:
        flash(f"The page {template} does not exist.", "warning")
        return redirect('/tips')


@app.route('/tips/carnival')
def carnival():
    return render_template(f'carnival.html')

@app.route('/tips/carnival/<string:game>')
@app.route('/tips/carnival/<string:game>/manual')
def carnival_game(game):
    valid_games = [
        "high_card_flush", 
        "mississippi_stud", 
        "pai_gow", 
        "three_card_poker", 
        "spanish21", 
        "war", 
        "ultimate"
    ]
    # Check if the game is valid
    if game not in valid_games:
        flash("Invalid game selected.", "danger")
        return redirect('/tips/carnival')

    # Check if the user requested the manual
    if request.path.endswith('/manual'):
        template = f'{game}_manual.html'
    else:
        template = f'{game}.html'

    # Render the appropriate template
    try:
        return render_template(template)
    except:
        flash(f"The page {template} does not exist.", "warning")
        return redirect('/tips/carnival')

# Initialize and Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
