from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta
from sqlalchemy.sql import func
from flask_migrate import Migrate


app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///toke.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'whyshouldidoitforfree'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class Toke(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    toke_count = db.Column(db.Float, nullable=False)
    hours_worked = db.Column(db.Float, nullable=False, default=0)  # New Column
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

    # Get the current year
    current_year = date.today().year

    # Calculate all weeks in the year
    start_of_year = date(current_year, 1, 1)
    start_of_week = start_of_year - timedelta(days=start_of_year.weekday())  # Start from the first Monday
    available_weeks = []
    for i in range(52):  # Assuming 52 weeks in a year
        week_start = start_of_week + timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        if week_start.year > current_year:
            break  # Stop if the week goes into the next year
        available_weeks.append({
            "id": f"week-{i + 1}",
            "label": f"Week {i + 1} ({week_start} - {week_end})",
            "start_date": week_start,
            "end_date": week_end,
        })

    # Get the selected week
    selected_week_id = request.args.get('selected_week', available_weeks[0]['id'])
    selected_week = next((week for week in available_weeks if week['id'] == selected_week_id), available_weeks[0])

    # Get the start and end dates for the selected week
    start_of_week = selected_week["start_date"]
    end_of_week = selected_week["end_date"]

    # Generate days for the selected week
    week_days = [
        {
            "date": (start_of_week + timedelta(days=i)).strftime('%Y-%m-%d'),
            "label": (start_of_week + timedelta(days=i)).strftime('%A, %B %d'),
        }
        for i in range(7)
    ]

    # Initialize weekly data
    weekly_tokes = {day["date"]: {"amount": 0, "hours": 0} for day in week_days}
    weekly_total = 0
    total_hours = 0

    # Handle form submission
    if request.method == 'POST' and user_role == 'admin':
        selected_day = datetime.strptime(request.form.get('day'), '%Y-%m-%d').date()
        toke_count = float(request.form.get('toke_count'))
        hours_worked = float(request.form.get('hours_worked'))

        # Check if an entry already exists
        existing_entry = Toke.query.filter_by(date=selected_day).first()
        if existing_entry:
            existing_entry.toke_count = toke_count
            existing_entry.hours_worked = hours_worked
            flash('Toke entry updated successfully.', 'success')
        else:
            new_toke = Toke(date=selected_day, toke_count=toke_count, hours_worked=hours_worked, added_by="Admin")
            db.session.add(new_toke)
            flash('Toke entry added successfully.', 'success')
        db.session.commit()

        # Redirect to refresh data
        return redirect(url_for('toke', selected_week=selected_week_id))

    # Fetch the latest data for the selected week
    toke_entries = Toke.query.filter(Toke.date.between(start_of_week, end_of_week)).all()
    for entry in toke_entries:
        day_str = entry.date.strftime('%Y-%m-%d')
        weekly_tokes[day_str] = {"amount": entry.toke_count, "hours": entry.hours_worked}

    # Recalculate weekly totals
    weekly_total = sum([data["amount"] for data in weekly_tokes.values()])
    total_hours = sum([data["hours"] for data in weekly_tokes.values()])

    # Pre-fill values for the selected day (if available)
    selected_day = request.args.get('day', date.today().strftime('%Y-%m-%d'))
    existing_entry = Toke.query.filter_by(date=datetime.strptime(selected_day, '%Y-%m-%d').date()).first()
    prefilled_values = {
        "toke_count": existing_entry.toke_count if existing_entry else "",
        "hours_worked": existing_entry.hours_worked if existing_entry else "",
    }

    # Render the updated template
    return render_template(
        'toke.html',
        current_week_label=selected_week["label"],
        current_week_id=selected_week_id,
        available_weeks=available_weeks,
        weekly_tokes=weekly_tokes,
        weekly_total=weekly_total,
        total_hours=total_hours,
        week_days=week_days,
        prefilled_values=prefilled_values,
        selected_day=selected_day,
        is_admin=(user_role == 'admin'),
    )

@app.route('/toke/history')
def toke_history():
    user_role = session.get('user_role')
    if user_role != 'dealer':
        flash('Access denied.', 'danger')
        return redirect('/login')

    history_data = []
    for i in range(1, 5):  # Fetch last 4 weeks
        start_date = date.today() - timedelta(days=i * 7)
        end_date = start_date + timedelta(days=6)
        week_data = Toke.query.filter(Toke.date.between(start_date, end_date)).all()
        weekly_total = sum(toke.toke_count for toke in week_data)
        history_data.append({
            "label": f"{start_date} - {end_date}",
            "days": {toke.date.strftime("%A"): toke.toke_count for toke in week_data},
            "weekly_total": weekly_total
        })
    return render_template('history.html', history_data=history_data)

@app.route('/toke/summary')
def toke_summary():
    user_role = session.get('user_role')
    if user_role != 'admin':
        flash('Access denied.', 'danger')
        return redirect('/login')

    today = date.today()
    start_date = today - timedelta(days=14)
    biweekly_data = Toke.query.filter(Toke.date >= start_date).all()

    summary = {"weeks": {}, "weekly_totals": {}, "biweekly_total": 0, "total_hours": 0, "toke_rate": 0}
    for i in range(2):
        week_start = start_date + timedelta(days=i * 7)
        week_end = week_start + timedelta(days=6)
        week_data = [toke for toke in biweekly_data if week_start <= toke.date <= week_end]
        weekly_total = sum(toke.toke_count for toke in week_data)
        summary["weeks"][i + 1] = {toke.date.strftime("%A"): toke.toke_count for toke in week_data}
        summary["weekly_totals"][i + 1] = weekly_total
        summary["biweekly_total"] += weekly_total

    summary["total_hours"] = 80
    summary["toke_rate"] = summary["biweekly_total"] / summary["total_hours"] if summary["total_hours"] > 0 else 0

    return render_template('summary.html', summary_data=summary, pay_period={"label": f"{start_date} - {today}"})

@app.route('/toke/delete/<int:toke_id>', methods=['POST'])
def delete_toke(toke_id):
    try:
        toke_entry = Toke.query.get_or_404(toke_id)
        db.session.delete(toke_entry)
        db.session.commit()
        return redirect('/toke')
    except Exception as e:
        return f"An error occurred: {e}"

# Casino Updates Routes (unchanged)

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

# Miscellaneous Routes (unchanged)
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
    if game not in valid_games:
        flash("Invalid game selected.", 'danger')
        return redirect('/tips')

    template = f'{game}_manual.html' if request.path.endswith('/manual') else f'{game}.html'
    try:
        return render_template(template)
    except:
        flash(f"The page {template} does not exist.", "warning")
        return redirect('/tips')

@app.route('/tips/carnival')
def carnival():
    return render_template('carnival.html')

@app.route('/tips/carnival/<string:game>')
@app.route('/tips/carnival/<string:game>/manual')
def carnival_game(game):
    valid_games = [
        "high_card_flush", "mississippi_stud", "pai_gow",
        "three_card_poker", "spanish21", "war", "ultimate"
    ]
    if game not in valid_games:
        flash("Invalid game selected.", "danger")
        return redirect('/tips/carnival')

    template = f'{game}_manual.html' if request.path.endswith('/manual') else f'{game}.html'
    try:
        return render_template(template)
    except:
        flash(f"The page {template} does not exist.", "warning")
        return redirect('/tips/carnival')

# Initialize and Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
