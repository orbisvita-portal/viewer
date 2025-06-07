

# app.py
from flask import Flask, render_template, request, redirect, session
import csv
import os

app = Flask(__name__)
app.secret_key = b'\xe9\xb2\x11\x91\xc2\xd5P\x91\xf6\xda\x95\x17~\xae\xd1\xa5\xc1\xecZ\x0f\xd0c\x8c\xf4'
  # 세션 암호화를 위한 키

# --- [1] CSV에서 사용자 및 메일 데이터 불러오기 ---
def load_accounts():
    accounts = {}
    with open("users.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts[row["id"]] = {
                "name": row["name"],
                "password": row["password"],
                "inbox": [],
                "sent": []
            }

    with open("inbox.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mail = {
                "from": row["from"].replace("<", "&lt;").replace(">", "&gt;"),
                "to": row["to"].replace("<", "&lt;").replace(">", "&gt;"),
                "subject": row["subject"],
                "date": row["date"],
                "body": row["body"].replace("\n", "<br>")
            }
            if row["id"] in accounts:
                accounts[row["id"]]["inbox"].append(mail)

    with open("sent.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mail = {
                "from": row["from"].replace("<", "&lt;").replace(">", "&gt;"),
                "to": row["to"].replace("<", "&lt;").replace(">", "&gt;"),
                "subject": row["subject"],
                "date": row["date"],
                "body": row["body"].replace("\n", "<br>")
            }
            if row["id"] in accounts:
                accounts[row["id"]]["sent"].append(mail)

    return accounts

# --- [2] 로그인 페이지 ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['userid']
        password = request.form['password']
        accounts = load_accounts()
        user = accounts.get(user_id)

        if user and user['password'] == password:
            session['user_id'] = user_id
            return redirect('/mail')
        else:
            return render_template('login.html', error='아이디 또는 비밀번호가 올바르지 않습니다.')

    return render_template('login.html', error='')

# --- [3] 메일 페이지 ---
@app.route('/mail')
def mail():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')

    accounts = load_accounts()
    user_data = accounts.get(user_id)
    if not user_data:
        return redirect('/')

    return render_template('mail.html', user=user_data, userid=user_id)

# --- [4] 로그아웃 ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # Render가 환경변수로 포트를 지정함
    app.run(host='0.0.0.0', port=port, debug=False)
