from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'inventory'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
	return render_template('index.html')


class RegisterForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=20), validators.DataRequired()])
	email = StringField('Email', [validators.Length(min=4, max=100), validators.DataRequired()])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password', [validators.DataRequired()	])

class LoginForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=20), validators.DataRequired()])
	password = PasswordField('Password', [validators.DataRequired()])


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		email = form.email.data
		password = sha256_crypt.encrypt(str(form.password.data))
		role = '1'
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO users(username, password, email, role) VALUES(%s, %s, %s, %s)",(username, password, email, role))
		mysql.connection.commit()
		cur.close()
		flash('Your are now registered and can login', 'success')
		return redirect(url_for('login'))	
	return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM users WHERE username = %s",[username])
		if result > 0:
			data = cur.fetchone()
			password = data['password']
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('login details authenticated')
				session['logged_in'] = True
				session['username'] = username
				flash('Login success', 'success')
				return redirect(url_for('inventory'))
			else:
				error = 'Invalid username/password'
				return render_template('login.html', error=error, form=form)
			cur.close()			
		else:
			error = 'Invalid username/password'
			return render_template('login.html', error=error, form=form)
	return render_template('login.html', form=form)

@app.route('/logout')
def logout():
	session.clear()
	flash('Logged out!', 'success')
	return redirect(url_for('login'))

@app.route('/inventory')
def inventory():
	return render_template('inventory.html')

if __name__ == '__main__':
	app.secret_key = 'isthissafe?'
	app.run(debug=True)
