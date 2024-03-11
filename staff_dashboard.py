from flask import render_template, redirect, url_for, request, Flask, flash, session, Blueprint
from db import getCursor
from flask import Blueprint
from flask import session
from flask_hashing import Hashing
from flask import current_app
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)
hashing = Hashing(app)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
staff_bp = Blueprint ('staff_dashboard', __name__, template_folder='templates')



@staff_bp.route('/profile', methods=['GET'])
def staff_profile():
    
    username = session.get('username')
    if username is None:
        return redirect(url_for('login'))
    
    cursor = getCursor()
    cursor.execute("SELECT * FROM Staff WHERE username = %s",  (username,))
    staff_info_row = cursor.fetchone()
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
        staff_info = {}
    return render_template('staff_profile.html', staff_info=staff_info)

@staff_bp.route('/update_staff_profile', methods=['POST'])
def update_staff_profile():
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    work_phone = request.form.get('work_phone')
    hire_date = request.form.get('hire_date')
    position = request.form.get('position')
    department = request.form.get('department')
    status = request.form.get('status')
    
    username= session.get('username')
    if username is None:
        return redirect(url_for('login'))
     
    cursor = getCursor()
    cursor.execute("""
        UPDATE Staff SET 
        FirstName = %s, LastName = %s, Email = %s, 
        WorkPhoneNumber = %s, HireDate = %s, 
        Position = %s, Department = %s, Status = %s
        WHERE username = %s
    """, (first_name, last_name, email, work_phone, hire_date, position, department, status, (username)))  

    return redirect(url_for('staff_dashboard.staff_profile'))


@staff_bp.route('/staff/change_password', methods=['GET', 'POST'])
def staff_change_password():
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
                return redirect(url_for('staff_dashboard')) 
            else:
                flash('Incorrect current password.')
                return redirect(url_for('staff_dashboard.staff_change_password'))
        else:
            flash('User not found.')
            return redirect(url_for('staff_dashboard.staff_change_password'))
   
    return render_template('staff_change_password.html')


@staff_bp.route('/river_users', methods=['GET'])
def staff_view_user():
    if 'loggedin' not in session or session['role'] != 'Staff':
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
    
    return render_template('staff_view_user.html', river_users_info=river_users_info)




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@staff_bp.route('/manage_guide', methods=['GET', 'POST'])
def manage_guide():
    cursor = getCursor()
    cursor.execute('SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE ORDER BY FreshwaterID DESC')
    rows = cursor.fetchall()
    guides = [dict(zip(cursor.column_names, row)) for row in rows]  
    return render_template('staff_manage_guide.html', guides=guides)


@staff_bp.route('/add_guide', methods=['GET', 'POST'])
def add_guide():
    if request.method == 'POST':
        # 从表单获取数据
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
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)


        cursor = getCursor()

        insert_sql = """
        INSERT INTO FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        (ItemType, PresentInNZ, CommonName, ScientificName, KeyCharacteristics, BiologyDescription, Impacts, ImageFilename) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, filename))
        cursor.close()
        flash('Guide item added successfully!')
        return redirect(url_for('staff_dashboard.manage_guide'))

    return render_template('staff_add_guide.html')



@staff_bp.route('/edit_guide/<int:item_id>', methods=['GET', 'POST'])
def edit_guide(item_id):
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

        # 处理图片上传
        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
        else:
            # 如果没有上传新图片，则保留原图片
            cursor.execute("SELECT ImageFilename FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
            filename = cursor.fetchone()
            if filename:
                filename = filename['ImageFilename']

   
        update_sql = """
        UPDATE FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE 
        SET ItemType = %s, PresentInNZ = %s, CommonName = %s, ScientificName = %s, KeyCharacteristics = %s, BiologyDescription = %s, Impacts = %s, ImageFilename = %s 
        WHERE FreshwaterID = %s
        """
        cursor.execute(update_sql, (item_type, present_in_nz, common_name, scientific_name, key_characteristics, biology_description, impacts, filename, item_id))
        

        flash('Guide item updated successfully!')
        return redirect(url_for('staff_dashboard.manage_guide'))
    else:

        cursor.execute("SELECT * FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s", (item_id,))
        row = cursor.fetchone()
        if row:
            item = dict(zip([column[0] for column in cursor.description], row))
        else:
            flash('Guide item not found!')
            return redirect(url_for('staff_dashboard.manage_guide'))
        return render_template('staff_edit_guide.html', item=item)
     

@staff_bp.route('/delete_guide/<int:item_id>', methods=['POST'])
def delete_guide(item_id):
    cursor = getCursor()
    delete_sql = "DELETE FROM FRESHWATER_PEST_AND_DISEASE_BIOSECURITY_GUIDE WHERE FreshwaterID = %s"
    cursor.execute(delete_sql, (item_id,))
    cursor.close()
    flash('Guide item deleted successfully!')
    return redirect(url_for('staff_dashboard.manage_guide'))

