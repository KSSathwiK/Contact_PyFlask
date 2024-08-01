from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('DBEndpoint')
app.config['MYSQL_USER'] = os.getenv('DBUser')
app.config['MYSQL_PASSWORD'] = os.getenv('DBPassword')
app.config['MYSQL_DB'] = os.getenv('DBName')

mysql = MySQL(app)

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM contacts WHERE user=%s", (username,))
        contacts = cur.fetchall()
        return render_template('index.html', username=username, contacts=contacts)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if 'username' in session:
        username = session['username']
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contacts (user, name, phone, email) VALUES (%s, %s, %s, %s)", (username, name, phone, email))
        mysql.connection.commit()
        
        return redirect(url_for('index'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
