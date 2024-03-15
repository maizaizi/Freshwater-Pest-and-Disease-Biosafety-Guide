from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from db import getCursor 
from flask_hashing import Hashing
hashing = Hashing()
user_bp = Blueprint('user_dashboard', __name__)

# http://127.0.0.1:5000/home - this will be the home page, only accessible for loggedin users

@user_bp.route('/home')
def home():
    if 'loggedin' in session:
        # If user is logged in, render the home page with the user's username
        return render_template('user_home.html', username=session['username'])
    # Redirect to the login page if not logged in
    return redirect(url_for('login'))


@user_bp.route('/userprofile')
def userprofile():
    if 'loggedin' in session:
        cursor = getCursor()  # Get database cursor
        username = session['username']  # Get the username from session
        # Execute SQL query to fetch user profile details
        cursor.execute('''
            SELECT s.username, r.FirstName, r.LastName, r.Email, r.Address, r.Phonenumber
            FROM secureaccount s
            JOIN RiverUsers r ON s.id = r.secureaccount_id
            WHERE s.username = %s
        ''', (username,))
        account = cursor.fetchone()  # Fetch the user profile details
        return render_template('user_profile.html', account=account)  # Render the profile page with account info
    return redirect(url_for('login'))  # Redirect to login if not logged in


@user_bp.route('/edit_profile', methods=['GET'])
def edit_profile():
    if 'loggedin' in session:
        cursor = getCursor()
        username = session['username']
        # Fetch the user's current profile information from the database
        cursor.execute('''
            SELECT s.username, r.FirstName, r.LastName, r.Email, r.Address, r.Phonenumber
            FROM secureaccount s
            JOIN RiverUsers r ON s.id = r.secureaccount_id
            WHERE s.username= %s
        ''', (username,))
        account = cursor.fetchone()
        if account:
            # If account exists, render the profile edit page with current information
            return render_template('user_update_profile.html', account={
                'username': account[0], 'firstname': account[1], 'lastname': account[2], 
                'email': account[3], 'address': account[4], 'phonenumber': account[5]
            })
        else:
            # Redirect to login if account does not exist (which is an unusual case)
            return redirect(url_for('login'))
    else:
        # Redirect to login if not logged in
        return redirect(url_for('login'))


@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session and request.method == 'POST':
        # Retrieve updated profile information from the form
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        username = session['username']
        account_info = {
            'firstname': firstname, 'lastname': lastname, 'address': address,
            'email': email, 'phonenumber': phonenumber
        }
        try:
            cursor = getCursor()
            # Update the user's profile information in the database
            cursor.execute('''
                UPDATE RiverUsers
                SET FirstName = %s, LastName = %s, Email = %s, Address = %s, Phonenumber = %s
                WHERE username = %s
            ''', (firstname, lastname, email, address, phonenumber, username))
            return redirect(url_for('user_bp.userprofile'))  # Redirect to the user profile page
        except Exception as e:
            # Render the profile update page with an error message if update fails
            return render_template('user_update_profile.html', error_message="Failed to update profile", account=account_info)
    else:
        # Redirect to the login page if not logged in or if the request method is not POST
        return redirect(url_for('login'))


@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    if request.method == 'POST':
        # Retrieve password information from the form
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        if new_password != confirm_password:
            flash("New passwords do not match.")  # Show error if new passwords do not match
            return redirect(url_for('user_bp.change_password'))
        cursor = getCursor()
        username = session['username']
        # Fetch the current password from the database
        cursor.execute('SELECT password FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account and hashing.check_value(account[0], current_password, salt='S1#e2!r3@t4$'):
            # If the current password is correct, update the password in the database
            hashed_password = hashing.hash_value(new_password, salt='S1#e2!r3@t4$')
            cursor.execute('''
                UPDATE secureaccount
                SET password = %s
                WHERE username = %s
            ''', (hashed_password, username))
            flash('Your password has been updated successfully.')  # Notify the user of success
            return redirect(url_for('user_bp.userprofile'))
        else:
            flash('Incorrect current password.')  # Notify the user of incorrect current password
            return redirect(url_for('user_bp.change_password'))
    return render_template('user_change_password.html')  # Render the password change form

@user_bp.route('/guide')
def guide():
    cursor = getCursor()  # Get the database cursor
    # Retrieve all guide entries from the database
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE')
    result = cursor.fetchall()
    # Convert the result into a list of dictionaries for easier access in the template
    columns = [desc[0] for desc in cursor.description]
    pests_and_diseases = [dict(zip(columns, row)) for row in result]
    return render_template('user_view_guide.html', pests_and_diseases=pests_and_diseases)

@user_bp.route('/detailed_view/<int:item_id>')
def detailed_view(item_id):
    cursor = getCursor()  # Get the database cursor
    # Retrieve the specific guide entry from the database using its ID
    cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
    item = cursor.fetchone()  # Fetch the main item details
    # Fetch additional images associated with this guide entry
    cursor.execute("SELECT AdditionalFilename FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
    additional_images = [row[0] for row in cursor.fetchall()]
    cursor.close()  # Close the database cursor
    return render_template('user_guide_detail.html', item=item, additional_images=additional_images)  # Render the detailed view page
