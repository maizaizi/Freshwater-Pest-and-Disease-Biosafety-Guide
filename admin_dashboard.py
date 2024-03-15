from flask import render_template, redirect, url_for, request, Flask, flash
from db import getCursor
from flask import Blueprint
from flask import session
from flask_hashing import Hashing
from datetime import datetime
from flask import current_app
import os
import uuid
from werkzeug.utils import secure_filename
app = Flask(__name__)
hashing = Hashing(app)

admin_bp = Blueprint('admin_dashboard', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'loggedin' in session:
        # If logged in, render the admin dashboard template
        return render_template('admin_dashboard.html', username=session['username'])
    # If not logged in, redirect to the login page
    return redirect(url_for('login'))


@admin_bp.route('/profile', methods=['GET'])
def admin_profile():
    # Retrieve database cursor
    cursor = getCursor()
    # Execute query to fetch admin details (here hardcoded to fetch the first admin for demonstration)
    cursor.execute("SELECT * FROM Administrator WHERE AdminNumber = %s", (1,))
    admin_info_row = cursor.fetchone()
    # If admin information is found, prepare it for the template
    if admin_info_row:
        admin_info = {
            'first_name': admin_info_row[1],
            'last_name': admin_info_row[2],
            'email': admin_info_row[3],
            'work_phone': admin_info_row[4],
            'hire_date': admin_info_row[5],
            'position': admin_info_row[6],
            'department': admin_info_row[7],
            'status': admin_info_row[8]
        }
    else:
        # If no admin information is found, pass an empty dictionary
        admin_info = {}
    # Render the admin profile template with the fetched admin information
    return render_template('admin_profile.html', admin_info=admin_info)


@admin_bp.route('/update_admin_profile', methods=['POST'])
def update_admin_profile():
    # Retrieve form data submitted for profile update
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    work_phone = request.form.get('work_phone')
    hire_date = request.form.get('hire_date')
    position = request.form.get('position')
    department = request.form.get('department')
    status = request.form.get('status')

    # Retrieve database cursor
    cursor = getCursor()
    # Update admin details in the database; here hardcoded to update the first admin for demonstration
    cursor.execute("""
        UPDATE Administrator SET 
        FirstName = %s, LastName = %s, Email = %s, 
        WorkPhoneNumber = %s, HireDate = %s, 
        Position = %s, Department = %s, Status = %s
        WHERE AdminNumber = %s
    """, (first_name, last_name, email, work_phone, hire_date, position, department, status, 1))

    # Redirect back to the admin profile page after updating
    return redirect(url_for('admin_dashboard.admin_profile'))



@admin_bp.route('/admin/change_password', methods=['GET', 'POST'])
def admin_change_password():
    # Check if user is logged in
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Handle form submission
    if request.method == 'POST':
        # Collect form data for password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
    
        # Ensure the new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('admin_dashboard.admin_change_password'))

        # Retrieve the current logged-in username
        username = session.get('username')

        # Retrieve the current hashed password from database
        cursor = getCursor()
        cursor.execute('SELECT password FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()

        # Check if the account exists and the current password is correct
        if account:
            hashed_current_password = account[0]
            if hashing.check_value(hashed_current_password, current_password, salt='S1#e2!r3@t4$'):
                # Hash the new password and update it in the database
                hashed_new_password = hashing.hash_value(new_password, salt='S1#e2!r3@t4$')
                cursor.execute('UPDATE secureaccount SET password = %s WHERE username = %s', (hashed_new_password, username,))
                flash('Your password has been updated successfully.')
                return redirect(url_for('admin_dashboard')) 
            else:
                flash('Incorrect current password.')
                return redirect(url_for('admin_dashboard.admin_change_password'))
        else:
            flash('User not found.')
            return redirect(url_for('admin_dashboard.admin_change_password'))
   
    # Render the password change template
    return render_template('admin_change_password.html')


@admin_bp.route('/manage_user', methods=['GET'])
def manage_user():
    # Check if user is logged in and is an administrator
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    # Retrieve all river user accounts
    cursor = getCursor()
    cursor.execute("SELECT * FROM RiverUsers")
    river_users_info = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Render the manage user template with the river users information
    return render_template('admin_manage_user.html', river_users_info=river_users_info)


@admin_bp.route('/add_river_user', methods=['GET', 'POST'])
def add_river_user():
    # Check if user is logged in and is an administrator
    if 'loggedin' not in session or session['role'] != 'Administrator':
        flash('You must be an admin to access this page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Ensure all required form fields are present
        required_fields = ['username', 'firstname', 'lastname', 'address', 'email', 'password', 'phonenumber']
        if not all(field in request.form for field in required_fields):
            flash('Missing required fields.', 'error')
            return redirect(url_for('admin_dashboard.add_river_user'))

        # Collect form data to add a new river user
        username = request.form['username']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['address']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phonenumber']
        status = request.form.get('status', 'Active')
        date_joined = datetime.today().strftime('%Y-%m-%d')
        role = 'River User'
        salt = 'S1#e2!r3@t4$'

        # Hash the password and insert the new user into the database
        hashed_password = hashing.hash_value(password, salt=salt)
        cursor = getCursor()
        try:
            # Insert new user into the 'secureaccount' and 'RiverUsers' tables
            cursor.execute("INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (username, hashed_password, email, first_name, last_name, phone_number, role))
            new_account_id = cursor.lastrowid
            cursor.execute("INSERT INTO RiverUsers (Username, FirstName, LastName, Address, Email, PhoneNumber, DateJoined, Status, secureaccount_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (username, first_name, last_name, address, email, phone_number, date_joined, status, new_account_id))
            flash('User added successfully!')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('admin_dashboard.add_river_user'))

        # Redirect to the manage user page after successful addition
        return redirect(url_for('admin_dashboard.manage_user'))

    # Render the add river user template
    return render_template('admin_add_river_user.html')


@admin_bp.route('/edit_river_user/<string:username>', methods=['GET', 'POST'])
def edit_river_user(username):
    # Retrieve database cursor
    cursor = getCursor()
    if request.method == 'POST':
        # Collect form data submitted for river user update
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phonenumber']
        date_joined = request.form['date_joined']
        status = request.form['status']

        # Update river user details in the database
        cursor.execute("""
            UPDATE RiverUsers SET
            FirstName = %s,
            LastName = %s,
            Address = %s,
            Email = %s,
            PhoneNumber = %s,
            DateJoined = %s,
            Status = %s
            WHERE Username = %s
        """, (first_name, last_name, address, email, phone_number, date_joined, status, username))

        # Update associated secureaccount details
        cursor.execute("""
            UPDATE secureaccount SET
            email = %s,
            firstname = %s,
            lastname = %s,
            phonenumber = %s
            WHERE username = %s
        """, (email, first_name, last_name, phone_number, username))

        # Notify user of successful update
        flash('User updated successfully!')
        return redirect(url_for('admin_dashboard.manage_user'))
    else:
        # Retrieve the existing user details to populate the form for editing
        cursor.execute("SELECT * FROM RiverUsers WHERE Username = %s", (username,))
        user_row = cursor.fetchone()
        if user_row:
            # Prepare the user details for rendering
            user = {
                'username': user_row[1], 
                'first_name': user_row[2],
                'last_name': user_row[3],
                'address': user_row[4],
                'email': user_row[5],
                'phone_number': user_row[6],
                'date_joined': user_row[7],
                'status': user_row[8]
            }
            return render_template('admin_edit_river_user.html', user=user)
        else:
            # Notify admin if the user is not found
            flash('User not found!')
            return redirect(url_for('admin_dashboard.manage_user'))


@admin_bp.route('/delete_river_user/<string:username>', methods=['POST'])
def delete_river_user(username):
    # Retrieve database cursor
    cursor = getCursor()
    # Get the secureaccount_id associated with the user
    cursor.execute("SELECT secureaccount_id FROM RiverUsers WHERE Username = %s", (username,))
    result = cursor.fetchone()

    if result:
        # If user exists, delete their records from RiverUsers and secureaccount
        secureaccount_id = result[0]
        cursor.execute("DELETE FROM RiverUsers WHERE Username = %s", (username,))
        cursor.execute("DELETE FROM secureaccount WHERE id = %s", (secureaccount_id,))

        # Notify admin of successful deletion
        flash('User deleted successfully!')
    else:
        # Notify admin if the user is not found
        flash('User not found!')

    return redirect(url_for('admin_dashboard.manage_user'))


@admin_bp.route('/manage_staff', methods=['GET'])
def manage_staff():
    # Check if user is logged in and is an administrator
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))

    # Retrieve all staff member accounts
    cursor = getCursor()
    cursor.execute("SELECT * FROM Staff")
    staff_members_info = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    
    # Render the manage staff template with the staff members information
    return render_template('admin_manage_staff.html', staff_members_info=staff_members_info)


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    # Check if user is logged in and is an administrator
    if 'loggedin' not in session or session['role'] != 'Administrator':
        flash('You must be an admin to access this page.')
        return redirect(url_for('login'))

    # Check if the form submission is POST (form has been submitted)
    if request.method == 'POST':
        # List of required fields in the form
        required_fields = ['username', 'firstname', 'lastname', 'email', 'password', 'workphonenumber', 'hiredate', 'position', 'department', 'status']
        # Check if all required fields are in the submitted form
        if not all(field in request.form for field in required_fields):
            flash('Missing required fields.', 'error')
            return redirect(url_for('admin_dashboard.add_staff'))

        # Retrieve the data from form
        username = request.form['username']
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        work_phone_number = request.form['workphonenumber']
        hire_date = request.form['hiredate']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']
        role = 'Staff'  # Set the role for new user
        salt = 'S1#e2!r3@t4$'  # Salt for hashing the password

        # Hash the password with the salt
        hashed_password = hashing.hash_value(password, salt=salt)
        # Get the database cursor
        cursor = getCursor()

        new_account_id = None  # Initialize new_account_id; will be used later
        try:
            # Insert new user into secureaccount table
            cursor.execute("INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (username, hashed_password, email, first_name, last_name, work_phone_number, role))

            # Insert new staff member into Staff table
            cursor.execute("INSERT INTO Staff (username, StaffNumber, FirstName, LastName, Email, WorkPhoneNumber, HireDate, Position, Department, Status, secureaccount_id) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (username, first_name, last_name, email, work_phone_number, hire_date, position, department, status, new_account_id))

            flash('Staff member added successfully!')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('admin_dashboard.add_staff'))

        return redirect(url_for('admin_dashboard.manage_staff'))

    # Render add staff template if method is not POST
    return render_template('admin_add_staff.html')

@admin_bp.route('/edit_staff/<string:username>', methods=['GET', 'POST'])
def edit_staff(username):
    # Get the database cursor
    cursor = getCursor()

    # Check if the form submission is POST (form has been submitted)
    if request.method == 'POST':
        # Retrieve the updated data from the form
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        work_phone_number = request.form['workphonenumber']
        hire_date = request.form['hiredate']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']

        # Update the Staff table with new data
        cursor.execute("""
            UPDATE Staff SET
            FirstName = %s,
            LastName = %s,
            Email = %s,
            WorkPhoneNumber = %s,
            HireDate = %s,
            Position = %s,
            Department = %s,
            Status = %s
            WHERE username = %s
        """, (first_name, last_name, email, work_phone_number, hire_date, position, department, status, username))

        # Update the secureaccount table with new data
        cursor.execute("""
            UPDATE secureaccount SET
            email = %s,
            firstname = %s,
            lastname = %s,
            phonenumber = %s
            WHERE username = (SELECT username FROM Staff WHERE username = %s)
        """, (email, first_name, last_name, work_phone_number, username))

        flash('Staff member updated successfully!')
        return redirect(url_for('admin_dashboard.manage_staff'))
    else:
        # Fetch the existing staff member's details
        cursor.execute("SELECT * FROM Staff WHERE username = %s", (username,))
        staff_row = cursor.fetchone()
        if staff_row:
            # Prepare the staff member details to be displayed in the form
            staff_member = {
                'username': staff_row[0], 
                'first_name': staff_row[2],
                'last_name': staff_row[3],
                'email': staff_row[4],
                'work_phone_number': staff_row[5],
                'hire_date': staff_row[6],
                'position': staff_row[7],
                'department': staff_row[8],
                'status': staff_row[9]
            }
            return render_template('admin_edit_staff.html', staff_member=staff_member)
        else:
            # Handle case where no staff member found with the provided username
            flash('Staff member not found!')
            return redirect(url_for('admin_dashboard.manage_staff'))

@admin_bp.route('/delete_staff/<string:username>', methods=['POST'])
def delete_staff(username):
    # Get the database cursor
    cursor = getCursor()
    # Select the secureaccount_id linked to the staff member
    cursor.execute("SELECT secureaccount_id FROM Staff WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        secureaccount_id = result[0]
        # Delete the staff member from Staff table
        cursor.execute("DELETE FROM Staff WHERE username = %s", (username,))
        # Delete the associated secureaccount
        cursor.execute("DELETE FROM secureaccount WHERE id = %s", (secureaccount_id,))
        flash('Staff member deleted successfully!')
    else:
        flash('Staff member not found!')

    return redirect(url_for('admin_dashboard.manage_staff'))


def allowed_file(filename):
    # Check if the file has an extension and if it is allowed
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@admin_bp.route('/manage_guide', methods=['GET', 'POST'])
def manage_guide():
    # Restrict access to logged-in administrators
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    # Retrieve and display all guides from the database ordered by FreshwaterID
    cursor = getCursor()
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE ORDER BY FreshwaterID DESC')
    rows = cursor.fetchall()
    guides = [dict(zip(cursor.column_names, row)) for row in rows]  # Convert fetched rows to list of dictionaries
    return render_template('admin_manage_guide.html', guides=guides)

@admin_bp.route('/add_guide', methods=['GET', 'POST'])
def add_guide():
    # Restrict access to logged-in administrators
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Retrieve guide details from form
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')

        image_filename = None
        # Process the main guide image if provided
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                # Generate a secure filename for the uploaded image
                image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                # Save the image to the configured upload folder
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                cursor = getCursor()
                # Insert the main image filename into UploadedImages table
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (image_filename,))
                
        # Insert new guide information into the database
        insert_sql = """
        INSERT INTO FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        (ItemType, PresentInNZ, CommonName, ScientificName, KeyCharacteristics, BiologyDescription, Impacts, ImageFilename) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, image_filename))

        # Retrieve the ID of the newly added guide
        new_guide_id = cursor.lastrowid

        # Handle the upload and storage of additional guide images if provided
        additional_images = request.files.getlist('additional_images')
        for additional_image in additional_images:
            if additional_image.filename != '' and allowed_file(additional_image.filename):
                additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                additional_image.save(additional_image_path)

                # Insert filename of additional image into UploadedImages table
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                # Link additional image to the guide in GuideAdditionalImages table
                cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (new_guide_id, additional_image_filename,))
        
        # Close database cursor and show success message
        cursor.close()
        flash('Guide item added successfully!')
        return redirect(url_for('admin_dashboard.manage_guide'))

    # Render the page for adding a new guide
    return render_template('admin_add_guide.html')



@admin_bp.route('/edit_guide/<int:item_id>', methods=['GET', 'POST'])
def edit_guide(item_id):
    # Ensure the user is logged in and is an administrator
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()  # Obtain the database cursor
    if request.method == 'POST':
        # Extract updated guide details from the submitted form
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')
        filename = None

        # Process the main image if provided
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                # Generate a unique and secure filename, then save the image
                filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                # Insert the new image filename into the database
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (filename,))
        else:
            # If no new main image is provided, keep the current one
            cursor.execute("SELECT ImageFilename FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
            filename_data = cursor.fetchone()
            if filename_data:
                filename = filename_data['ImageFilename']

        # Update the guide details in the database
        update_sql = """
        UPDATE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        SET ItemType = %s, PresentInNZ = %s, CommonName = %s, ScientificName = %s, KeyCharacteristics = %s, BiologyDescription = %s, Impacts = %s, ImageFilename = %s 
        WHERE FreshwaterID = %s
        """
        cursor.execute(update_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, filename, item_id))

        # Process additional images if provided
        additional_images = request.files.getlist('additional_images')
        for additional_image in additional_images:
            if additional_image.filename != '' and allowed_file(additional_image.filename):
                # For each additional image, generate a secure filename, save it, and update the database
                additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                additional_image.save(additional_image_path)
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (item_id, additional_image_filename))

        # Close the database cursor and provide feedback to the user
        cursor.close()
        flash('Guide item updated successfully!')
        return redirect(url_for('admin_dashboard.manage_guide'))
    else:
        # If not a POST request, load the current guide details to be edited
        cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
        row = cursor.fetchone()
        if row:
            # Prepare the guide data to be displayed in the edit form
            item = dict(zip([column[0] for column in cursor.description], row))
            cursor.execute("SELECT AdditionalFilename FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
            additional_filenames_data = cursor.fetchall()
            item['additional_images'] = [row[0] for row in additional_filenames_data]
        else:
            # If no guide found with the provided ID, inform the user and redirect
            flash('Guide item not found!')
            return redirect(url_for('admin_dashboard.manage_guide'))

        return render_template('admin_edit_guide.html', item=item)

@admin_bp.route('/delete_guide/<int:item_id>', methods=['POST'])
def delete_guide(item_id):
    # Check if user is logged in and has administrator privileges
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()
    try:
        # Attempt to delete additional images and the guide from the database
        cursor.execute("DELETE FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
        cursor.execute("DELETE FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
        flash('Guide item and associated additional images deleted successfully!')
    except Exception as e:
        # If an error occurs, roll back the transaction and inform the user
        cursor.connection.rollback()
        print("Error occurred: ", e)
        flash('Error deleting guide item.')
    finally:
        # Ensure the database cursor is closed
        cursor.close()

    return redirect(url_for('admin_dashboard.manage_guide'))
