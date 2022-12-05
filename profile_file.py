from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt

class ChangePasswordForm(Form):
	old_password = PasswordField('Existing Password')
	new_password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords aren\'t matching pal!, check \'em')
	])
	confirm = PasswordField('Confirm Password')

class EditForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    street = StringField('Street', [validators.Length(min = 1, max = 100)])
    city = StringField('City', [validators.Length(min = 1, max = 100)])
    phone = StringField('Phone', [validators.Length(min = 1, max = 100)])

def update(username,mysql):
	form = ChangePasswordForm(request.form)
	if request.method == 'POST' and form.validate():
		new = form.new_password.data
		entered = form.old_password.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT password FROM info WHERE username = %s", [username])
		old = (cur.fetchone())['password']
		if sha256_crypt.verify(entered, old):
			cur.execute("UPDATE info SET password = %s WHERE username = %s", (sha256_crypt.encrypt(new), username))
			mysql.connection.commit()
			cur.close()
			flash('New password will be in effect from next login!!', 'info')
			return redirect(url_for('memberDash', username = session['username']))
		cur.close()
		flash('Old password you entered is wrong!!, try again', 'warning')
	return render_template('updatePassword.html', form = form)

def look_prof(username,mysql):
	if username == session['username'] or session['profile']==1 or session['profile']==2:
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM info WHERE username = %s", [username])
		result = cur.fetchone()
		return render_template('profile.html', result = result)
	flash('You cannot view other\'s profile', 'warning')
	if session['profile']==3:
		return redirect(url_for('trainorDash'))
	return redirect(url_for('memberDash', username = username))

def edit_prof(username,mysql):
	if username != session['username']:
		flash('You aren\'t authorised to edit other\'s details', 'warning')
		if session['profile']==4:
			return redirect(url_for('memberDash', username = username))
		if session['profile']==1:
			return redirect(url_for('adminDash'))
		if session['profile']==2:
			return redirect(url_for('recepDash', username = username))
		if session['profile']==3:
			return redirect(url_for('trainorDash', username = username))

	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM info WHERE username = %s", [username]);
	result = cur.fetchone()

	form = EditForm(request.form)
	
	form.name.data = result['name']
	form.street.data = result['street']
	form.city.data = result['city']
	form.phone.data = result['phone']

	cur.close()

	if request.method == 'POST' and form.validate():
		name = request.form['name']
		street = request.form['street']
		city = request.form['city']
		phone = request.form['phone']
		cur = mysql.connection.cursor()

		q = cur.execute("UPDATE info SET name = %s, street = %s, city = %s, phone = %s WHERE username = %s", (name, street, city, phone, username))
		mysql.connection.commit()
		cur.close()
		flash('You successfully updated your profile!!', 'success')
		if session['profile']==4:
			return redirect(url_for('memberDash', username = username))
		if session['profile']==1:
			return redirect(url_for('adminDash'))
		if session['profile']==2:
			return redirect(url_for('recepDash', username = username))
		if session['profile']==3:
			return redirect(url_for('trainorDash', username = username))
	return render_template('edit_profile.html', form=form)

