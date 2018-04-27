import os
import sqlite3
from flask import *
from flask_sqlalchemy import *
from datetime import datetime
from flask import send_from_directory
from werkzeug.utils import secure_filename
from sqlalchemy import update


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///confessions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = 'random string'

UPLOAD_FOLDER = 'C:/Users/welcome/Desktop/SC/mainproject/flaskr/flaskr/static'

ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif','txt','pdf','JPG'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

class Users(db.Model):
	__tablename__='users'
	password = db.Column(db.String(255))
	email = db.Column(db.String(255),primary_key=True)
	name = db.Column(db.String(255))
	phone = db.Column(db.String(255))
	gender = db.Column(db.String(255))
	Birthday = db.Column(db.String(255))

class Image(db.Model):
	__tablename__='images'
	title = db.Column(db.String(255))
	desc =  db.Column(db.String(255))
	id =db.Column(db.Integer,primary_key=True)
	imagename = db.Column(db.String(255))
	upvotes =db.Column(db.Integer)
	downvotes =db.Column(db.Integer)
	comment = db.Column(db.String(255))

db.create_all()


@app.route("/register",methods = ['GET','POST'])
def register():
	if request.method =='POST':
		password = request.form['password']
		password1= request.form['password1']
		email = request.form['email']
		name = request.form['name']
		gender = request.form['gender']
		Birthday = request.form['Birthday']
		phone = request.form['phone']
		if(password == password1):
			try:
				user = Users(password=password,email=email,name=name,gender=gender,Birthday=Birthday,phone=phone)
				db.session.add(user)
				db.session.commit()
				msg="registered successfully"
			except:
				db.session.rollback()
				msg="error occured"
		else:
			return render_template("layout.html",error1="password doesnot match")
	db.session.close()
	return render_template("layout.html",msg=msg)

@app.route("/loginForm")
def loginForm():
		return render_template('layout.html', error='')


@app.route('/')
def layout():	
	return render_template("page1.html")

@app.route("/registerationForm")
def registrationForm():
	return render_template("layout.html")


@app.route("/login", methods = ['POST', 'GET'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		if is_valid(email, password):
			session['email'] = email
			session['logged_in'] = True
			global x
			x = email
			return redirect(url_for('index'))
		else:
			error = 'Invalid UserId / Password'
			return render_template('layout.html', error=error)
x=""		
@app.route('/index')
def index():
	if 'email' in session:
		email = session['email']
		image1 = "SELECT * FROM images"
		data1 = db.engine.execute(image1).fetchall()
		return render_template('main.html',email=email,name=data1)
	return render_template('page1.html')

def is_valid(email,password):
	stmt = "SELECT email, password FROM users"
	data = db.engine.execute(stmt).fetchall()
	for row in data:
		if row[0] == email and row[1] == password:
			return True
	return False

@app.route("/write")
def write():
	return render_template('post.html')

@app.route("/About")
def about():
	stmt = "SELECT * FROM users"
	data = db.engine.execute(stmt).fetchall()
	for confession1 in data:
		if(confession1.email==x):
			Name=confession1.name
			Email=confession1.email
			Birthday=confession1.Birthday
			gender=confession1.gender
			mobile=confession1.phone
			return render_template('about.html',Name=Name,Email=Email,Birthday=Birthday,gender=gender,mobile=mobile)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	
	if request.method == 'POST':
		title = request.form['title']
		desc =  request.form['text']
	
		# check if post request has file path
		if 'file' not in request.files:
			print "return............."
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		print file
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			# return render_template("post.html",name=file.filename)
			return redirect(url_for('uploaded_file',filename=file.filename,title=title,desc=desc))
	error="error occured"
	return render_template("post.html",error=error)
	
def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>/<title>/<desc>',methods=['GET', 'POST'])
def uploaded_file(filename,title,desc):
	print filename
	ImagesAll = Image(imagename=filename,title=title,desc=desc,upvotes=0,downvotes=0,comment="comments goes here \n")
	db.session.add(ImagesAll)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/votes/<xid>', methods=['GET', 'POST'])
def votes(xid):
	xid=int(xid)
	if request.method == 'POST':
		name = request.form['voted']
		stmt=Image.query.filter_by(id=xid).all()[0]
		if(name =="like"):
			stmt.upvotes+=1
			db.session.commit()
			return redirect(url_for('index'))
		else:
			stmt.downvotes+=1
			db.session.commit()
			return redirect(url_for('index'))
	return render_template("page1.html")

@app.route('/comment/<xid>', methods=['GET', 'POST'])
def comment(xid):
	xid=int(xid)
	if request.method == 'POST':
		name = request.form['text']
		if(len(name)>0):
			stmt=Image.query.filter_by(id=xid).all()[0]
			z=stmt.comment.replace('\n','<br>')
			s=z+"\n"+name
			s=s.replace('\n','<br>')
			stmt.comment=s
			db.session.commit()
			return redirect(url_for('index'))
		return redirect(url_for('index'))

@app.route('/sign/<name>/<email>')
def sign(name,email):
	try:
		user = Users(password=None,email=email,name=name,gender=None,Birthday=None,phone=None)
		db.session.add(user)
		db.session.commit()
		msg="registered successfully"
	except:
		db.session.rollback()
		msg="error occured"
	session['email'] = email
	session['logged_in'] = True
	global x
	x=email
	return redirect(url_for('index'))

@app.route('/logout')
def logout():
	session['logged_in'] = False
	session.pop('email',None)
	x=''
	return redirect(url_for('index'))

if __name__ =='__main__':
	
	app.run(port=3522)