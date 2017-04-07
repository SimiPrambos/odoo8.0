import os
from flask import Flask, render_template, flash, request, redirect, url_for, session
from content_management import Content
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from dbconnect import connection
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from functools import wraps
import gc
from flask_socketio import SocketIO, send


app = Flask(__name__)
DIC = Content()

app.config['SECRET_KEY'] = '51m1pr4mb05'
socketio = SocketIO(app)


#ext func
#########################################################################################################################
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.Required(),validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.Required()])

def login_req(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return func(*args, **kwargs)
		else:
			flash("You need to login man!", "alert alert-warning")
			return redirect(url_for('login'))
	return wrap
############################################################################################################################



#######################################################################################################
@app.route('/')
def home():
	title = 'Home'
	judul = 'Welcome to Flask Web App'
	#paragraph = {"menu": [["menu satu", "/menu-satu/"], ["menu dua", "/menu-dua/"]]}
	return render_template('index.html', title = title, judul = judul)

@app.route('/login/', methods=['GET', 'POST'])
def login():
	error = ''
	try:
		c, conn = connection()
		if request.method == 'POST':
			data = c.execute("SELECT * FROM users WHERE username = (%s)",
				[thwart(request.form['username'])])
			data = c.fetchone()[2]

			if sha256_crypt.verify(request.form['password'], data):
				session['logged_in'] = True
				session['username'] = request.form['username']

				flash("Hello " + (request.form['username']) + ", Welcome to Flask Web App", "alert alert-success")
				return redirect(url_for('chat'))
			else:
				flash("Username or password is invalid, Please try again!", "alert alert-warning")
				return redirect(url_for('login'))
		gc.collect()
		return render_template("login.html", error=error)

	except Exception as e:
		flash("Username or password is invalid, Please try again!", "alert alert-warning")
		return redirect(url_for('login'))

@app.route('/logout/')
@login_req #------------> ext function to require login
def logout():
	session.clear()
	flash("You are logged out!", "alert alert-warning")
	gc.collect
	return redirect(url_for('login'))



@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection() #----------------------------------------> Connecting to DB

            x = c.execute("SELECT * FROM users WHERE username = (%s)", (thwart(username),))

            if int(x) > 0:
                flash("That username is already taken, please choose another", "alert alert-danger")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)", (thwart(username), thwart(password), thwart(email), thwart("coming soon")))
                
                conn.commit()
                flash("Hello " + (username), "alert alert-info")
                flash("Thanks for registering!", "alert alert-success")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('home'))
        return render_template("register.html", form=form)
    except Exception as e:
        return(str(e))

@app.route('/content/')
def cm():
	return render_template("index.html", dict = DIC)
	
@app.route('/about/')
def about():
	title = "About Page"
	judul = "This is About page!"
	return render_template('index.html', title=title, judul=judul)

@socketio.on('message')
def handleMessage(msg):
	print "Message: " + msg
	send(msg, broadcast=True)

@app.route('/chat/')
def chat():
	title = 'Simi Chat'
	judul = 'Simple Chat with Socket.io'
	#user = (request.form['username'])
	return render_template('chat.html', title=title, judul=judul)

@app.errorhandler(404)
def not_found(error):
	return("Page doesn't exists!"), 404
"""
####### Chat #########
@socketio.on('message')
def handleMessage(msg):
	print('Message: ' + msg)
	send(msg, broadcast=True)
#############################################################################################################
"""
try:
	if __name__ == "__main__":
		socketio.run(app)
except KeyboardInterrupt:
	print "restarting app ..."
	#os.system('python main.py')
