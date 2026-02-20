from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re

app = Flask(__name__)
# KUNCI RAHASIA UNTUK KEAMANAN SESSION (Jangan dikasih tahu siapa-siapa)
app.secret_key = 'arusdigital_rahasia_banget_2026'

# --- BOT AUTO CONVERTER GOOGLE DRIVE ---
def convert_gdrive_link(url):
    match1 = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match1:
        return f"https://drive.google.com/uc?export=view&id={match1.group(1)}"
    match2 = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if match2 and "uc?export=view" not in url:
        return f"https://drive.google.com/uc?export=view&id={match2.group(1)}"
    return url

def get_db_connection():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  icon TEXT,
                  category TEXT,
                  category_icon TEXT,
                  color TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- HALAMAN UTAMA ---
@app.route('/')
def home():
    conn = get_db_connection()
    karya_karya = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', projects=karya_karya)

# --- HALAMAN LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Kalau sudah login, langsung lempar ke admin
    if session.get('logged_in'):
        return redirect(url_for('admin'))
        
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # GANTI USERNAME DAN PASSWORD KAMU DI SINI
        if username == 'admin' and password == 'ridho2026':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Username atau Password salah bos!'
            
    return render_template('login.html', error=error)

# --- FUNGSI LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# --- HALAMAN ADMIN (DILINDUNGI) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # CEK KEAMANAN: Kalau belum login, tendang ke halaman login!
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        icon_raw = request.form['icon'] 
        icon_converted = convert_gdrive_link(icon_raw)
        category = request.form['category']
        category_icon = request.form['category_icon']
        color = request.form['color']
        
        conn.execute('INSERT INTO projects (title, description, icon, category, category_icon, color) VALUES (?, ?, ?, ?, ?, ?)',
                     (title, description, icon_converted, category, category_icon, color))
        conn.commit()
        return redirect(url_for('admin'))
    
    karya_karya = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('admin.html', projects=karya_karya)

# --- FITUR HAPUS (DILINDUNGI) ---
@app.route('/delete/<int:id>')
def delete(id):
    # CEK KEAMANAN: Tendang kalau belum login
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)