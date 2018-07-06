from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_mysqldb import MySQL
from wtforms.fields.html5 import DateField
from wtforms import Form, StringField, TextAreaField, PasswordField, FloatField, IntegerField, validators
from passlib.hash import sha256_crypt
from functools import wraps

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


def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Login to proceed', 'danger')
			return redirect(url_for('login'))
	return wrap


def is_manager(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			cur = mysql.connection.cursor()
			current_user = session['username']
			result = cur.execute('SELECT * from users WHERE username = %s', [current_user])
			user = cur.fetchone()
			user_role = user['role']
			if user_role == 0:
				cur.close()
				return f(*args, **kwargs)
			else:
				cur.close()
				flash('Login as manager to access this endpoint')
				return 'Unauthorized request'
		else:
			cur.close()
			flash('Login to proceed', 'danger')
			return 'Unauthorized request'
	return wrap


class RegisterForm(Form):
	username = StringField('Username', [validators.Length(min=4, max=20, message='Enter a valid username'), validators.DataRequired()])
	email = StringField('Email', [validators.DataRequired(),validators.Email(message='Enter a valid email')])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match')
	])
	confirm = PasswordField('Confirm Password', [validators.DataRequired()])


class LoginForm(Form):
	username = StringField('Username', [validators.DataRequired()])
	password = PasswordField('Password', [validators.DataRequired()])


class AddInventoryRecord(Form):
	name = StringField('Product Name', [validators.Length(min=2, message='Enter a valid username'), validators.DataRequired()])
	vendor = StringField('Vendor Name', [validators.Length(min=2, message='Enter a valid username'), validators.DataRequired()])
	mrp = FloatField('Cost', [validators.DataRequired()])
	batch_num = IntegerField('Batch Number', [validators.DataRequired()])
	batch_date = DateField('Batch Date', format='%Y-%m-%d')
	quantity = IntegerField('Quantity', [validators.DataRequired()])


@app.route('/add')
@is_logged_in
def add():
	form = AddInventoryRecord(request.form)
	cur = mysql.connection.cursor()
	current_user = session['username']
	result = cur.execute('SELECT * from users WHERE username = %s', [current_user])
	user = cur.fetchone()
	user_role = user['role']
	if user_role == 0:
		cur.close()
		return render_template('add.html', form=form)
	elif user_role == 1:
		cur.close()
		return render_template('adda.html', form=form)



@app.route('/api/addrecord/', methods=['POST'])
@is_manager
def addrecord():
	name = request.form['name']
	vendor = request.form['vendor']
	mrp = request.form['mrp']
	batch_num = request.form['batch_num']
	batch_date = request.form['batch_date']
	quantity = request.form['quantity']
	status = 'Approved'
	cur = mysql.connection.cursor()
	cur.execute('INSERT INTO products(name, vendor, mrp, batch_num, batch_date, quantity, status) VALUES(%s, %s, %s, %s, %s, %s, %s)', (name, vendor, mrp, batch_num, batch_date, quantity, status))
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'name' : name,
		'vendor' : vendor,
		'mrp' : mrp,
		'batch_num' : batch_num,
		'batch_date' : batch_date,
		'quantity' : quantity,
		'status' : status
		})

@app.route('/api/addrecord/assistant/', methods=['POST'])
@is_logged_in
def addrecordassistant():
	name = request.form['name']
	vendor = request.form['vendor']
	mrp = request.form['mrp']
	batch_num = request.form['batch_num']
	batch_date = request.form['batch_date']
	quantity = request.form['quantity']
	status = 'Pending Approval'
	cur = mysql.connection.cursor()
	cur.execute('INSERT INTO products(name, vendor, mrp, batch_num, batch_date, quantity, status) VALUES(%s, %s, %s, %s, %s, %s, %s)', (name, vendor, mrp, batch_num, batch_date, quantity, status))
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'name' : name,
		'vendor' : vendor,
		'mrp' : mrp,
		'batch_num' : batch_num,
		'batch_date' : batch_date,
		'quantity' : quantity,
		'status' : status
		})


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
	form = LoginForm(request.form)
	if request.method == 'POST':
		username = request.form['username']
		password_candidate = request.form['password']
		cur = mysql.connection.cursor()
		result = cur.execute("SELECT * FROM users WHERE username = %s",[username])
		if result > 0:
			data = cur.fetchone()
			password = data['password']
			role = data['role']
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('login details authenticated')
				session['logged_in'] = True
				session['username'] = username
				session['role'] = role
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

@app.route('/view')
@is_logged_in
def view():
	return "view all"


@app.route('/view/pending')
@is_manager
def viewpending():
	return "view pending"


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('Logged out!', 'success')
	return redirect(url_for('login'))


@app.route('/inventory')
@is_logged_in
def inventory():
	return render_template('inventory.html')


if __name__ == '__main__':
	app.secret_key = 'isthissafe?'
	app.run(debug=True)
