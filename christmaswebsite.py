from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wishlist.db'  # Use SQLite as an example, change this to your desired database
db = SQLAlchemy(app)

participants = ['Gavin', 'Mum', 'Dad', 'Caitlin', 'Iain', 'Alastair', 'Douglas', 'Josh', 'Aaron']

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    gifts = db.Column(db.String(500))


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_name = request.form.get('name').lower().strip()
        user_name = user_name[0].upper() + user_name[1:]
        if user_name in participants:
            return redirect(url_for('choices', user_name=user_name))
    return render_template('home.html')

@app.route('/choices/<user_name>', methods=['GET'])
def choices(user_name):
    return render_template('choicepage.html', user_name=user_name)

@app.route('/submit_request/<user_name>', methods=['GET', 'POST'])
def submit_request(user_name):
    if request.method == 'POST':
        gift_list = request.form.get('gifts').split(',')
        gift_list = [x.strip().lower() for x in gift_list]
        gift_list = [x for x in gift_list if x != '']

        # Query the database to get the user's wishlist
        user_wishlist = Wishlist.query.filter_by(user_name=user_name).first()

        if user_wishlist:
            # If the user already has a wishlist, update it
            user_wishlist.gifts = ','.join(gift_list)
        else:
            # If the user doesn't have a wishlist, create a new entry
            new_wishlist = Wishlist(user_name=user_name, gifts=','.join(gift_list))
            db.session.add(new_wishlist)

        db.session.commit()

        return render_template('home.html')

    return render_template('submitrequest.html', user_name=user_name)

@app.route('/view_wishlists/<user_name>', methods=['GET', 'POST'])
def view_wishlists(user_name):
    all_wishlists = Wishlist.query.all()
    wishlist_data = {}

    for entry in all_wishlists:
        wishlist_data[entry.user_name] = entry.gifts.split(',')

    return render_template('wishlist.html', user_name=user_name, wishlists=wishlist_data)

@app.route('/remove_item/<user_name>/<item>', methods=['GET'])
def remove_item(user_name, item):
    user_wishlist = Wishlist.query.filter_by(user_name=user_name).first()
    if user_wishlist and item in user_wishlist.gifts.split(','):
        gifts = [gift for gift in user_wishlist.gifts.split(',') if gift != item]
        user_wishlist.gifts = ','.join(gifts)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
