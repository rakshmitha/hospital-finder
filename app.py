from flask import Flask, jsonify, request, redirect, render_template,session,url_for
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
import random
import string
from bson.objectid import ObjectId
import datetime
import os
bcrypt = Bcrypt()

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin-gokul:"+os.environ.get('MONGO_PASSWORD')+"@cluster0-oybfo.mongodb.net/Hospital_Pricing?retryWrites=true&w=majority"
mongo = PyMongo(app)
app.secret_key = "mysecret"
@app.route('/',methods = ['GET','POST'])
def index(): 
    hospitals = mongo.db.hospitals
    hospitals_from_db = hospitals.find()
    # if(session.get('page_no') == 2):
    #     session['page_no'] = 1
    print(hospitals_from_db)
    return render_template("index.html",  hospitals_list = hospitals_from_db)


@app.route('/trusted-commitee', methods=['GET', 'POST'])
def login():
    if session.get('email'):
        users = mongo.db.users
        hospitals = mongo.db.hospitals
        login_user = users.find_one({'email_id' : session.get('email')})
        users_from_db = users.find()
        hospitals_from_db = hospitals.find()
        if(session.get('page_no') == 2):
            session['page_no'] = 1
            return render_template("trusted-commitee-2.html", user = login_user, users_list = users_from_db, hospitals_list = hospitals_from_db)
        return render_template("trusted-commitee.html", user = login_user, users_list = users_from_db, hospitals_list = hospitals_from_db)
    if request.method == 'POST':
        if request.form['email'] == '':
            return render_template('login.html', error_msg = 'Please fill email field')
        if request.form['pass'] == '':
            return render_template('login.html', error_msg = 'Please fill password field')
        users = mongo.db.users
        login_user = users.find_one({'email_id' : request.form['email']})
        if login_user:
            if bcrypt.check_password_hash(login_user['password'], request.form['pass']):
                session['email'] = login_user['email_id']
                return redirect(url_for('login'))
        return render_template('login.html', error_msg = 'Invalid Credentials')
    return render_template('login.html', error_msg = '')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/trusted-commitee/join/<referral>',methods = ['GET', 'POST'])
def register(referral):
    if request.method == 'POST':
        form_details = {'username' : request.form['username'], 'city' : request.form['city'], 'email' : request.form['email'], 'referred_by': request.form['referred_by']}
        if request.form['username'] == '':
            return render_template('register.html', error_msg = 'Please fill name field', form_details = form_details)
        if request.form['city'] == '':
            return render_template('register.html', error_msg = 'Please fill city field', form_details = form_details)
        if request.form['email'] == '':
            return render_template('register.html', error_msg = 'Please fill email address field', form_details = form_details)
        if request.form['pass'] == '':
            return render_template('register.html', error_msg = 'Please fill password field', form_details = form_details)
        if request.form['confirmpass'] == '':
            return render_template('register.html', error_msg = 'Please fill confirm password field', form_details = form_details)
        
        users = mongo.db.users
        existing_user = users.find_one({'email_id' : request.form['email']})
        if existing_user is None:
            password = request.form['pass']
            confirm_password = request.form['confirmpass']
            if(len(password) >=8 and password == confirm_password):
                hashpass = bcrypt.generate_password_hash(password)
                letters_and_digits = string.ascii_letters + string.digits
                referral_id = ''.join((random.choice(letters_and_digits) for i in range(16)))
                current_date = datetime.date.today()
                date = current_date.strftime("%d-%m-%Y")
                users.insert({'name':request.form['username'],'city':request.form['city'],'email_id' : request.form['email'],
                'password':hashpass, 'referral_id':referral_id, 'referred_by': request.form['referred_by'], 'joined_at': date})
                session['email'] = request.form['email']
                return redirect(url_for('login'))
            elif(len(password) < 8 ):
                return render_template('register.html', error_msg = 'Password must be atleast 8 characters', form_details = form_details)
            elif(password != confirm_password):
                return render_template('register.html', error_msg = 'Password and confirm password fields does not match', form_details = form_details)
        return render_template('register.html', error_msg = 'Email address already registered', form_details = form_details)
    users = mongo.db.users
    existing_user = users.find_one({'referral_id' : referral})
    if existing_user is None:
        return 'Invalid URL'
    form_details = {'username' : '', 'city' : '', 'email' : '', 'referred_by': existing_user['name']}
    return render_template('register.html', error_msg = '', form_details = form_details)

# THIS ROUTE SHOULD BE COMMENTED UNLESS ANY ADMIN WANTS TO JOIN WITHOUT REFERRAL
# @app.route('/trusted-commitee/join/admin',methods = ['GET', 'POST'])
# def admin_register():
#     form_details = {'username' : '', 'city' : '', 'email' : '', 'referred_by': "No one referred me. I'm The Admin."}
#     return render_template('register.html', error_msg = '', form_details = form_details)

@app.route('/trusted-commitee/user/<user_id>', methods=['GET', 'POST'])
def user_details(user_id):
    if session.get('email'):
        users = mongo.db.users
        login_user = users.find_one({'email_id' : session.get('email')})
        user_from_db = users.find_one({'_id' : ObjectId(user_id)})
        return render_template("user-details.html", user = login_user, user_from_db = user_from_db)
    return render_template('login.html', error_msg = '')

@app.route('/trusted-commitee/user/my_profile', methods=['GET', 'POST'])
def my_profile():
    if session.get('email'):
        users = mongo.db.users
        login_user = users.find_one({'email_id' : session.get('email')})
        return render_template("my-profile.html", user = login_user)
    return render_template('login.html', error_msg = '')

@app.route('/trusted-commitee/hospital/<hospital_id>', methods=['GET', 'POST'])
def hospital_details(hospital_id):
    if session.get('email'):
        session['page_no'] = 2
        users = mongo.db.users
        hospitals = mongo.db.hospitals
        login_user = users.find_one({'email_id' : session.get('email')})
        hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
        return render_template("hospital-details.html", user = login_user, hospital_from_db = hospital_from_db, error_msg='')
    return render_template('login.html', error_msg = '')

@app.route('/users/hospital/<hospital_id>', methods=['GET', 'POST'])
def users_hospital_details(hospital_id):
    hospitals = mongo.db.hospitals
    hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
    return render_template("display-hospital-details.html", hospital_from_db = hospital_from_db, error_msg='')
    

@app.route('/trusted-commitee/hospital/update/<hospital_id>', methods=['GET', 'POST'])
def update_hospital(hospital_id):
    if session.get('email'):
        session['page_no'] = 2
        if request.method == 'POST':
            hospitals = mongo.db.hospitals
            hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
            print('OPTION ::::',request.values.get("image-radio"))
            if request.values.get("image-radio") == 'option2':
                new_file = request.files['image']
                if(new_file.filename == ''):
                    file_name = 'Oiz637YiuxCSz1XA-default.png'
                else:
                    letters_and_digits = string.ascii_letters + string.digits
                    random_string = ''.join((random.choice(letters_and_digits) for i in range(16)))
                    file_name = random_string+'-'+new_file.filename
                    mongo.save_file(file_name, new_file)
            elif request.values.get("image-radio") == 'option1':
                file_name = hospital_from_db['file_name']

            hospital_name = request.values.get("hospital_name")
            city = request.values.get("city")
            description = request.values.get("description")
            address = request.values.get("address")
            contact = request.values.get("contact")
            currency = request.values.get("currency")
            field = request.values.getlist('field')
            price = request.values.getlist('price')
            category = request.values.get("category")
            created_at = hospital_from_db['created_at']
            created_by = hospital_from_db['created_by']
            current_date = datetime.date.today()
            date = current_date.strftime("%d-%m-%Y")
            data = {
                'hospital_name': hospital_name,
                'city': city,
                'description': description,
                'address' : address,
                'contact': contact,
                'file_name': file_name,
                'currency': currency,
                'field': field,
                'price': price,
                'category': category,
                'created_at': created_at,
                'updated_at': date,
                'created_by': created_by,
                'updated_by': session.get('email')
            }
            updated_hospital = {"$set": data}
            filt = {'_id' : ObjectId(hospital_id)}
            hospitals.update_one(filt, updated_hospital)
            print(data)
            return redirect(url_for('login'))
        users = mongo.db.users
        hospitals = mongo.db.hospitals
        login_user = users.find_one({'email_id' : session.get('email')})
        hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
        return render_template("update-hospital.html", user = login_user, hospital = hospital_from_db)
    return render_template('login.html', error_msg = '')

@app.route('/trusted-commitee/hospital/delete/<hospital_id>', methods=['GET', 'POST'])
def delete_hospital(hospital_id):
    if session.get('email'):
        session['page_no'] = 2
        if request.method == 'POST':
            hospitals = mongo.db.hospitals
            delete_input = request.values.get("delete-input")
            hidden_input = request.values.get("hidden-input")
            if(delete_input == hidden_input):
                hospitals.delete_one({'_id' : ObjectId(hospital_id)})
                return redirect(url_for('login'))
            users = mongo.db.users
            login_user = users.find_one({'email_id' : session.get('email')})
            hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
            return render_template("hospital-details.html", user = login_user, hospital_from_db = hospital_from_db, error_msg="Delete operation cannot be performed since you have typed incorrectly.")
    return render_template('login.html', error_msg = '')


@app.route('/image/<hospital_id>', methods=['GET', 'POST'])
def hospital_image(hospital_id):
    hospitals = mongo.db.hospitals
    hospital_from_db = hospitals.find_one({'_id' : ObjectId(hospital_id)})
    file_name = hospital_from_db['file_name']
    return mongo.send_file(file_name)

@app.route('/trusted-commitee/add-hospital', methods=['GET', 'POST'])
def add_hospital():
    if session.get('email'):
        session['page_no'] = 2
        if request.method == 'POST':
            hospitals = mongo.db.hospitals
            new_file = request.files['image']
            if(new_file.filename == ''):
                file_name = 'Oiz637YiuxCSz1XA-default.png'
            else:
                letters_and_digits = string.ascii_letters + string.digits
                random_string = ''.join((random.choice(letters_and_digits) for i in range(16)))
                file_name = random_string+'-'+new_file.filename
                mongo.save_file(file_name, new_file)
            hospital_name = request.values.get("hospital_name")
            city = request.values.get("city")
            address = request.values.get("address")
            description = request.values.get("description")
            contact = request.values.get("contact")
            currency = request.values.get("currency")
            field = request.values.getlist('field')
            price = request.values.getlist('price')
            category = request.values.get("category")
            current_date = datetime.date.today()
            date = current_date.strftime("%d-%m-%Y")
            data = {
                'hospital_name': hospital_name,
                'city': city,
                'description': description,
                'address' : address,
                'contact': contact,
                'file_name': file_name,
                'currency': currency,
                'field': field,
                'price': price,
                'category': category,
                'created_at': date,
                'updated_at': date,
                'created_by': session.get('email'),
                'updated_by': session.get('email')
            }
            hospitals.insert(data)
            print(data)
            return redirect(url_for('login'))
        users = mongo.db.users
        login_user = users.find_one({'email_id' : session.get('email')})
        return render_template("add-hospital.html", user = login_user)
    return render_template('login.html', error_msg = '')
    
if __name__ == '__main__':
    app.run(debug=True)
