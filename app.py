from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

def db():
    conn = sqlite3.connect('game.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, coins INTEGER DEFAULT 0, best_score INTEGER DEFAULT 0, level INTEGER DEFAULT 1, referred_by TEXT)')
    return conn

db().commit()

@app.route('/')
def game():
    return render_template('index.html')

@app.route('/api/user', methods=['POST'])
def user():
    d = request.json
    uid = d.get('user_id')
    username = d.get('username', 'Player')
    ref = d.get('referred_by')
    conn = db(); cur = conn.cursor()
    cur.execute('SELECT coins, best_score, level FROM users WHERE user_id=?', (uid,))
    row = cur.fetchone()
    if not row:
        cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?)', (uid, username, 100, 0, 1, ref))
        if ref and ref != uid:
            cur.execute('UPDATE users SET coins = coins + 50 WHERE user_id=?', (ref,))
        conn.commit(); coins, best, level = 100, 0, 1
    else:
        coins, best, level = row
    conn.close()
    return jsonify({'coins': coins, 'best_score': best, 'level': level})

@app.route('/api/save', methods=['POST'])
def save():
    d = request.json
    uid = d.get('user_id'); coins = d.get('coins', 0); score = d.get('score', 0); level = d.get('level', 1)
    conn = db()
    conn.execute('UPDATE users SET coins=?, best_score=MAX(best_score,?), level=? WHERE user_id=?', (coins, score, level, uid))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/leaderboard')
def leaderboard():
    conn = db()
    rows = conn.execute('SELECT username, best_score, coins FROM users ORDER BY best_score DESC LIMIT 10').fetchall()
    conn.close()
    return jsonify([{'name': r[0], 'score': r[1], 'coins': r[2]} for r in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
