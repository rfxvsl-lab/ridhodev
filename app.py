from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

app = Flask(__name__)

# --- BOT AUTO CONVERTER GOOGLE DRIVE ---
def convert_gdrive_link(url):
    # Jika link mengandung /file/d/ (Link Share biasa)
    match1 = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
    if match1:
        return f"https://drive.google.com/uc?export=view&id={match1.group(1)}"
    
    # Jika link mengandung ?id=
    match2 = re.search(r'[?&]id=([a-zA-Z0-9_-]+)', url)
    if match2 and "uc?export=view" not in url:
        return f"https://drive.google.com/uc?export=view&id={match2.group(1)}"
        
    return url # Kalau bukan link GDrive, kembalikan apa adanya

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
    
    c.execute("SELECT COUNT(*) FROM projects")
    if c.fetchone()[0] == 0:
        # Data awal sekarang menggunakan Link Gambar, bukan Ikon FontAwesome
        data_awal = [
            ('Vorvox.id', 'Pengembangan company profile dan katalog digital elegan untuk perusahaan konveksi.', 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600', 'Web Dev', 'fa-brands fa-html5', 'amber'),
            ('Arus Digital', 'Portofolio layanan live streaming event dengan visual yang responsif dan imersif.', 'https://images.unsplash.com/photo-1598550880863-4e8aa3d0edb4?w=600', 'Broadcasting', 'fa-solid fa-satellite-dish', 'rose'),
            ('Wedding SaaS', 'Platform undangan digital dengan fitur dashboard builder dan manajemen template.', 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600', 'Laravel', 'fa-brands fa-laravel', 'teal'),
            ('RFX Femmora', 'Integrasi layanan kreatif (RFX Visual) dengan sistem reseller premium.', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600', 'Integration', 'fa-solid fa-network-wired', 'amber'),
            ('Expo Campuss 2026', 'Produksi video animasi promosi untuk memeriahkan acara pameran kampus sekolah.', 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=600', 'Motion Graphics', 'fa-solid fa-clapperboard', 'rose')
        ]
        c.executemany("INSERT INTO projects (title, description, icon, category, category_icon, color) VALUES (?, ?, ?, ?, ?, ?)", data_awal)
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    karya_karya = conn.execute("SELECT * FROM projects ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', projects=karya_karya)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        icon_raw = request.form['icon'] 
        
        # PROSES CONVERTER BOT BERJALAN DI SINI
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

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)