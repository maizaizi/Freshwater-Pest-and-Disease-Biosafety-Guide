from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import re
from datetime import datetime
from flask_hashing import Hashing
import os
from db import getCursor

app = Flask(__name__)
app.secret_key = b'T1\x8b\xab\xa3:\xb1\xec+\x97.\x8b\xec\xb5(>\xbe\x9a \x89}\xa5\x7f5'
app.config['UPLOAD_FOLDER'] = 'static/images'  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
hashing = Hashing(app)

from user_dashboard import user_bp
from admin_dashboard import admin_bp
from staff_dashboard import staff_bp
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(staff_bp, url_prefix='/staff')


# Function to create an admin account
def admin_account():
    # Setting default values for the admin account
    username = "admin"
    raw_password = "12345"  
    email = "admin@example.com"
    firstname = "Admin"
    lastname = "User"
    phonenumber = "1234567890"
    role = 'Administrator'

    # Generating a hashed password using a predefined salt
    salt ='S1#e2!r3@t4$'
    hashed_password = hashing.hash_value(raw_password, salt=salt)
    print(hashed_password)

    # Establishing database connection and inserting the admin account details into the database
    cursor = getCursor()
    cursor.execute('INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (username, hashed_password, email, firstname, lastname, phonenumber, role))
    cursor.close()

# Route definition for the admin dashboard page
@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if the user is logged in and has an administrator role
    if 'loggedin' in session and session['role'] == 'Administrator':
        # Retrieve all administrator accounts from the database
        cursor = getCursor()
        cursor.execute('SELECT * FROM secureaccount WHERE role = %s', ('Administrator',))
        admin_members = cursor.fetchall()
        # Render the admin dashboard template with the retrieved data
        return render_template('admin_layout.html', staff_members=admin_members)
    else:
        # Redirect the user to the login page if they are not logged in or not an administrator
        return redirect(url_for('login'))

# Function to create a staff account
def create_staff_account(username, raw_password, email, firstname, lastname, phonenumber, role):
    # Generate a hashed password for the new account
    salt = 'S1#e2!r3@t4$' 
    hashed_password = hashing.hash_value(raw_password, salt=salt)  
    
    # Insert the new staff account details into the database
    cursor = getCursor()  
    cursor.execute(
        'INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (username, hashed_password, email, firstname, lastname, phonenumber, role)
    )
    
# Functions to create specific staff accounts
def create_alice_account():
    create_staff_account(
        'alice.green',
        '12345',
        'alice.green@example.com',
        'Alice',
        'Green',
        '555-6789',
        'Staff'
    )

def create_bob_account():
    create_staff_account(
        'bob.white',
        '12345',
        'bob.white@example.com',
        'Bob',
        'White',
        '555-9876',
        'Staff'
    )

def create_charlie_account():
    create_staff_account(
        'charlie.brown',
        '12345',
        'charlie.brown@example.com',
        'Charlie',
        'Brown',
        '555-1234',
        'Staff'
    )

# Route definition for the staff dashboard page
@app.route('/staff/dashboard')
def staff_dashboard():
    # Check if the user is logged in and has a staff role
    if 'loggedin' in session and session['role'] == 'Staff':
        # Retrieve all staff accounts from the database
        cursor = getCursor()
        cursor.execute('SELECT * FROM secureaccount WHERE role = %s', ('Staff',))
        admin_members = cursor.fetchall()
        # Render the staff dashboard template with the retrieved data
        return render_template('staff_layout.html', staff_members=admin_members)
    else:
        # Redirect the user to the login page if they are not logged in or not a staff member
        return redirect(url_for('login'))

# Route definition for the login page, supporting both GET and POST requests
@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''  # Message to display on the login page
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']
        # Retrieve the account details from the database
        cursor = getCursor()
        cursor.execute('SELECT * FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            # Check if the entered password matches the one stored in the database
            user_id, username, password, email, role = account[0], account[1], account[2], account[3], account[8]  
            if hashing.check_value(password, user_password, salt='S1#e2!r3@t4$'):
                # Set session variables and redirect the user to the appropriate dashboard
                session['loggedin'] = True
                session['id'] = user_id
                session['username'] = username
                session['password'] = password
                session['role'] = role  
                session['email'] = email
                

                if role == 'Administrator':
                    return redirect(url_for('admin_dashboard'))
                elif role == 'Staff':
                    return redirect(url_for('staff_dashboard'))
                else:
                    return redirect(url_for('user_dashboard.home'))
            else:
                msg = 'Incorrect password!'
        else:
            msg = 'Incorrect username!'
    # Render the login page with any message (if applicable)
    return render_template('index.html', msg=msg)

# Route definition for the registration page, supporting both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''  # Message to display on the registration page
    if request.method == 'POST' and all(key in request.form for key in ['username', 'password', 'email', 'firstname', 'lastname', 'phonenumber']):
        # Retrieve the form data
        username = request.form['username']
        password = request.form['password']  
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phonenumber = request.form['phonenumber']
        date_joined = datetime.today().strftime('%Y-%m-%d')  
        status = 'Active'  

        # Validate the submitted data and create the new account
        cursor = getCursor()
        cursor.execute('SELECT * FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        elif len(password) < 8 or not re.search("[a-zA-Z]", password) or not re.search("[0-9]", password):
            msg = 'Password must be at least 8 characters long and include a mix of letters and numbers!'
        else:
            # Insert the new user into the database
            hashed_password = hashing.hash_value(password, salt='S1#e2!r3@t4$')  
            cursor.execute('INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                           (username, hashed_password, email, firstname, lastname, phonenumber, 'River User'))
            secureaccount_id = cursor.lastrowid  
            cursor.execute('INSERT INTO RiverUsers (Username, FirstName, LastName, Address, Email, PhoneNumber, DateJoined, Status, secureaccount_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (username, firstname, lastname, '', email, phonenumber, date_joined, status, secureaccount_id))
            msg = 'You have successfully registered!'
    # Render the registration page with any message (if applicable)
    return render_template('register.html', msg=msg)

# Route definition for the logout page
@app.route('/logout')
def logout():
    # Remove session data to log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Main function to run the Flask app
if __name__ == '__main__':
    app.run()
