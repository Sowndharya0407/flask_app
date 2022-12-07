# """the Flask class to create a Flask application instance, the render_template() function to render templates,
#  the request object to handle requests, the url_for() function to construct URLs for routes, 
#  and the redirect() function for redirecting users."""
from flask import Flask,render_template,request,jsonify,redirect,url_for
import os                                               # used to construct a file path for your database.db database file.
from flask_sqlalchemy import SQLAlchemy                 # to access all the functions,helpers and classes from SQLAlchemy
from sqlalchemy.sql import func                         # helper from sqlalchemy.sql module to access the sql functions
import rsa
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)                                   # instance of flask application and used to configure  the two flask-SQLAlchemy configuration keys

""""below are the set up a database file path,configure and connect application with sqlalchemy"""

base_dir = os.path.abspath(os.path.dirname(__file__))   # construct a path for SQLite database file
                                                        # Database URI specifys the database you want to establish a connection with 
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(base_dir,'database.db6') #connect to a database.db database file in your flask_app directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # disable tracking modifications of objects. 
db = SQLAlchemy(app)                                    # database object to connect flask application with SQLAlchemy
                                                        # use this db object to interact with your database.
publicKey, privateKey = rsa.newkeys(512)
# app.secret_key = "__privatekey__"


class User(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),nullable = False,unique = True)
    password = db.Column(db.String(256),nullable = False)

    def __init__(self,name,password):
        self.name = name
        self.password = password     

    def __repr__(self):
        return f'<User {self.name}>'

class Upload(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    
    def __init__(self,filename,data):
        self.filename = filename
        self.data = data
    
    def __repr__(self):
        return f'<Upload {self.filename}>'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # return render_template('')
    return "Hellow sowndharyakrish"

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        try:
            print('inside a block')
            input = request.get_json(silent = True)
            username = input['username']
            password = input['password']
            password2 = input['password2']
            if not username or not password or not password2:
                print("should not be empty")
                return jsonify({"status":"Username or password cannot be empty"}),400
            
            elif username and password:
                print("username",username)
                # found_user = User.query.filter(User.name == username,User.password == password).all()
                found_user = User.query.filter_by(name = username).first()
                if found_user:
                    # return render_template("error.html")
                    return jsonify({"status":"User already exist"}),409
                elif not found_user:
                    if password == password2:
                        encrypted_pwd = pbkdf2_sha256.hash(password)
                        print("encrypted_pwd",encrypted_pwd)
                        user_obj = User(username,encrypted_pwd)
                        db.session.add(user_obj)
                        db.session.commit()
                        # return render_template('login.html')
                        return jsonify({"status":"registered successfully"}),200   
                    else:
                        return jsonify({"status":"Password doesn't match.Try again"})                  
        
        except Exception as error:
            print(str(error))
            return jsonify({"status":"API failed","missing":str(error) + " is missing"}),400
    elif request.method == 'GET':
        # return render_template('register.html')
        pass

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        try:
            print('cmng inside')
            input = request.get_json(silent = True)
            username = input['username']
            password = input['password']
            found_user = User.query.filter_by(name = username).first()
            if found_user:
                enc_password = User.query.filter_by(name = str(username)).first().password
                print("enc_password==",enc_password)   
                if enc_password:
                    if pbkdf2_sha256.verify(password,enc_password):
                        return jsonify({"status":"logged in successfully","username":username}),200
                    else:
                        return jsonify({"status":"Incorrect password"}),400              
            
            return jsonify({"status":"User not found"}),404
        except Exception as error:
            # return redirect('login.html')
            return jsonify({"status":"API Failed","message":str(error) + " is missing"}),400

@app.route('/upload_file',methods = ['GET','POST'])
def upload_file():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({"status":"No 'file' key present in the request"}), 400
            uploaded_file = request.files['file']  
            if uploaded_file.filename == '':
                return jsonify({"status":"No file selected for upload"}), 404
            else:
                upload_obj = Upload(filename = uploaded_file.filename, data = uploaded_file.read())
                db.session.add(upload_obj)
                db.session.commit()
                return jsonify({"status":"File uploaded successfully"}),200
        except Exception as error:
            return jsonify({"status":"API Failed","message":str(error)}),400    


if __name__ == '__main__':
    app.run(debug=True,port=5000,host='localhost')   