from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, session, flash, url_for
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

@app.route('/register', methods = ['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        new_user = User.register(username, password, first_name, last_name, email)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash('New User Created')
        return redirect(url_for('handle_login',username=username))
    
    return render_template('register.html', form=form)

@app.route('/users/<username>')
def handle_login(username):
    user = User.query.get_or_404(username)

    if "username" not in session:
        flash("please login")
        return redirect('/login')

    # if session['username'] = username:
    return render_template('profile.html', user=user)
    # else:
    #     flash("invalid user")

@app.route('/login', methods = ['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username,password)

        if user:
            flash(f"welcome back {user.username}")
            session['username'] = user.username
            return redirect(url_for('handle_login',username=username))
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    flash('you have logged out')
    session.pop('username')
    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods = ['GET', 'POST'])
def add_feedback(username):
    user = User.query.get_or_404(username)
    form = FeedbackForm()

    if "username" not in session:
        flash("please login")
        return redirect('/login')

    if form.validate_on_submit():
        if user.username == session['username']:
            title = form.title.data
            content = form.content.data
            new_feedback = Feedback(title = title, content = content, username = session['username'])
            db.session.add(new_feedback)
            db.session.commit()
            flash("feedback created!")
            return redirect(url_for('handle_login',username=username))
        if user.username != session['username']:
            flash('you cannot add feedback as this user')
            return redirect(url_for('handle_login',username=username))
    return render_template('add-feedback.html', form = form)

@app.route('/feedback/<int:feedbackid>/update', methods = ['GET', 'POST'])
def edit_feedback(feedbackid):
    form = FeedbackForm()
    feedback = Feedback.query.get_or_404(feedbackid)
    if "username" not in session:
        flash("please login")
        return redirect('/login')

    if form.validate_on_submit():
        if feedback.user.username == session['username']:
            title = form.title.data
            content = form.content.data
            feedback.title = title
            feedback.content = content
            db.session.commit()
            return redirect(url_for('handle_login',username=feedback.user.username))
    return render_template("edit-feedback.html", form=form, feedback=feedback)

@app.route('/users/<username>/delete', methods = ['POST','GET'])
def delete_user(username):
    user = User.query.get_or_404(username)
    if "username" not in session:
        flash("please login")
        return redirect('/login')
    for feedback in user.feedbacks:
        if feedback.user.username == session['username']:
            db.session.delete(feedback)
            db.session.commit()
    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash('your account has been deleted')
    elif user.username != session['username']:
        flash('you cannot delete another user acct')
    return redirect('/register')

@app.route('/feedback/<int:feedbackid>/delete', methods = ['POST','GET'])
def delete_feedback(feedbackid):
    feedback = Feedback.query.get_or_404(feedbackid)
    if feedback.user.username == session['username']:
            db.session.delete(feedback)
            db.session.commit()
            return redirect(url_for('handle_login',username=feedback.user.username))
    if feedback.user.username != session['username']:
        flash('you cannot delete this feedback')
        return redirect(url_for('handle_login',username=feedback.user.username))













