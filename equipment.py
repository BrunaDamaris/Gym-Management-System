from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session

choices = []

class AddEquipForm(Form):
	name = StringField('Name', [validators.Length(min = 1, max = 100)])
	count = IntegerField('Count', [validators.NumberRange(min = 1, max = 25)])

class RemoveEquipForm(Form):
	name = RadioField('Name', choices = choices)
	count = IntegerField('Count', [validators.InputRequired()])

def add(mysql):
	form = AddEquipForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		count = form.count.data
		cur = mysql.connection.cursor()
		q = cur.execute("SELECT name FROM equip")
		equips = []
		b = cur.fetchall()
		for i in range(q):
			equips.append(b[i]['name'])
		if name in equips:
			cur.execute("UPDATE equip SET count = count+%s WHERE name = %s", (count, name))
		else:
			cur.execute("INSERT INTO equip(name, count) VALUES(%s, %s)", (name, count))
		mysql.connection.commit()
		cur.close()
		flash('You added a new Equipment!!', 'success')
		return redirect(url_for('adminDash'))
	return render_template('addEquip.html', form = form)

def delete(mysql):
	choices.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT name FROM equip")
	b = cur.fetchall()
	for i in range(q):
		tup = (b[i]['name'],b[i]['name'])
		choices.append(tup)
	form = RemoveEquipForm(request.form)
	if request.method == 'POST' and form.validate():
		cur.execute("SELECT * FROM equip WHERE name = %s", [form.name.data])
		data = cur.fetchone()
		num = data['count']
		if num >= form.count.data and form.count.data>0:
			name = form.name.data
			count = form.count.data
			cur = mysql.connection.cursor()
			cur.execute("UPDATE equip SET count = count-%s WHERE name = %s", (count, name))
			mysql.connection.commit()
			cur.close()
			choices.clear()
			flash('You successfully removed some of your equipment!!', 'success')
			return redirect(url_for('adminDash'))
		else:
			flash('you must enter valid number', 'danger')
	return render_template('removeEquip.html', form = form)
