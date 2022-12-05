from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from passlib.hash import sha256_crypt
from datetime import datetime
from wtforms.fields.html5 import DateField

values = []
choices = []

class AddTrainorForm(Form):
	name = StringField('Nome', [validators.Length(min = 1, max = 100)])
	username = StringField('Nome de Usuário', [validators.InputRequired(), validators.NoneOf(values = values, message = "Username already taken, Please try another")])
	password = PasswordField('Senha', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'As senhas informadas não coincidem')
	])
	confirm = PasswordField('Confirmar senha')
	street = StringField('Endereço', [validators.Length(min = 1, max = 100)])
	city = StringField('Cidade', [validators.Length(min = 1, max = 100)])
	prof = 3
	phone = StringField('Número de Telefone', [validators.Length(min = 1, max = 100)])

class trainorForm(Form):
	name = RadioField('Selecionar nome de usuário', choices = choices)
	date = DateField('Data', format='%Y-%m-%d')
	report = StringField('Relatório', [validators.InputRequired()])
	rate = RadioField('Resultado', choices = [('bom', 'bom'),('médio', 'médio'),('baixo', 'baixo') ])

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
		flash('Novo treinador adicinado', 'success')
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
		flash('Treinador não pode ser removido(a) porque é único(a)', 'danger')
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
		flash('Treinador removido(a)', 'success')
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
			flash('Data inválida', 'warning')
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
			flash('Atualizado com sucesso', 'success')
			return redirect(url_for('trainorDash'))
		

		cur.execute("INSERT INTO progress(username, date, daily_result, rate) VALUES(%s, %s, %s, %s)", (username, date, report, rate))
		mysql.connection.commit()
		cur.close()
		choices.clear()
		flash('Progresso atualizado e relatado', 'info')
		return redirect(url_for('trainorDash'))

	return render_template('trainorDash.html', equips = equips, form = form, members = members_under)
