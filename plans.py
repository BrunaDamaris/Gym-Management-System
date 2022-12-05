from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField, SelectField, IntegerField
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging

class UpdatePlanForm(Form):
    name = StringField('Plan Name', [validators.Length(min=1, max=50)])
    exercise = StringField('Exercise', [validators.Length(min = 1, max = 100)])
    reps = IntegerField('Reps', [validators.NumberRange(min = 1, max = 20)])
    sets = IntegerField('Sets', [validators.NumberRange(min = 1, max = 20)])

def update(mysql):
	form = UpdatePlanForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		exercise = form.exercise.data
		reps = form.reps.data
		sets = form.sets.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT name, exercise FROM plans WHERE name = %s and exercise = %s", (name, exercise))
		result = cur.fetchall()
		if len(result)>0:
			cur.execute("UPDATE plans SET sets=%s, reps= %s WHERE name = %s and exercise = %s", (sets, reps, name, exercise))
		else:
			cur.execute("INSERT INTO plans(name, exercise, sets, reps) VALUES(%s, %s, %s, %s)", (name, exercise, sets, reps))
		mysql.connection.commit()
		cur.close()
		flash('You have updated the plan schemes', 'success')
		return redirect(url_for('trainorDash'))
	return render_template('addPlan.html', form = form)
