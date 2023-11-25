from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# INSERT PASSWORDS FOR USERS HERE IF DESIRED
# passwords_dict = {
# }

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

participants = []

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    gifts = db.Column(db.String(500))

class TotalWishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    gifts = db.Column(db.String(500))

@app.route('/', methods=['GET', 'POST'])
def home():
    error_message = None  # Initialize the error message
    if request.method == 'POST':
        pass_word = request.form.get('password').lower()
        user_name = request.form.get('name').lower().strip()
        user_name = user_name[0].upper() + user_name[1:]
        if user_name in participants and pass_word==passwords_dict[user_name]:
            return redirect(url_for('choices', user_name=user_name))
        else:
            error_message = "Incorrect username or password. Please try again."
    return render_template('home.html', error_message = error_message)

@app.route('/choices/<user_name>', methods=['GET'])
def choices(user_name):
    totaluser_wishlist = TotalWishlist.query.filter_by(user_name=user_name).first()
    if totaluser_wishlist:
        gifts_to_display = totaluser_wishlist.gifts.replace(",", ", ")
    else:
        gifts_to_display = ''
    return render_template('choicepage.html', user_name=user_name, gifts_to_display=gifts_to_display)

@app.route('/submit_request/<user_name>', methods=['GET', 'POST'])
def submit_request(user_name):
    success_message = None
    if request.method == 'POST':
        gift_list = request.form.get('gifts').split(',')
        gift_list = [x.strip().lower() for x in gift_list]
        gift_list = [x for x in gift_list if x != '']

        # Query the database to get the user's wishlist
        user_wishlist = Wishlist.query.filter_by(user_name=user_name).first()
        totaluser_wishlist = TotalWishlist.query.filter_by(user_name=user_name).first()

        if totaluser_wishlist:
            current_total_gifts = totaluser_wishlist.gifts.split(',')
            totaluser_wishlist.gifts = ','.join(current_total_gifts + gift_list)
        else:
            new_totalwishlist = TotalWishlist(user_name=user_name, gifts=','.join(gift_list))
            db.session.add(new_totalwishlist)

        if user_wishlist:
            # If the user already has a wishlist, update it
            current_gifts = user_wishlist.gifts.split(',')
            new_gifts = [gift for gift in gift_list if gift not in current_gifts]
            user_wishlist.gifts = ','.join(current_gifts + new_gifts)

        else:
            # If the user doesn't have a wishlist, create a new entry
            new_wishlist = Wishlist(user_name=user_name, gifts=','.join(gift_list))
            db.session.add(new_wishlist)


        db.session.commit()

        success_message = f"Submitted the following items to your wishlist: {gift_list}"

        return render_template('submitrequest.html', user_name=user_name, success_message=success_message)

    return render_template('submitrequest.html', user_name=user_name, success_message=success_message)

@app.route('/view_wishlists/<user_name>', methods=['GET', 'POST'])
def view_wishlists(user_name):
    all_wishlists = Wishlist.query.all()
    wishlist_data = {}

    for entry in all_wishlists:
        wishlist_data[entry.user_name] = entry.gifts.split(',')

    return render_template('wishlist.html', user_name=user_name, wishlists=wishlist_data)

@app.route('/confirm_removal/<user_name>/<user_name_of_removed>/<item>', methods=['GET', 'POST'])
def remove_confirm_page(user_name, user_name_of_removed, item):
    return render_template('removeconfirm.html', user_name=user_name, user_name_of_removed=user_name_of_removed, item=item)


@app.route('/remove_item/<user_name_of_removed>/<item>', methods=['GET'])
def remove_item(user_name_of_removed, item):  # Fix the parameter name here
    user_wishlist = Wishlist.query.filter_by(user_name=user_name_of_removed).first()
    if user_wishlist is not None and user_wishlist.gifts:
        gifts = [gift for gift in user_wishlist.gifts.split(',') if gift != item]
        user_wishlist.gifts = ','.join(gifts)
        db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
