from flask import Blueprint, session, render_template, redirect, url_for, request, flash
from db import getCursor 
from flask_hashing import Hashing
hashing = Hashing()
user_bp = Blueprint('user_dashboard', __name__)

# http://127.0.0.1:5000/home - this will be the home page, only accessible for loggedin users
@user_bp.route('/home')
def home():

    if 'loggedin' in session:
        return render_template('user_home.html', username=session['username'])
    return redirect(url_for('login'))

@user_bp.route('/userprofile')
def userprofile():
    # Check if user is logged in
    if 'loggedin' in session:
        # Get database cursor
        cursor = getCursor()
        username = session['username']
        # Execute SQL query to fetch user profile details
        cursor.execute('''
            SELECT s.username, r.FirstName, r.LastName, r.Email, r.Address, r.Phonenumber
            FROM secureaccount s
            JOIN RiverUsers r ON s.id = r.secureaccount_id
            WHERE s.username = %s
        ''', (username,))

        # Fetch the user profile details
        account = cursor.fetchone()

        # Show the profile page with account info
        return render_template('user_profile.html', account=account)
    # If user is not logged in, redirect to login page
    return redirect(url_for('login'))



@user_bp.route('/edit_profile', methods=['GET'])
def edit_profile():
    if 'loggedin' in session:

        cursor = getCursor()
        username = session['username']
        cursor.execute('''
            SELECT s.username, r.FirstName, r.LastName, r.Email, r.Address, r.Phonenumber
            FROM secureaccount s
            JOIN RiverUsers r ON s.id = r.secureaccount_id
            WHERE  s.username= %s
        ''', (username,))

        account = cursor.fetchone()
        
        if account:
        
            return render_template('user_update_profile.html', account={'username': account[0], 'firstname': account[1], 'lastname': account[2], 'email': account[3], 'address': account[4], 'phonenumber': account[5]})
        else:
            return redirect(url_for('login'))  
    else:
        return redirect(url_for('login'))




@user_bp.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session and request.method == 'POST':
        
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        
        
        username = session['username']
        account_info = {
            'firstname': firstname,
            'lastname': lastname,
            'address': address,
            'email': email,
            'phonenumber': phonenumber,
           
        }

        try:
            cursor = getCursor()
            cursor.execute('''
                UPDATE RiverUsers
                SET FirstName = %s, LastName = %s, Email = %s, Address = %s, Phonenumber = %s
                WHERE username = %s
            ''', (firstname, lastname, email, address, phonenumber, username))

           
            return redirect(url_for('profile_bp.userprofile'))
        except Exception as e:
           
            return render_template('user_update_profile.html', error_message="Failed to update profile", account=account_info)
    else:
        return redirect(url_for('login'))


@user_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('change_password'))

        cursor = getCursor()
        username = session['username']
        cursor.execute('SELECT password FROM secureaccount WHERE username = %s', (username,))

        account = cursor.fetchone()

        if account and hashing.check_value(account[0], current_password, salt='S1#e2!r3@t4$'):
            
            hashed_password = hashing.hash_value(new_password, salt='S1#e2!r3@t4$')  
            cursor.execute('''
                UPDATE secureaccount
                SET password = %s
                WHERE username = %s
            ''', (hashed_password, username))

            flash('Your password has been updated successfully.')
            return redirect(url_for('user_dashboard.userprofile')) 
        else:
            flash('Incorrect current password.')
            return redirect(url_for('change_password'))

    return render_template('user_change_password.html')

@user_bp.route('/guide')
def guide():
    cursor = getCursor()
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE')
    result = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    pests_and_diseases = [dict(zip(columns, row)) for row in result] 
    return render_template('user_view_guide.html', pests_and_diseases=pests_and_diseases)

@user_bp.route('/detailed_view/<int:item_id>')
def detailed_view(item_id):
    cursor = getCursor()
    cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
    item = cursor.fetchone()
    cursor.execute("SELECT AdditionalFilename FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
    additional_images = [row[0] for row in cursor.fetchall()] 
    cursor.close()
    return render_template('user_guide_detail.html', item=item, additional_images=additional_images)
