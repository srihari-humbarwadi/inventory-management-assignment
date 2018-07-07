from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
from flask_mysqldb import MySQL
from wtforms.fields.html5 import DateField
from wtforms import Form, StringField, TextAreaField, PasswordField, FloatField, IntegerField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from flask_json import FlaskJSON, JsonError, json_response, as_json

app = Flask(__name__)
FlaskJSON(app)
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
	content = request.get_json()
	name = content['name']
	vendor = content['vendor']
	mrp = content['mrp']
	batch_num = content['batch_num']
	batch_date = content['batch_date']
	quantity = content['quantity']
	status = 'Approved'
	cur = mysql.connection.cursor()
	cur.execute('INSERT INTO products(name, vendor, mrp, batch_num, batch_date, quantity, status) VALUES(%s, %s, %s, %s, %s, %s, %s)', (name, vendor, mrp, batch_num, batch_date, quantity, status))
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'Status' : 'ok',
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
	content = request.get_json()
	name = content['name']
	vendor = content['vendor']
	mrp = content['mrp']
	batch_num = content['batch_num']
	batch_date = content['batch_date']
	quantity = content['quantity']
	status = 'Pending Addition'
	cur = mysql.connection.cursor()
	cur.execute('INSERT INTO products(name, vendor, mrp, batch_num, batch_date, quantity, status) VALUES(%s, %s, %s, %s, %s, %s, %s)', (name, vendor, mrp, batch_num, batch_date, quantity, status))
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'Status' : 'ok',
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
				return redirect(url_for('dashboard'))
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
	cur = mysql.connection.cursor()
	current_user = session['username']
	result = cur.execute('SELECT * from users WHERE username = %s', [current_user])
	user = cur.fetchone()
	user_role = user['role']
	return render_template('view.html', role=user_role)


@app.route('/view/pending')
@is_logged_in
def viewpending():
	cur = mysql.connection.cursor()
	current_user = session['username']
	result = cur.execute('SELECT * from users WHERE username = %s', [current_user])
	user = cur.fetchone()
	user_role = user['role']
	return render_template('view_pending.html', role=user_role)


@app.route('/modify/<id>/<name>')
@is_logged_in
def modify(id, name):
	cur = mysql.connection.cursor()
	current_user = session['username']
	uresult = cur.execute('SELECT * from users WHERE username = %s', [current_user])
	user = cur.fetchone()
	user_role = user['role']
	results = cur.execute('SELECT * FROM products WHERE id = %s AND name = %s', [id, name])
	if results > 0:
		data = cur.fetchone()
		cur.close()
	else:
		cur.close()
		error = 'Something went wrrong, please try again'
		return render_template('view.html', error=error)
	form = AddInventoryRecord(request.form)
	if user_role == 0:
		cur.close()
		return render_template('modify.html', form=form, data=data)
	elif user_role == 1:
		cur.close()
		return render_template('modifya.html', form=form, data=data)


@app.route('/api/modifyrecord/', methods=['POST'])
@is_manager
def modifyrecord():
	content = request.get_json()
	name = content['name']
	vendor = content['vendor']
	quantity = content['quantity']
	mrp = content['mrp']
	status = 'Approved'
	cur = mysql.connection.cursor()
	cur.execute('UPDATE products SET quantity = %s, mrp = %s, status = %s WHERE name = %s AND vendor = %s', [quantity, mrp, status, name, vendor])
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'Status' : 'ok',
		'name' : name,
		'quantity' : quantity,
		'status' : status
		})

@app.route('/api/modifyrecord/assistant/', methods=['POST'])
@is_logged_in
def modifyrecordassistant():
	content = request.get_json()
	name = content['name']
	vendor = content['vendor']
	quantity = content['quantity']
	mrp = content['mrp']
	status = 'Pending modification'
	cur = mysql.connection.cursor()
	cur.execute('UPDATE products SET quantity = %s, mrp = %s, status = %s WHERE name = %s AND vendor = %s', [quantity, mrp, status, name, vendor])
	mysql.connection.commit()
	cur.close()
	return jsonify({
		'Status' : 'ok',
		'name' : name,
		'quantity' : quantity,
		'status' : status
		})



@app.route('/api/get/')
@is_logged_in
def get():
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT * FROM products')
	data = cur.fetchall()
	cur.close()
	return jsonify(data)


@app.route('/api/get/pending/')
@is_logged_in
def getpending():
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT * FROM products WHERE NOT status = %s', ['Approved'])
	data = cur.fetchall()
	cur.close()
	return jsonify(data)


@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('Logged out!', 'success')
	return redirect(url_for('login'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')



@app.route('/api/approve/', methods=['POST'])
@is_manager
def approve():
	content = request.get_json()
	name = content['name']
	id = content['id']
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT * FROM products WHERE id = %s AND name = %s',[id, name])
	data = cur.fetchone()
	curr_status = data['status']
	status = 'Approved'
	if curr_status != status:
		if curr_status == 'Pending deletion':
			cur.execute('DELETE FROM products WHERE id = %s AND name = %s',[id, name])
			mysql.connection.commit()
			cur.close()
			return jsonify({
				'status':'ok'
				})
		else:
			cur.execute('UPDATE products SET status = %s WHERE id = %s AND name = %s', [status, id, name])
			mysql.connection.commit()
			cur.close()
			return jsonify({
				'status': 'ok'
				})
	else:
		return jsonify({
			'status':'already approved'
			})



@app.route('/api/delete/', methods=['POST'])
@is_logged_in
def delete():
	content = request.get_json()
	name = content['name']
	id = content['id']
	cur = mysql.connection.cursor()
	results = cur.execute('SELECT * FROM products WHERE id = %s AND name = %s',[id, name])
	data = cur.fetchone()
	curr_status = data['status']
	current_user = session['username']
	uresult = cur.execute('SELECT * from users WHERE username = %s', [current_user])
	user = cur.fetchone()
	user_role = user['role']
	if user_role == 0:
		cur.execute('DELETE FROM products WHERE id = %s AND name = %s',[id, name])
		mysql.connection.commit()
		cur.close()
		return jsonify({
			'status':'ok'
			})
	elif user_role == 1:
		status = 'Pending deletion'
		if curr_status != status:
			cur.execute('UPDATE products SET status = %s WHERE id = %s AND name = %s', [status, id, name])
			mysql.connection.commit()
			cur.close()
			return jsonify({
				'status':'ok'
			})
		else:
			return jsonify({
				'status':'already marked for deletion'
				})

if __name__ == '__main__':
	app.secret_key = 'isthissafe?'
	app.run(debug=True, host='0.0.0.0')
