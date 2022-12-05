from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt


choices = []
values = []
choices2 = []

class AddMemberForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    plan  = RadioField('Select Plan', choices = choices)
    trainor = SelectField('Select Trainor', choices = choices2)
    street = StringField('Street', [validators.Length(min = 1, max = 100)])
    city = StringField('City', [validators.Length(min = 1, max = 100)])
    phone = StringField('Phone', [validators.Length(min = 1, max = 100)])


def add(mysql):
	cur = mysql.connection.cursor()
	
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	
	q = cur.execute("SELECT DISTINCT name FROM plans")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['name'],b[i]['name'])
		choices.append(tup)
	
	q = cur.execute("SELECT username FROM trainors")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices2.append(tup)
	
	cur.close()
	
	form = AddMemberForm(request.form)
	if request.method == 'POST' and form.validate():
		#app.logger.info("setzdgxfhcgjvkhbjlkn")
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		street = form.street.data
		city = form.city.data
		phone = form.phone.data
		plan = form.plan.data
		trainor = form.trainor.data
		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, street, city, profile, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", (name, username, password, street, city, 4,phone))
		cur.execute("INSERT INTO members(username, plan, trainor) VALUES(%s, %s, %s)", (username, plan, trainor))
		mysql.connection.commit()
		cur.close()
		choices2.clear()
		choices.clear()
		flash('You added a new member!!', 'success')
		if(session['profile']==1):
			return redirect(url_for('adminDash'))
		return redirect(url_for('recepDash'))
	return render_template('addMember.html', form=form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM members")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = delete.DeleteRecepForm(request.form)
	if request.method == 'POST':
		username = form.username.data
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM members WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('You deleted a member from the GYM!!', 'success')
		if(session['profile']==1):
			return redirect(url_for('adminDash'))
		return redirect(url_for('recepDash'))
	return render_template('deleteRecep.html', form = form)

def openDash(username, mysql):
	if session['profile']==4 and username!=session['username']:
		flash('You aren\'t authorised to view other\'s Dashboards', 'danger')
		return redirect(url_for('memberDash', username = session['username']))
	if session['profile']!=4:
		if session['profile']==1:
			return redirect(url_for('adminDash'))
		if session['profile']==2:
			return redirect(url_for('recepDash', username = username))
		if session['profile']==3:
			return redirect(url_for('trainorDash', username = username))	
	cur = mysql.connection.cursor()
	cur.execute("SELECT plan FROM members WHERE username = %s", [username])
	plan = (cur.fetchone())['plan']
	cur.execute("SELECT exercise, reps, sets FROM plans WHERE name = %s", [plan])
	scheme = cur.fetchall()
	n = cur.execute("SELECT date, daily_result, rate FROM progress WHERE username = %s ORDER BY date DESC", [username])
	progress = cur.fetchall()
	result = []
	for i in range(n):
		result.append(int(progress[i]['rate']))
	if len(result) != 0: 
		good = result.count(1)
		average = result.count(2)
		poor = result.count(3)
		total = good + poor + average
	else:
		good = 0
		poor = 0
		average = 0
		total = 1
	good = round((good/total) * 100, 2)
	average = round((average/total) * 100, 2)
	poor = round((poor/total) * 100, 2)
	cur.close()
	return render_template('memberDash.html',user = username, plan = plan, scheme = scheme, progress = progress, good = good, poor = poor, average = average)