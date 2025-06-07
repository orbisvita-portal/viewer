import csv
import json
from collections import defaultdict

# 계정, 받은메일, 보낸메일 정보를 CSV에서 불러오기
accounts = {}

# 사용자 정보 불러오기
with open("C:/Users/USER/Desktop/users.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        accounts[row["id"]] = {
            "name": row["name"],
            "password": row["password"],
            "inbox": [],
            "sent": []
        }

# 받은 메일
with open("C:/Users/USER/Desktop/inbox.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        mail = {
            "from": row["from"].replace("<", "&lt;").replace(">", "&gt;"),
            "to": row["to"].replace("<", "&lt;").replace(">", "&gt;"),
            "subject": row["subject"],
            "date": row["date"],
            "body": row["body"].replace("\n", "<br>")
        }
        accounts[row["id"]]["inbox"].append(mail)

# 보낸 메일
with open("C:/Users/USER/Desktop/sent.csv", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        mail = {
            "from": row["from"].replace("<", "&lt;").replace(">", "&gt;"),
            "to": row["to"].replace("<", "&lt;").replace(">", "&gt;"),
            "subject": row["subject"],
            "date": row["date"],
            "body": row["body"].replace("\n", "<br>")
        }
        accounts[row["id"]]["sent"].append(mail)

# 이제 HTML 생성 코드에서 accounts 변수 사용 가능
with open("gmail_interface.html", "w", encoding="utf-8-sig") as f:
    f.write(f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>ORBIS VITA PORTAL</title>
  <script>
    const accounts = JSON.parse(`{json.dumps(accounts, ensure_ascii=False).replace('\\', '\\\\').replace('`', '\\`')}`);
  </script>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; }}
    #loginNotice {{
        max-width: 400px;
        margin: 200px auto 10px auto;
        text-align: center;
        background-color: #f2f2f2;
        color: #d93025;
        padding: 8px 12px;
        font-size: 14px;
        border-radius: 4px;
    }}
    #loginBox {{
      max-width: 400px; margin: 40px auto; padding: 20px;
      border: 1px solid #ccc; border-radius: 8px;
    }}
    input {{ width: 100%; padding: 8px; margin: 5px 0; }}
    button {{ padding: 8px 16px; width: 100%; margin-top: 10px; }}
    #app {{ display: none; height: 100vh; flex-direction: column; }}
    #topbar {{
        display: flex;
        justify-content: space-between; /* 좌/우 정렬 */
        align-items: center;
        background: #060b66;
        color: white;
        padding: 10px 20px;
        font-size: 18px;
        font-weight: bold;
        height: 50px;
        position: relative;
    }}

    #titleText {{
        flex-grow: 1;
    }}

    #usernameDisplay {{
        font-size: 18px;
        font-weight: bold;
        text-align: center; 
    }}

    #logoutBtn {{
        width: 100px;
        background: white;
        color: #060b66;
        border: none;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: bold;
        cursor: pointer;
    }}
    #messageBar {{
        background-color: #f2f2f2;    /* 밝은 회색 배경 */
        color: #d93025;               /* Gmail 스타일의 빨간 글씨 */
        font-weight: bold;
        padding: 8px 20px;
        font-size: 14px;
        text-align: center;
        border-bottom: 1px solid #ccc;  
    }}
    #main {{
      flex: 1; display: flex; overflow: hidden;
    }}
    #left {{
      width: 500px; min-width: 500px; max-width: 500px; border-right: 1px solid #ccc; display: flex; flex-direction: column;
    }}
    .mailbox {{
      flex: 1; overflow-y: auto; border-bottom: 1px solid #ccc;
    }}
    .mailbox-title {{
      background: #f2f2f2; padding: 10px; font-weight: bold;
      border-bottom: 1px solid #ddd;
    }}
    .mailListItem {{
      padding: 10px; border-bottom: 1px solid #eee; cursor: pointer;
    }}
    .mailListItem:hover {{ background: #f9f9f9; }}
    #right {{
      flex-grow: 1; padding: 20px; overflow-y: auto;
    }}
    .subject {{ font-weight: bold; }}
    .from, .to, .date {{ font-size: 12px; color: #666; }}
  </style>
</head>
<body>
  <div id="loginNotice">⚠️ 현재 인터넷이 연결되어 있지 않습니다.<br> 
            <b>7월 4일 17:00</b> 이전 수신/송신된 메일 확인만 가능합니다.</div>
  <div id="loginBox">
    <h2>메일 로그인</h2>
    <input type="text" id="userid" placeholder="아이디 입력">
    <input type="password" id="password" placeholder="비밀번호 입력">
    <button onclick="login()">확인</button>
    <p id="error" style="color: red;"></p>
  </div>

  <div id="app">
    <div id="topbar">ORVIS VITA POTAL - EMAIL CLIENT V4.0
        <span id="usernameDisplay"></span>
        <button id="logoutBtn" onclick="logout()">로그아웃</button>
    </div>
    <div id="messageBar">⚠️ 현재 인터넷이 연결되어 있지 않습니다. 오프라인 사본을 출력합니다.</div>
    <div id="main">
      <div id="left">
        <div class="mailbox">
          <div class="mailbox-title">📥 받은 편지함</div>
          <div id="inboxList"></div>
        </div>
        <div class="mailbox">
          <div class="mailbox-title">📤 보낸 편지함</div>
          <div id="sentList"></div>
        </div>
      </div>
      <div id="right">
        <p>메일 제목을 클릭하면 여기에 본문이 표시됩니다.</p>
      </div>
    </div>
  </div>

  <script>
    function createMailItem(mail, container) {{
      const item = document.createElement("div");
      item.className = "mailListItem";
      item.innerHTML = `
        <div class="subject">${{mail.subject}}</div>
        <div class="from">${{mail.from}}</div>
        <div class="date">${{mail.date}}</div>
      `;
      item.onclick = () => {{
        document.getElementById("right").innerHTML = `
          <h2>${{mail.subject}}</h2>
          <div><strong>보낸 사람:</strong> ${{mail.from}}</div>
          <div><strong>받은 사람:</strong> ${{mail.to}}</div>
          <div><strong>날짜:</strong> ${{mail.date}}</div>
          <hr>
          <p>${{mail.body}}</p>
        `;
      }};
      container.appendChild(item);
    }}

    function login() {{
      const id = document.getElementById("userid").value.trim();
      const pw = document.getElementById("password").value.trim();
      const error = document.getElementById("error");

      if (accounts[id] && accounts[id].password === pw) {{
        document.getElementById("loginBox").style.display = "none";
        document.getElementById("loginNotice").style.display = "none";
        document.getElementById("app").style.display = "flex";
        document.getElementById("usernameDisplay").textContent = accounts[id].name + "(" +id+  ") 님, 환영합니다.";

        const inboxList = document.getElementById("inboxList");
        const sentList = document.getElementById("sentList");
        inboxList.innerHTML = "";
        sentList.innerHTML = "";

        const inbox = accounts[id].inbox;
        const sent = accounts[id].sent;

        inbox.forEach(mail => createMailItem(mail, inboxList));
        sent.forEach(mail => createMailItem(mail, sentList));
      }} else {{
        error.textContent = "아이디 또는 비밀번호가 올바르지 않습니다.";
      }}
    }}

    function logout() {{
    // 로그인 창 다시 보이기
        document.getElementById("loginBox").style.display = "block";
        document.getElementById("loginNotice").style.display = "block";
        document.getElementById("app").style.display = "none";
    // 입력창 초기화 (선택사항)
        document.getElementById("userid").value = "";
        document.getElementById("password").value = "";
        document.getElementById("error").textContent = "";
    // 본문 초기화
        document.getElementById("usernameDisplay").textContent = "";
        document.getElementById("right").innerHTML = "<p>메일 제목을 클릭하면 여기에 본문이 표시됩니다.</p>";
}}
  </script>
</body>
</html>
""")