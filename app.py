from hack import app, create_db,db
from flask import render_template, redirect, url_for, send_file, request, abort
from flask_login import current_user, login_required, login_user, logout_user
from hack.forms import FileForm, LoginForm, RegForm
from hack.models import File, User
from werkzeug.security import check_password_hash
import os

app.config['UPLOAD_FOLDER'] = 'hack/static/uploads/'

create_db(app)

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    form = FileForm()
    if form.validate_on_submit():
        fname = form.file_name.data
        file = request.files['file']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
        new_file = File(file_name=fname, file=file_path, uploader=current_user.id)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        db.session.add(new_file)
        db.session.commit()
    return render_template('index.html', form=form)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            mess = 'Account already exists'
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('home'))

    if current_user.is_authenticated:
        return abort(404)
    return render_template('reg.html', form=form, mess=mess)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    mess=''
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            mess = 'Email not found'
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                mess = 'Incorrect password'
    if current_user.is_authenticated:
        return abort(404)

    return render_template('login.html', mess=mess, form=form)

@app.route('/view/<file_name>')
@login_required 
def view(file_name):
    file = File.query.filter_by(file_name=file_name).first()
    path_ = os.path.join(app.config['UPLOAD_FOLDER'], file.file_name)
    return send_file(path_)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/delete/<file_name>')
@login_required
def delete(file_name):
    file = File.query.filter_by(file_name=file_name).first()
    db.session.delete(file)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

