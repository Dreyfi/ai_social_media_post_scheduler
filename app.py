from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
from datetime import datetime
import requests
from openai import OpenAI

app = Flask(__name__)
scheduler = BackgroundScheduler()
scheduler.start()

client = OpenAI(
    api_key="__API_KEY__",
)

def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS posts
                        (id INTEGER PRIMARY KEY,
                         content TEXT NOT NULL,
                         post_time TEXT NOT NULL)''')

def post_to_social_media(content):
    print(f"Posting to social media: {content}")

def generate_content(prompt):

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful digital marketing assistant."},
            {"role": "user", "content": prompt},
        ],
        model="gpt-3.5-turbo",
    )

    return response.choices[0].message.content

@app.route('/', methods=['GET', 'POST'])
def home():
    suggested_content = None
    if request.method == 'POST':
        if 'generate' in request.form:
            prompt = request.form['prompt']
            suggested_content = generate_content(prompt)
        else:
            content = request.form['content']
            post_time = request.form['post_time']
            post_time = datetime.strptime(post_time, '%Y-%m-%dT%H:%M')
            with sqlite3.connect('database.db') as conn:
                conn.execute('INSERT INTO posts (content, post_time) VALUES (?, ?)', (content, post_time))
                scheduler.add_job(post_to_social_media, 'date', run_date=post_time, args=[content])
            return redirect(url_for('home'))
    
    with sqlite3.connect('database.db') as conn:
        posts = conn.execute('SELECT * FROM posts').fetchall()
    return render_template('index.html', posts=posts, suggested_content=suggested_content)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)