from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt
from datetime import datetime
from wtforms.fields.html5 import DateField

values = []
choices = []

class AddTrainorForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 100)])
	username = StringField('Username', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Senhas não são iguais')
	])
	confirm = PasswordField('Confirm Password')
	street = StringField('Street', [validators.Length(min = 1, max = 100)])
	city = StringField('City', [validators.Length(min = 1, max = 100)])
	prof = 3
	phone = StringField('Phone', [validators.Length(min = 1, max = 100)])

class trainorForm(Form):
	name = RadioField('Select Username', choices = choices)
	date = DateField('Date', format='%Y-%m-%d')
	report = StringField('Report', [validators.InputRequired()])
	rate = RadioField('Result', choices = [('good', 'good'),('average', 'average'),('poor', 'poor') ])

def add(mysql):
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM info")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['username'])
	cur.close()
	form = AddTrainorForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))
		street = form.street.data
		city = form.city.data
		prof = 2
		phone = form.phone.data

		cur = mysql.connection.cursor()

		cur.execute("INSERT INTO info(name, username, password, street, city, profile, phone) VALUES(%s, %s, %s, %s, %s, %s, %s)", (name, username, password, street, city, 3,phone))
		cur.execute("INSERT INTO trainors(username) VALUES(%s)", [username])
		mysql.connection.commit()
		cur.close()
		flash('You recruited a new Trainor!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('addTrainor.html', form=form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT username FROM trainors")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	form = delete.DeleteRecepForm(request.form)
	if len(choices)==1:
		flash('You cannot remove your only Trainor!!', 'danger')
		return redirect(url_for('adminDash'))
	if request.method == 'POST':
		username = form.username.data
		q = cur.execute("SELECT username FROM trainors WHERE username != %s", [username])
		b = cur.fetchall()
		new = b[0]['username']
		cur.execute("UPDATE members SET trainor = %s WHERE trainor = %s", (new, username))
		cur.execute("DELETE FROM trainors WHERE username = %s", [username])
		cur.execute("DELETE FROM info WHERE username = %s", [username])
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('You removed your Trainor!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('deleteRecep.html', form = form)

def openDash(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	cur.execute("SELECT name, count FROM equip")
	equips = cur.fetchall()
	cur.execute("SELECT username FROM members WHERE trainor = %s", [session['username']])
	members_under = cur.fetchall()
	cur.close()
	cur = mysql.connection.cursor()

	q = cur.execute("SELECT username FROM members WHERE trainor = %s", [session['username']])
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['username'],b[i]['username'])
		choices.append(tup)
	cur.close()

	form = trainorForm(request.form)

	if request.method == 'POST':
		date = form.date.data
		username = form.name.data
		report = form.report.data
		rate = form.rate.data
		if rate == 'good':
			rate = 1
		elif rate == 'average':
			rate = 2
		else:
			rate = 3
		if datetime.now().date()<date:
			flash('You cannot predict furture, buoy!!', 'warning')
			choices.clear()
			return redirect(url_for('trainorDash'))
		

		cur = mysql.connection.cursor()
		p = cur.execute("SELECT date FROM progress WHERE username = %s", [username])
		entered = []
		q = cur.fetchall()
		for i in range(p):
			entered.append(q[i]['date'])
		

		if date in entered:
			cur.execute("UPDATE progress SET daily_result = %s, rate = %s WHERE username = %s and date = %s", (report,rate, username, date))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('Succesfully updated!', 'success')
			return redirect(url_for('trainorDash'))
		

		cur.execute("INSERT INTO progress(username, date, daily_result, rate) VALUES(%s, %s, %s, %s)", (username, date, report, rate))
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Progress updated and Reported', 'info')
		return redirect(url_for('trainorDash'))

	return render_template('trainorDash.html', equips = equips, form = form, members = members_under)
