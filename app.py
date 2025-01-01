from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/toke', methods=['GET', 'POST'])
def toke():
    # Check if user is authorized (you'll handle authentication later)
    is_admin = True  # Change this based on authentication logic

    if request.method == 'POST' and is_admin:
        # Get data from form and update the toke count
        new_toke_count = request.form.get('toke_count')
        # Save to a database or a file
        with open('toke_data.txt', 'w') as f:
            f.write(new_toke_count)
    
    # Retrieve the current toke count
    try:
        with open('toke_data.txt', 'r') as f:
            current_toke_count = f.read()
    except FileNotFoundError:
        current_toke_count = "No data yet."

    return render_template('toke.html', current_toke_count=current_toke_count, is_admin=is_admin)

@app.route('/tricks')
def tricks():
    return render_template('tricks.html')

@app.route('/updates')
def updates():
    return render_template('updates.html')

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

@app.route('/tips/craps')
def craps():
    return render_template('craps.html')


@app.route('/tips/roulette')
def roulette_tips():
    return render_template('roulette.html')


@app.route('/tips/blackjack')
def blackjack_tips():
    return render_template('blackjack.html')

@app.route('/tips/baccarat')
def baccarat_tips():
    return render_template('baccarat.html')

@app.route('/tips/carnival')
def carnival_tips():
    return render_template('carnival.html')

@app.route('/tips/carnival/high_card_flush')
def high_card_flush():
    return render_template('high_card_flush.html')

@app.route('/tips/carnival/mississippi_stud')
def mississippi_stud():
    return render_template('mississippi_stud.html')

@app.route('/tips/carnival/pai_gow')
def pai_gow():
    return render_template('pai_gow.html')

@app.route('/tips/carnival/spanish21')
def spanish21():
    return render_template('spanish21.html')

@app.route('/tips/carnival/three_card_poker')
def three_card_poker():
    return render_template('three_card_poker.html')

@app.route('/tips/carnival/war')
def war():
    return render_template('war.html')

@app.route('/tips/carnival/ultimate')
def ultimate():
    return render_template('ultimate.html')

@app.route('/tips/carnival/ultimate/ultimate_manual')
def ultimate_manual():
    return render_template('ultimate_manual.html')

@app.route('/tips/carnival/high_card_flush/high_card_flush_manual')
def high_card_flush_manual():
    return render_template('high_card_flush_manual.html')

@app.route('/tips/carnival/War/War_manual')
def war_manual():
    return render_template('war_manual.html')

@app.route('/tips/carnival/pai_gow/pai_gow_manual')
def pai_gow_manual():
    return render_template('pai_gow_manual.html')

@app.route('/tips/carnival/three_card_poker/three_card_poker_manual')
def three_card_poker_manual():
    return render_template('three_card_poker_manual.html')

@app.route('/tips/carnival/mississippi_stud/mississippi_stud_manual')
def mississippi_stud_manual():
    return render_template('mississippi_stud_manual.html')

@app.route('/tips/carnival/spanish21/Spanish_21_manual')
def Spanish_21_manual():
    return render_template('spanish21_manual.html')

@app.route('/tips/baccarat/baccarat_manual')
def baccarat_manual():
    return render_template('baccarat_manual.html')

@app.route('/tips/blackjack/blackjack_manual')
def blackjack_manual():
    return render_template('blackjack_manual.html')

@app.route('/tips/craps/craps_manual')
def craps_manual():
    return render_template('craps_manual.html')

@app.route('/tips/roulette/roulette_manual')
def roulette_manual():
    return render_template('roulette_manual.html')

if __name__ == '__main__':
    app.run(debug=True)