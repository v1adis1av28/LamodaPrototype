from flask import render_template, request, redirect, url_for

from eng import app
from models import db_session, User

from flask_login import login_required, login_user, logout_user


@app.route('/registration', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')
    login = request.form.get('username')
    password = request.form.get('password')
    user = User(login = login, password = password)
    db_session.add(user)
    db_session.commit()
    login_user(user)
    return render_template('registration.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        return redirect(url_for('register'))  # Исправлено на 'register'
    return response
