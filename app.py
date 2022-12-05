from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_script import Manager
from functools import wraps

import profile_file
import login_file
import trainor
import equipment
import members
import plans
import receptionist

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'gym_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'aabb'

mysql = MySQL(app)

def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Por favor, realize o ', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_trainor(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 3:
			return f(*args, **kwargs)
		else:
			flash('Não é um treinador', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_admin(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] == 1:
			return f(*args, **kwargs)
		else:
			flash('Não é um Admin', 'danger')
			return redirect(url_for('login'))
	return wrap

def is_recep_level(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['profile'] <= 2:
			return f(*args, **kwargs)
		else:
			flash('Não tem autorização para ver essa página', 'danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	result = login_file.login_func(mysql)
	return result


@app.route('/update_password/<string:username>', methods = ['GET', 'POST'])
def update_password(username):
	result = profile_file.update(username,mysql)
	return result

@app.route('/adminDash')
@is_logged_in
@is_admin
def adminDash():
	return render_template('adminDash.html')

@app.route('/addTrainor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addTrainor():
	result = trainor.add(mysql)
	return result

@app.route('/deleteTrainor', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def deleteTrainor():
	result = trainor.delete(mysql)
	return result

@app.route('/addRecep', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addRecep():
	result = receptionist.add(mysql)
	return result

@app.route('/deleteRecep', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def deleteRecep():
	result = receptionist.delete(mysql)
	return result

@app.route('/addEquip', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def addEquip():
	result = equipment.add(mysql)
	return result

@app.route('/removeEquip', methods = ['GET', 'POST'])
@is_logged_in
@is_admin
def removeEquip():
	result = equipment.delete(mysql)
	return result

@app.route('/addMember', methods = ['GET', 'POST'])
@is_logged_in
@is_recep_level
def addMember():
	result = members.add(mysql)
	return result

@app.route('/deleteMember', methods = ['GET', 'POST'])
@is_logged_in
@is_recep_level
def deleteMember():
	result = members.delete(mysql)
	return result

@app.route('/viewDetails')
def viewDetails():
	cur = mysql.connection.cursor()
	cur.execute("SELECT username FROM info WHERE username != %s", [session['username']])
	result = cur.fetchall()
	return render_template('viewDetails.html', result = result)

@app.route('/recepDash')
@is_recep_level
def recepDash():
	return render_template('recepDash.html')

@app.route('/trainorDash', methods = ['GET', 'POST'])
@is_logged_in
@is_trainor
def trainorDash():
	result = trainor.openDash(mysql)
	return result

@app.route('/updatePlans', methods = ['GET', 'POST'])
@is_trainor
def updatePlans():
	result = plans.update()
	return result


@app.route('/memberDash/<string:username>')
@is_logged_in
def memberDash(username):
	result = members.openDash(username, mysql)
	return result

@app.route('/profile/<string:username>')
@is_logged_in
def profile(username):
	result = profile_file.look_prof(username,mysql)
	return result

@app.route('/edit_profile/<string:username>', methods = ['GET', 'POST'])
@is_logged_in
def edit_profile(username):
	result = profile_file.edit_prof(username,mysql)
	return result

@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))


if __name__ == "__main__":
	app.secret_key = 'aabb'
	app.debug = True
	manager = Manager(app)
	manager.run()