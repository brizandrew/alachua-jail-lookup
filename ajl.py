# coding: utf-8
from flask import Flask, render_template, redirect, url_for, request
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms.fields import StringField, SubmitField, IntegerField, RadioField, BooleanField, PasswordField, SelectField
from wtforms.fields.html5 import DateField, IntegerField
from wtforms.validators import Required, Optional, Email
from threading import Thread
import pymysql
import db
import ajlScraper

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GuhQK39XZ7Hl8BPw6MeydzaqVg'

bootstrap = Bootstrap(app)

class SearchForm(Form):
    searchString = StringField('Type search here...', validators=[Required()])
    submit = SubmitField('Submit')

class AdvancedSearchForm(Form):
    fname = StringField('First Name')
    lname = StringField('Last Name')
    bookingNumber = StringField('Booking Number')
    bookingDateMin = DateField('Booking Date',validators=[Optional()])
    bookingDateMax = DateField(validators=[Optional()])
    bondMin = IntegerField('Bond', validators=[Optional()])
    bondMax = IntegerField(validators=[Optional()])
    status = RadioField('Status', choices=[('Sentenced','Sentenced'),('Unsentenced','Unsentenced')], validators=[Optional()])
    agency = StringField('Agency')
    statute = StringField('Case Statute')
    description = StringField('Charges')
    level = RadioField('Level', choices=[('M','Misdemeanor'),('F','Felony')], validators=[Optional()])
    degree = StringField('Charge Degree')
    removed = BooleanField('Removed')
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')

class AlertForm(Form):
    attribute = SelectField('Attribute', choices=[('name', 'Name'), ('totalBond', 'Bond Amount'), ('description', 'Charge'), ('level', 'Level')])
    comparison = SelectField('Comparison', choices=[('>','>'),('<','<'),('in','Includes'), ('=', 'Exact Match')])
    value = StringField('Value')
    submit = SubmitField('Add')

class UserForm(Form):
    fname = StringField('First Name', validators=[Required()])
    lname = StringField('Last Name', validators=[Required()])
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    email = StringField('Email Address', validators=[Required(),Email()])
    permissions = SelectField('Permissions', choices=[('user','User'),('admin','Admin')], validators=[Required()])
    submit = SubmitField('Submit')

def convertAdvancedSearchFormToDict(form):
    return {
        'fname': form.fname.data,
        'lname': form.lname.data,
        'bookingNumber': form.bookingNumber.data,
        'bookingDateMin': form.bookingDateMin.data,
        'bookingDateMax': form.bookingDateMax.data,
        'bondMin': form.bondMin.data,
        'bondMax': form.bondMax.data,
        'status': form.status.data,
        'agency': form.agency.data,
        'statute': form.statute.data,
        'description': form.description.data,
        'level': form.level.data,
        'degree': form.degree.data,
        'removed': form.removed.data
    }

def scrapeJailSite(app):
    with app.app_context():
        ajlScraper.scrapeJailSite()

def newDBThread():
    thr = Thread(target=scrapeJailSite, args=[app])
    thr.start()
    return thr

@app.route('/', methods=['GET', 'POST'])
def index():
    searchString = None
    searchResults = None
    searchSubmitted = False
    form = SearchForm()
    if form.validate_on_submit():
        searchString = form.searchString.data
        searchResults = db.searchDB(searchString, 'simple')
        form.searchString.data = ''
        searchSubmitted = True
    return render_template('index.html', form=form, page='home', searchResults=searchResults,searchSubmitted=searchSubmitted)

@app.route('/inmates/')
def inmates():
    return redirect(url_for('index'))

@app.route('/inmates/<bookingNumber>')
def inmate(bookingNumber):
    inmate = db.getSingleInmateData(bookingNumber)
    return render_template('inmate.html', inmate=inmate, page='all-inmates')

@app.route('/all-inmates')
def allInmates():
    inmates = db.getAllInmateData(True)
    return render_template('all-inmates.html', inmates=inmates, page='all-inmates')

@app.route('/changelog')
def changelog():
    changelog = db.getChanges()
    return render_template('changelog.html', changelog=changelog, page='changelog')

@app.route('/advanced-search', methods=['GET', 'POST'])
def advancedSearch():
    searchResults = None
    searchSubmitted = False
    form = AdvancedSearchForm()
    if form.validate_on_submit():
        searchResults = db.searchDB(convertAdvancedSearchFormToDict(form), 'advanced')
        searchSubmitted = True
    return render_template('advanced-search.html', form=form, page='advanced-search', searchResults=searchResults,searchSubmitted=searchSubmitted)

@app.route('/login', methods=['GET', 'POST'])
def login():
    userInfo = None
    alerts = None
    allUsers = None
    invalidPassword = False

    loginForm = LoginForm()
    alertForm = AlertForm()
    userForm = UserForm()

    if loginForm.validate_on_submit():
        if db.authenticateUser(loginForm.username.data, loginForm.password.data):
            userInfo = db.getUserData(loginForm.username.data)
            alerts = db.getAllAlerts(loginForm.username.data)
            allUsers = db.getAllUsers()
            userForm.username.data = ''
            if alertForm.validate_on_submit():
                db.addAlert(loginForm.username.data, alertForm.attribute.data, alertForm.comparison.data, alertForm.value.data)
        else:
            invalidPassword = True

    return render_template('login.html', page='login', loginForm=loginForm, alertForm=alertForm, userForm=userForm, invalidPassword=invalidPassword, userInfo=userInfo, alerts=alerts, allUsers=allUsers)

@app.route('/addAlert', methods=['POST'])
def addAlert():
    db.addAlert(request.form['username'], request.form['attribute'], request.form['comparison'], request.form['value'] )
    return redirect(url_for('index'))

@app.route('/deleteAlert', methods=['POST'])
def deleteAlert():
    db.deleteAlert(request.form['uniqueKey'])
    return redirect(url_for('index'))

@app.route('/addUser', methods=['POST'])
def addUser():
    db.addUser(request.form['username'], request.form['password'], request.form['fname'], request.form['lname'],request.form['email'], request.form['permissions'])
    return redirect(url_for('index'))

@app.route('/updateDB', methods=['POST'])
def updateDB():
    newDBThread()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.errorhandler(405)
def internal_server_error(e):
    return render_template('405.html'), 405

if __name__ == '__main__':
    # ajlScraper.newScrapeThread()
    app.run(debug=True)
