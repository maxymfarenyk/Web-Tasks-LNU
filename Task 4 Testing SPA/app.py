import requests
from flask import Flask, render_template, request, redirect, url_for, make_response
import jwt
import datetime
import hashlib
import sqlite3
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def generate_jwt(username, firstname, lastname, role):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Токен діє 1 годину
    token = jwt.encode({
        'username': username,
        'firstname': firstname,
        'lastname': lastname,
        'role': role,
        'exp': expiration_time
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_jwt(token):
    try:
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None  # Токен застарілий
    except jwt.InvalidTokenError:
        return None  # Невірний токен

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def check_password(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    stored_password = cursor.fetchone()
    conn.close()

    if stored_password:
        return stored_password[0] == hash_password(password)
    return False

def add_user(username, firstname, lastname, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, firstname, lastname, password, role) VALUES (?, ?, ?, ?, ?)",
                   (username, firstname, lastname, hash_password(password), 'user'))
    conn.commit()
    conn.close()

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        firstname TEXT NOT NULL,
        lastname TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            return 'Користувач з таким логіном вже існує'

        add_user(username, firstname, lastname, password)
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_password(username, password):
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT firstname, lastname, role FROM users WHERE username=?", (username,))
            firstname, lastname, role = cursor.fetchone()
            conn.close()

            token = generate_jwt(username, firstname, lastname, role)
            response = make_response(redirect(url_for('home')))
            response.set_cookie('token', token)
            return response
        else:
            return 'Невірний логін або пароль'

    return render_template('login.html')


@app.route('/')
def home():
    token = request.cookies.get('token')
    if token:
        decoded_token = decode_jwt(token)
        if decoded_token:
            username = decoded_token['username']
            role = decoded_token['role']
            return render_template('home.html', username=username, role=role)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    token = request.cookies.get('token')
    if token:
        decoded_token = decode_jwt(token)
        if decoded_token:
            return render_template('profile.html',
                                   username=decoded_token['username'],
                                   firstname=decoded_token['firstname'],
                                   lastname=decoded_token['lastname'],
                                   role=decoded_token['role'])
    return redirect(url_for('login'))

# Запит до Wikipedia API для пошуку статей за іменем
def get_wikipedia_articles(firstname):
    wiki_url = f'https://en.wikipedia.org/w/api.php?action=opensearch&search={firstname}&limit=10&namespace=0&format=json'
    response = requests.get(wiki_url)
    data = response.json()
    return data[1]


@app.route('/info')
def info():
    token = request.cookies.get('token')
    if token:
        decoded_token = decode_jwt(token)
        if decoded_token:
            firstname = decoded_token['firstname']
            articles = get_wikipedia_articles(firstname)
            return render_template('info.html', firstname=firstname, articles=articles)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('token')
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
