import base64
import gridfs
from bson import ObjectId
from flask import Flask, Response, redirect, url_for, request, session, abort, render_template, jsonify
from flask_login import LoginManager, UserMixin, \
    login_required, login_user, logout_user
from pymongo import MongoClient
from flask_mail import *
from random import *
import re
from models.user import User

app = Flask(__name__)
mail = Mail(app)
app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = '[email]'
app.config['MAIL_PASSWORD'] = '[password]'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)
client = MongoClient("mongodb://[username]:[password]@[ip_address]/[db_name]")
db = client.get_database('[db_name]')
grid_fs = gridfs.GridFS(db)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@app.route('/')
def home():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        session['username'] = request.form['email']
        username = request.form['email']
        password = request.form['password']
        db_collection = db.user_collection
        if db_collection.find_one({"email": username,"password":password}):
            user = User(username,password)
            print("login")
            login_user(user)
            return render_template("home.html")
        else:
            return render_template("login.html",msg="Incorrect username or password.")
    else:
        return render_template("login.html")

@app.route("/allpets", methods=["GET", "POST"])
@login_required
def allpets():
    db_pet = db.pet_collection
    pets = db_pet.find({})
    return render_template("pets.html", puppies=pets)

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("index.html")


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template("login.html",msg="Login Failed")



@login_manager.user_loader
def load_user(username):
    return User(username,"password")

@app.route('/upload', methods=['POST','GET'])
@login_required
def upload():
    return render_template("addpet_verified.html",useremail=session['username'])

@app.route('/edit', methods=['POST','GET'])
@login_required
def edit():

        image = request.files['img']
        image_string = base64.b64encode(image.read())
        db.pet_collection.insert_one(
                {
                    "name": request.form.get('name'),
                    "breed": request.form.get('breed'),
                    "age": request.form.get('age'),
                    "gender": request.form.get('gender'),
                    "type": request.form.get('type'),
                    "weight": request.form.get('weight'),
                    "address": [request.form.get('address'),request.form.get('Lat'),request.form.get('Lng')],
                    "owner": request.form.get('owner'),
                    "contactemail":request.form.get('contactemail'),
                    "profile_image": image_string.decode('utf-8')
                }
            )
        db_pet = db.pet_collection
        pets = db_pet.find({"contactemail": session['username']})
        return render_template("mypets.html", puppies=pets)



@app.route('/registeruser',methods =['GET', 'POST'])
def registeruser():
    user_otp = request.form['otp']
    if otp == int(user_otp):
        db_collection = db.user_collection
        msg = ''
        if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
            password = request.form['password']
            email = request.form['email']
            if db_collection.find_one({"email": email}):
                msg = 'Email id already in Use !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif  not password or not email:
                msg = 'Please fill out the form !'
            else:
                user_data = {
                    'password' : password,
                    'email': email
                }

                image_id = db_collection.insert_one(user_data).inserted_id
                msg = 'You have successfully registered !'
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template('register_verified.html', msg=msg)
    else:
        return render_template('register.html', msg="Incorrect OTP. Register Again!!!!!!!")

@app.route('/singlepet',methods =['GET', 'POST'])
@login_required
def singlepet():
    pet = request.form["adopt"]
    pet_details = db.pet_collection.find_one(ObjectId(pet))
    return render_template('adoption.html', pup=pet_details, currentuser=session['username'])

@app.route('/verify',methods = ["POST"])
def verify():
 global otp
 otp = randint(000000,999999)
 email = request.form["contactemail"]
 msg = Message('OTP',sender = 'notification.petagent@gmail.com', recipients = [email])
 msg.body = str(otp)
 mail.send(msg)
 return render_template('register_verified.html',useremail =email)

@app.route('/adopt',methods = ["POST"])
@login_required
def adopt():
 email = request.form["yourmail"]
 owner = request.form["owneremail"]
 pet_name = request.form["name"]
 breed= request.form["breed"]
 your_message = request.form["yourmsg"]
 your_message = "NOTE: \nThis is a system generated mail. Please relpy to : "+ email +"\n \n"+ "Showed Interest on "+str(pet_name)+\
                ", breed:"+str(breed)+'\n \n'+ "Message follows:\n \n "+str(your_message)
 msg = Message(sender = 'notification.petagent@gmail.com', recipients = [owner])
 msg.body = str(your_message)
 mail.send(msg)
 db_pet = db.pet_collection
 pets = db_pet.find({})
 return render_template("pets.html", puppies=pets)


@app.route('/register',methods =['GET', 'POST'])
def register():
    return render_template('register.html')

@app.route('/mypets',methods =['GET', 'POST'])
@login_required
def mypets():
    db_pet = db.pet_collection
    pets = db_pet.find({"contactemail": session['username']})
    return render_template("mypets.html", puppies=pets)

@app.route('/deletepet',methods =['GET', 'POST'])
@login_required
def deletepet():
    pet = request.form['delete']
    print(pet)
    db_pet = db.pet_collection
    # db.pet_collection.remove({"_id": ObjectId(pet)})
    db_pet.delete_one( {"_id": ObjectId(pet)})
    pets = db_pet.find({"contactemail": session['username']})
    return render_template("mypets.html", puppies=pets)

@app.route("/availablepets", methods=["GET", "POST"])
def availablepets():
    db_pet = db.pet_collection
    pets = db_pet.find({})
    out = []
    for q in pets:
        out.append({'Pet Name':q['name'],'Breed':q['breed'],'Age':q['age'],"Gender":q['gender'],'Type':q['type'],"weight":q['weight'],"Address":q["address"][0]})
    return jsonify(out)

if __name__ == "__main__":
    global otp
    app.run()