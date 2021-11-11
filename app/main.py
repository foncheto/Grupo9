from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'

import gspread
from oauth2client.service_account import ServiceAccountCredentials

credential = ServiceAccountCredentials.from_json_keyfile_name("credentials.json",
                                                              ["https://spreadsheets.google.com/feeds",                                                               "https://www.googleapis.com/auth/spreadsheets",                                                        "https://www.googleapis.com/auth/drive.file",                                                        "https://www.googleapis.com/auth/drive"])

client = gspread.authorize(credential)
users_gs = client.open_by_key('19sh4ifgoU1OCiv8-wU9wqLEgsoo8ZPHTF3mmTLgJXMU').sheet1
contact_gs = client.open_by_key('1W7bJiuMZLA0HzXVW_ImYj_E1kIm9YmqpCsvsD5S2tRA').sheet1
cont_r = 0
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/excel')
def excel():
    return jsonify(users_gs.get_all_records())

@app.route('/nosotros')
def team():
    return render_template('nosotros.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/ingresar')
def signin():
    return render_template('sign-in.html')

@app.route('/registrarme')
def signup():
    return render_template('sign-up.html')  
@app.route('/registrar', methods=['POST'])
def register():
    users = users_gs.get_all_records()
    if request.form['pass'] != request.form['cpass']:
        flash('Claves distintas')
        return redirect('/registrarme')
    for user in users:
        if user['email'] == request.form['email']:
            flash('Este email ya tiene una cuenta con nosotros. Prueba iniciando sesión')
            return redirect("/registrarme") 
    
    new_id = (users[0]['id']+1)
    row = [new_id,request.form['name'],request.form['email'],request.form['pass'],0]
    users_gs.insert_row(row,2)

    session['id'] = new_id
    session['name'] = request.form['name']
    session['active'] = True
    return redirect('/panel')
    
    
@app.route('/contactar', methods=['POST'])
def contact():
    contact = contact_gs.get_all_records()
    new_id = (contact[0]['id']+1)
    row = [new_id,request.form['name'],request.form['email'],request.form['asunto'],request.form['message']]
    contact_gs.insert_row(row,2)
    flash('Mensaje enviado con exito')
    return redirect('/contacto')

@app.route('/informate')
def informate():
    return render_template('info.html')
@app.route('/informate/localizador')
def localizador():
    return render_template('localizador.html')
@app.route('/panel/crear')
def crear():
    if 'active' in session:
        return render_template('crear.html')
    return redirect('/')
@app.route('/panel')
def dashboard():
    if 'active' in session:
        users = users_gs.get_all_records()
        return render_template('dashboard.html', users = users)
    return redirect('/')
@app.route('/profile')
def profile():
    if 'active' in session:
        return render_template('profile.html')
    return redirect('/')

@app.route('/check-user', methods=['POST'])
def create_user():
    users = users_gs.get_all_records()
    for user in users:
        if user['email'] == request.form['email'] and user['password'] == request.form['pass']:
            session['id'] = user['id']
            session['name'] = user['name']
            session['progress'] = user['progress']
            session['active'] = True
            return redirect('/panel')
    flash('Error en Email o Clave')
    return redirect("/ingresar")

@app.route('/salir')
def logout():
    session.clear()
    return redirect('/')