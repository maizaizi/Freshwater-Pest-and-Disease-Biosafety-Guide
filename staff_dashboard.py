from flask import render_template, redirect, url_for, request, Flask, flash, session, Blueprint
from db import getCursor
from flask_hashing import Hashing
from flask import current_app
from werkzeug.utils import secure_filename
import os
import uuid


app = Flask(__name__)
hashing = Hashing(app)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
staff_bp = Blueprint ('staff_dashboard', __name__, template_folder='templates')
from flask import render_template


@staff_bp.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'loggedin' in session:
        # If logged in, render the staff dashboard template
        return render_template('staff_dashboard.html', username=session['username'])
    # If not logged in, redirect to the login page
    return redirect(url_for('login'))

@staff_bp.route('/profile', methods=['GET'])
def staff_profile():
    # Get the username from the session
    username = session.get('username')
    # Redirect to login page if no user is logged in
    if username is None:
        return redirect(url_for('login'))
    
    # Get database cursor and retrieve staff information
    cursor = getCursor()
    cursor.execute("SELECT * FROM Staff WHERE username = %s",  (username,))
    staff_info_row = cursor.fetchone()
    # If staff information exists, prepare it to be passed to the template
    if staff_info_row:
        staff_info = {
            'staff_number': staff_info_row[1],
            'first_name': staff_info_row[2],
            'last_name': staff_info_row[3],
            'email': staff_info_row[4],
            'work_phone': staff_info_row[5],
            'hire_date': staff_info_row[6],
            'position': staff_info_row[7],
            'department': staff_info_row[8],
            'status': staff_info_row[9]
        }
    else:
        # If no staff information, pass an empty dictionary
        staff_info = {}
    # Render the staff profile template with staff information
    return render_template('staff_profile.html', staff_info=staff_info)


@staff_bp.route('/update_staff_profile', methods=['POST'])
def update_staff_profile():
    # Retrieve form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    work_phone = request.form.get('work_phone')
    hire_date = request.form.get('hire_date')
    position = request.form.get('position')
    department = request.form.get('department')
    status = request.form.get('status')
    
    # Check if user is logged in
    username= session.get('username')
    if username is None:
        return redirect(url_for('login'))
     
    # Get database cursor and update staff information
    cursor = getCursor()
    cursor.execute("""
        UPDATE Staff SET 
        FirstName = %s, LastName = %s, Email = %s, 
        WorkPhoneNumber = %s, HireDate = %s, 
        Position = %s, Department = %s, Status = %s
        WHERE username = %s
    """, (first_name, last_name, email, work_phone, hire_date, position, department, status, username))  

    # Redirect to the staff profile page after updating
    return redirect(url_for('staff_dashboard.staff_profile'))


@staff_bp.route('/staff/change_password', methods=['GET', 'POST'])
def staff_change_password():
    # Check if user is logged in
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Retrieve form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate new passwords match
        if new_password != confirm_password:
            flash("New passwords do not match.")
            return redirect(url_for('staff_dashboard.staff_change_password'))

        # Get the username from the session
        username = session.get('username')

        # Get database cursor and check the current password
        cursor = getCursor()
        cursor.execute('SELECT password FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            hashed_current_password = account[0]

            # Validate current password and update with the new one if correct
            if hashing.check_value(hashed_current_password, current_password, salt='S1#e2!r3@t4$'):
                hashed_new_password = hashing.hash_value(new_password, salt='S1#e2!r3@t4$')
                cursor.execute('UPDATE secureaccount SET password = %s WHERE username = %s', (hashed_new_password, username,))
                flash('Your password has been updated successfully.')
                return redirect(url_for('staff_dashboard')) 
            else:
                flash('Incorrect current password.')
                return redirect(url_for('staff_dashboard.staff_change_password'))
        else:
            flash('User not found.')
            return redirect(url_for('staff_dashboard.staff_change_password'))
   
    # Render the change password template
    return render_template('staff_change_password.html')

@staff_bp.route('/river_users', methods=['GET'])
def staff_view_user():
    # Check if user is logged in and has the role of Staff
    if 'loggedin' not in session or session['role'] != 'Staff':
        return redirect(url_for('login'))
    
    # Get database cursor and fetch all river users information
    cursor = getCursor()
    cursor.execute("SELECT * FROM RiverUsers")
    river_users_info = []
    # Format fetched data for rendering
    for row in cursor.fetchall():
        user_info = {
            'user_id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'address': row[4],
            'email': row[5],
            'phone_number': row[6],
            'date_joined': row[7],
            'status': row[8]
        }
        river_users_info.append(user_info)
    
    # Render the template for viewing river users with the fetched data
    return render_template('staff_view_user.html', river_users_info=river_users_info)


# Function to check if the file extension is allowed
def allowed_file(filename):
    # Return true if the file has a period and the extension after the period is in the allowed extensions list
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@staff_bp.route('/manage_guide', methods=['GET', 'POST'])
def manage_guide():
    # Check if user is logged in and has Staff role
    if 'loggedin' not in session or session['role'] != 'Staff':
        return redirect(url_for('login'))
    
    # Retrieve all entries from the guide table ordered by their ID
    cursor = getCursor()
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE ORDER BY FreshwaterID DESC')
    rows = cursor.fetchall()
    # Convert each row into a dictionary using column names
    guides = [dict(zip(cursor.column_names, row)) for row in rows]  
    # Render the manage guide template with the guide entries
    return render_template('staff_manage_guide.html', guides=guides)


@staff_bp.route('/add_guide', methods=['GET', 'POST'])
def add_guide():
    # Check if user is logged in and has Staff role
    if 'loggedin' not in session or session['role'] != 'Staff':
        return redirect(url_for('login'))
    
    # Handle form submission
    if request.method == 'POST':
        # Retrieve form data for the new guide entry
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')

        image_filename = None
        # Check if an image file was uploaded and validate it
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                # Generate a unique filename and save the image
                image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                # Insert the image filename into the database
                cursor = getCursor()
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (image_filename,))
                
        # Insert the new guide entry into the database
        insert_sql = """
        INSERT INTO FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        (ItemType, PresentInNZ, CommonName, ScientificName, KeyCharacteristics, BiologyDescription, Impacts, ImageFilename) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, image_filename))
        new_guide_id = cursor.lastrowid

        # Handle additional image files if provided
        additional_images = request.files.getlist('additional_images')
        for additional_image in additional_images:
            if additional_image.filename != '' and allowed_file(additional_image.filename):
                # Save and store additional images
                additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                additional_image.save(additional_image_path)
                # Associate additional images with the new guide entry in the database
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (new_guide_id, additional_image_filename,))
        
        # Close the cursor and redirect to the manage guide page with a success message
        cursor.close()
        flash('Guide item added successfully!')
        return redirect(url_for('staff_dashboard.manage_guide'))

    # Render the add guide template
    return render_template('staff_add_guide.html')


@staff_bp.route('/edit_guide/<int:item_id>', methods=['GET', 'POST'])
def edit_guide(item_id):
    # Verify if the user is logged in and has the 'Staff' role
    if 'loggedin' not in session or session['role'] != 'Staff':
        return redirect(url_for('login'))
    
    # Retrieve database cursor for operations
    cursor = getCursor()
    if request.method == 'POST':
        # Extract form data submitted for guide update
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')
        filename = None

        # Handle file upload for a primary image
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (filename,))
        else:
            # If no new primary image is uploaded, keep the old one
            cursor.execute("SELECT ImageFilename FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
            filename_data = cursor.fetchone()
            if filename_data:
                filename = filename_data['ImageFilename']

        # Update guide details in the database
        update_sql = """
        UPDATE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        SET ItemType = %s, PresentInNZ = %s, CommonName = %s, ScientificName = %s, KeyCharacteristics = %s, BiologyDescription = %s, Impacts = %s, ImageFilename = %s 
        WHERE FreshwaterID = %s
        """
        cursor.execute(update_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, filename, item_id))

        # Handle additional image files if provided
        additional_images = request.files.getlist('additional_images')
        for additional_image in additional_images:
            if additional_image.filename != '' and allowed_file(additional_image.filename):
                additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                additional_image.save(additional_image_path)
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (item_id, additional_image_filename,))

        # Finalize updates and inform user of success
        cursor.close()
        flash('Guide item updated successfully!')
        return redirect(url_for('staff_dashboard.manage_guide'))
    else:
        # Retrieve the existing guide details to populate the form for editing
        cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
        row = cursor.fetchone()
        if row:
            item = dict(zip([column[0] for column in cursor.description], row))
            cursor.execute("SELECT AdditionalFilename FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
            additional_filenames_data = cursor.fetchall()
            item['additional_images'] = [row[0] for row in additional_filenames_data]
        else:
            flash('Guide item not found!')
            return redirect(url_for('staff_dashboard.manage_guide'))

        return render_template('staff_edit_guide.html', item=item)


@staff_bp.route('/delete_guide/<int:item_id>', methods=['POST'])
def delete_guide(item_id):
    # Check if user is logged in and has 'Staff' role
    if 'loggedin' not in session or session['role'] != 'Staff':
        return redirect(url_for('login'))
    
    # Perform the deletion process
    cursor = getCursor()
    try:
        # Delete any additional images associated with the guide
        delete_additional_images_sql = "DELETE FROM GuideAdditionalImages WHERE GuideID = %s"
        cursor.execute(delete_additional_images_sql, (item_id,))

        # Delete the guide entry itself
        delete_guide_sql = "DELETE FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s"
        cursor.execute(delete_guide_sql, (item_id,))

        # Notify user of successful deletion
        flash('Guide item and associated additional images deleted successfully!')
    except Exception as e:
        # Handle any errors during deletion
        cursor.connection.rollback()
        flash('Error deleting guide item.')
    finally:
        # Close database cursor and redirect to guide management page
        cursor.close()
    return redirect(url_for('staff_dashboard.manage_guide'))
