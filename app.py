import re
import bleach
import sqlite3
from flask import Flask, abort, render_template, request, redirect

app = Flask(__name__)

# Kara liste öğeleri
blacklist = ['onload', 'iframe', 'style', 'object', 'embed', 'link', 'onerror', 'img', 'OnFocus', 'AutoFocus', 'href', 'HREF']

allowed_tags = bleach.sanitizer.ALLOWED_TAGS
allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES

def get_db_connection():
    conn = sqlite3.connect('cybertime.db')
    conn.row_factory = sqlite3.Row
    return conn

def clean_query(query):
    # Sadece ilk <script> ve </script> etiketlerini kaldır, içerik kalsın
    query = re.sub(r'(?i)<\s*script\s*>', '', query, count=1)
    query = re.sub(r'(?i)<\s*/\s*script\s*>', '', query, count=1)
    
    # Remove 'script' within tags but keep the rest
    query = re.sub(r'(?i)<([^>]*)script([^>]*)>', r'<\1\2>', query, count=2)

    # Kara listedeki etiketleri kontrol et
    for tag in blacklist:
        if tag.lower() in query.lower():
            abort(400, description="403 Forbidden!")

    # HTML içeriğini temizle, sadece <script> kaldırıldı
    return query

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return render_template('search_results.html', query=query, results=[])

    query = clean_query(query)  # Sorguyu temizle

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE first_name LIKE ? OR last_name LIKE ?", ('%' + query + '%', '%' + query + '%'))
    
    results = cur.fetchall()
    conn.close()

    return render_template('search_results.html', query=query, results=results)

@app.route('/search', methods=['POST'])
def search_post():
    query = request.form.get('query')
    query = clean_query(query)  # Sorguyu temizle
    return redirect(f'/search?query={query}')

@app.route('/admin')
def admin():
    abort(403)

@app.route('/user')
def user():
    abort(500)

if __name__ == '__main__':
    app.run(debug=True)
