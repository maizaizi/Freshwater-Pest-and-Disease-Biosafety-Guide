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

@admin_bp.route('/profile', methods=['GET'])
def admin_profile():

    cursor = getCursor()
    cursor.execute("SELECT * FROM Administrator WHERE AdminNumber = %s", (1,))  
    admin_info_row = cursor.fetchone()
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
        admin_info = {}
    return render_template('admin_profile.html', admin_info=admin_info)



@admin_bp.route('/update_admin_profile', methods=['POST'])
def update_admin_profile():
   
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    work_phone = request.form.get('work_phone')
    hire_date = request.form.get('hire_date')
    position = request.form.get('position')
    department = request.form.get('department')
    status = request.form.get('status')

   
    cursor = getCursor()
    cursor.execute("""
        UPDATE Administrator SET 
        FirstName = %s, LastName = %s, Email = %s, 
        WorkPhoneNumber = %s, HireDate = %s, 
        Position = %s, Department = %s, Status = %s
        WHERE AdminNumber = %s
    """, (first_name, last_name, email, work_phone, hire_date, position, department, status, 1))

    return redirect(url_for('admin_dashboard.admin_profile'))


@admin_bp.route('/admin/change_password', methods=['GET', 'POST'])
def admin_change_password():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        print("Current Password:", current_password)
        print("New Password:", new_password)
        print("Confirm Password:", confirm_password)
    
        if new_password != confirm_password:
            print("Before flash()")
            flash("New passwords do not match.")
            return redirect(url_for('admin_dashboard.admin_change_password'))

        
        username = session.get('username')
        print("Session Username:", username)

        cursor = getCursor()
        cursor.execute('SELECT password FROM secureaccount WHERE username = %s', (username,))
        account = cursor.fetchone()
        print("Database Username:", account)

        if account:
            hashed_current_password = account[0]
           
            print("Hashed Current Password:", hashed_current_password)
            print("Hashed New Password:", hashing.hash_value(new_password, salt='S1#e2!r3@t4$'))

            if hashing.check_value(hashed_current_password, current_password, salt='S1#e2!r3@t4$'):
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
   
    return render_template('admin_change_password.html')


@admin_bp.route('/manage_user', methods=['GET'])
def manage_user():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()
    cursor.execute("SELECT * FROM RiverUsers")
    river_users_info = []
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
    
    return render_template('admin_manage_user.html', river_users_info=river_users_info)


@admin_bp.route('/add_river_user', methods=['GET', 'POST'])
def add_river_user():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        flash('You must be an admin to access this page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        required_fields = ['username', 'firstname', 'lastname', 'address', 'email', 'password', 'phonenumber']
        if not all(field in request.form for field in required_fields):
            flash('Missing required fields.', 'error')
            return redirect(url_for('admin_dashboard.add_river_user'))

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

        hashed_password = hashing.hash_value(password, salt=salt)  
        cursor = getCursor()

        try:
     
            cursor.execute("INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (username, hashed_password, email, first_name, last_name, phone_number, role))

 
            new_account_id = cursor.lastrowid

  
            cursor.execute("INSERT INTO RiverUsers (Username, FirstName, LastName, Address, Email, PhoneNumber, DateJoined, Status, secureaccount_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (username, first_name, last_name, address, email, phone_number, date_joined, status, new_account_id))

            flash('User added successfully!')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('admin_dashboard.add_river_user'))

        return redirect(url_for('admin_dashboard.manage_user'))

    return render_template('admin_add_river_user.html')

@admin_bp.route('/edit_river_user/<string:username>', methods=['GET', 'POST'])
def edit_river_user(username):
    cursor = getCursor()
    if request.method == 'POST':
  
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phonenumber']
        date_joined = request.form['date_joined']
        status = request.form['status']

        
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


        cursor.execute("""
            UPDATE secureaccount SET
            email = %s,
            firstname = %s,
            lastname = %s,
            phonenumber = %s
            WHERE username = %s
        """, (email, first_name, last_name, phone_number, username))

        flash('User updated successfully!')
        return redirect(url_for('admin_dashboard.manage_user'))
    else:
       
        cursor.execute("SELECT * FROM RiverUsers WHERE Username = %s", (username,))
        user_row = cursor.fetchone()
        if user_row:
   
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

            flash('User not found!')
            return redirect(url_for('admin_dashboard.manage_user'))



@admin_bp.route('/delete_river_user/<string:username>', methods=['POST'])
def delete_river_user(username):
    cursor = getCursor()
    cursor.execute("SELECT secureaccount_id FROM RiverUsers WHERE Username = %s", (username,))
    result = cursor.fetchone()

    if result:
        secureaccount_id = result[0]
        cursor.execute("DELETE FROM RiverUsers WHERE Username = %s", (username,))
        cursor.execute("DELETE FROM secureaccount WHERE id = %s", (secureaccount_id,))

        flash('User deleted successfully!')
    else:
        flash('User not found!')

    return redirect(url_for('admin_dashboard.manage_user'))


@admin_bp.route('/manage_staff', methods=['GET'])
def manage_staff():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))

    cursor = getCursor()
    cursor.execute("SELECT * FROM Staff")
    staff_members_info = []
    for row in cursor.fetchall():
        staff_info = {
            'username': row[0], 
            'staff_id': row[1],   
            'first_name': row[2],
            'last_name': row[3],
            'email': row[4],
            'work_phone_number': row[5],
            'hire_date': row[6],
            'position': row[7],
            'department': row[8],
            'status': row[9]
        }
        staff_members_info.append(staff_info)

    return render_template('admin_manage_staff.html', staff_members_info=staff_members_info)


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        flash('You must be an admin to access this page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        required_fields = ['username', 'firstname', 'lastname', 'email', 'password', 'workphonenumber', 'hiredate', 'position', 'department', 'status']
        if not all(field in request.form for field in required_fields):
            flash('Missing required fields.', 'error')
            return redirect(url_for('admin_dashboard.add_staff'))

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
        role = 'Staff'
        salt = 'S1#e2!r3@t4$'

        hashed_password = hashing.hash_value(password, salt=salt)
        cursor = getCursor()
       
        new_account_id = None
        try:
            cursor.execute("INSERT INTO secureaccount (username, password, email, firstname, lastname, phonenumber, role) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (username, hashed_password, email, first_name, last_name, work_phone_number, role))

    

            cursor.execute("INSERT INTO Staff (username, StaffNumber, FirstName, LastName, Email, WorkPhoneNumber, HireDate, Position, Department, Status, secureaccount_id) VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (username, first_name, last_name, email, work_phone_number, hire_date, position, department, status, new_account_id))

            flash('Staff member added successfully!')
        except Exception as e:
            flash(f'An error occurred: {e}', 'error')
            return redirect(url_for('admin_dashboard.add_staff'))

        return redirect(url_for('admin_dashboard.manage_staff'))

    return render_template('admin_add_staff.html')


@admin_bp.route('/edit_staff/<string:username>', methods=['GET', 'POST'])
def edit_staff(username):
    cursor = getCursor()
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        email = request.form['email']
        work_phone_number = request.form['workphonenumber']
        hire_date = request.form['hiredate']
        position = request.form['position']
        department = request.form['department']
        status = request.form['status']

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
        cursor.execute("SELECT * FROM Staff WHERE username = %s", (username,))
        staff_row = cursor.fetchone()
        if staff_row:

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

            flash('Staff member not found!')
            return redirect(url_for('admin_dashboard.manage_staff'))

@admin_bp.route('/delete_staff/<string:username>', methods=['POST'])
def delete_staff(username):
    cursor = getCursor()
    cursor.execute("SELECT secureaccount_id FROM Staff WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        
        secureaccount_id = result[0]
        cursor.execute("DELETE FROM Staff WHERE username = %s", (username,))
        cursor.execute("DELETE FROM secureaccount WHERE id = %s", (secureaccount_id,))
        flash('Staff member deleted successfully!')
    else:
        flash('Staff member not found!')

    return redirect(url_for('admin_dashboard.manage_staff'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@admin_bp.route('/manage_guide', methods=['GET', 'POST'])
def manage_guide():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE ORDER BY FreshwaterID DESC')
    rows = cursor.fetchall()
    guides = [dict(zip(cursor.column_names, row)) for row in rows]  
    return render_template('admin_manage_guide.html', guides=guides)



@admin_bp.route('/add_guide', methods=['GET', 'POST'])
def add_guide():
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')

        image_filename = None
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                cursor = getCursor()
                # Store the primary image file name in the UploadedImages table
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (image_filename,))
                
        # Insert the guide details into the FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE table
        insert_sql = """
        INSERT INTO FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        (ItemType, PresentInNZ, CommonName, ScientificName, KeyCharacteristics, BiologyDescription, Impacts, ImageFilename) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, image_filename))
        new_guide_id = cursor.lastrowid

        # Handle additional images
        additional_images = request.files.getlist('additional_images')
        for additional_image in additional_images:
            if additional_image.filename != '' and allowed_file(additional_image.filename):
                additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                additional_image.save(additional_image_path)

                # Store the additional image file name in the UploadedImages table
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                # Store the additional image relation to guide in the GuideAdditionalImages table
                cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (new_guide_id, additional_image_filename,))
        
        cursor.close()
        flash('Guide item added successfully!')
        return redirect(url_for('admin_dashboard.manage_guide'))

    return render_template('admin_add_guide.html')


@admin_bp.route('/edit_guide/<int:item_id>', methods=['GET', 'POST'])
def edit_guide(item_id):
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()
    if request.method == 'POST':
        item_type = request.form['ItemType']
        present_in_nz = request.form['PresentInNZ']
        common_name = request.form['CommonName']
        scientific_name = request.form.get('ScientificName', '')
        key_characteristics = request.form.get('KeyCharacteristics', '')
        biology_description = request.form.get('BiologyDescription', '')
        impacts = request.form.get('Impacts', '')
        filename = None

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(image.filename)[1])
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                # Store the new primary image file name in the UploadedImages table
                cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (filename,))
        else:
            cursor.execute("SELECT ImageFilename FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
            filename_data = cursor.fetchone()
            if filename_data:
                filename = filename_data['ImageFilename']

        # Update the guide details in the FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE table
        update_sql = """
        UPDATE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        SET ItemType = %s, PresentInNZ = %s, CommonName = %s, ScientificName = %s, KeyCharacteristics = %s, BiologyDescription = %s, Impacts = %s, ImageFilename = %s 
        WHERE FreshwaterID = %s
        """
        cursor.execute(update_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, filename, item_id))

        # Handle additional images
        additional_images = request.files.getlist('additional_images')
        if additional_images:
            # First, you might want to clear existing additional images if needed
            # cursor.execute("DELETE FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
            for additional_image in additional_images:
                if additional_image.filename != '' and allowed_file(additional_image.filename):
                    additional_image_filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(additional_image.filename)[1])
                    additional_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], additional_image_filename)
                    additional_image.save(additional_image_path)
                    # Store the new additional image file names in the UploadedImages table and link them with the guide
                    cursor.execute("INSERT INTO UploadedImages (ImageFilename) VALUES (%s)", (additional_image_filename,))
                    cursor.execute("INSERT INTO GuideAdditionalImages (GuideID, AdditionalFilename) VALUES (%s, %s)", (item_id, additional_image_filename))

        cursor.close()
        flash('Guide item updated successfully!')
        return redirect(url_for('admin_dashboard.manage_guide'))
    else:
        cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
        row = cursor.fetchone()
        if row:
            item = dict(zip([column[0] for column in cursor.description], row))
            # Load additional images for the guide
            cursor.execute("SELECT AdditionalFilename FROM GuideAdditionalImages WHERE GuideID = %s", (item_id,))
            item['additional_images'] = [row[2] for row in cursor.fetchall() if len(row) > 2]
        else:
            flash('Guide item not found!')
            return redirect(url_for('admin_dashboard.manage_guide'))

        return render_template('admin_edit_guide.html', item=item)


@admin_bp.route('/delete_guide/<int:item_id>', methods=['POST'])
def delete_guide(item_id):
    if 'loggedin' not in session or session['role'] != 'Administrator':
        return redirect(url_for('login'))
    
    cursor = getCursor()
    try:

        delete_additional_images_sql = "DELETE FROM GuideAdditionalImages WHERE GuideID = %s"
        cursor.execute(delete_additional_images_sql, (item_id,))
        delete_guide_sql = "DELETE FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s"
        cursor.execute(delete_guide_sql, (item_id,))

        flash('Guide item and associated additional images deleted successfully!')
    except Exception as e:
       
        cursor.connection.rollback()
        print("Error occurred: ", e)
        flash('Error deleting guide item.')
    finally:

        cursor.close()

    return redirect(url_for('admin_dashboard.manage_guide'))
