
from flask import Flask, request, jsonify, session, render_template_string
import sqlite3
import random
import uuid
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "friendship-secret-change-later")
app.permanent_session_lifetime = 60 * 60 * 24 * 365

DB = "friendship.db"

# 1200 unique message combinations
openings = [
    "A little reminder for you:",
    "Hey, beautiful soul!",
    "Dear wonderful friend,",
    "Just for you:",
    "I hope you remember this:",
    "Here's something you should know:",
    "Sending you happiness:",
    "One thing I want you to remember:",
    "A special thought for today:",
    "Before you continue your day,"
]

feelings = [
    "you deserve happiness, love, and beautiful memories.",
    "your smile makes ordinary days special.",
    "you are stronger than you sometimes believe.",
    "your presence makes the world brighter.",
    "you deserve people who appreciate your heart.",
    "never let a difficult day make you forget your worth.",
    "beautiful things are waiting for you.",
    "your dreams are worth fighting for.",
    "you should be proud of how far you have come.",
    "you are enough, exactly as you are.",
    "your kindness is something truly special.",
    "even small steps can lead to wonderful things."
]

endings = [
    "Keep smiling. You deserve it. ❤️",
    "Never forget how special you are. 💗",
    "I'm always wishing you the best. 🌸",
    "Keep shining, beautiful soul. ✨",
    "You deserve all the good things in life. 🦋",
    "Take care of yourself and stay happy. 💕",
    "Believe in yourself, always. 🌷",
    "Sending you a big virtual hug. 🤗",
    "May your days be filled with happiness. 🌈",
    "And remember, you matter. ❤️"
]

messages = [
    f"{opening} {feeling} {ending}"
    for opening in openings
    for feeling in feelings
    for ending in endings
]


def connect_db():
    return sqlite3.connect(DB)


def setup_database():
    con = connect_db()

    con.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            visitor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            opened_count INTEGER DEFAULT 0,
            cycle INTEGER DEFAULT 0
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS opened_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            visitor_id TEXT NOT NULL,
            cycle INTEGER NOT NULL,
            message_id INTEGER NOT NULL
        )
    """)

    con.commit()
    con.close()


setup_database()


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>FRIENDSHIP ❤️</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #ffb6c1, #e6b8ff, #ffcce0);
}

.container {
    width: 100%;
    max-width: 440px;
    padding: 30px 22px;
    background: rgba(255,255,255,0.95);
    border-radius: 28px;
    text-align: center;
    box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.heart {
    font-size: 55px;
    animation: beat 1s infinite;
}

@keyframes beat {
    50% { transform: scale(1.15); }
}

h1 {
    color: #e75480;
    font-size: 34px;
    letter-spacing: 3px;
    margin-bottom: 8px;
}

.subtitle {
    color: #999;
    line-height: 1.6;
}

input {
    width: 100%;
    padding: 15px;
    border: 1px solid #ffc5dc;
    border-radius: 15px;
    margin: 15px 0;
    font-size: 16px;
    text-align: center;
    outline: none;
}

button {
    width: 100%;
    padding: 16px;
    border: none;
    border-radius: 30px;
    background: linear-gradient(90deg, #ff69a4, #d66bff);
    color: white;
    font-size: 17px;
    font-weight: bold;
    cursor: pointer;
}

button:active {
    transform: scale(0.97);
}

.counter {
    background: #fff0f5;
    border-radius: 20px;
    padding: 18px;
    margin: 20px 0;
}

.counter h3 {
    color: #d94f85;
}

.number {
    color: #e75480;
    font-size: 38px;
    font-weight: bold;
}

.message {
    min-height: 155px;
    padding: 24px 17px;
    margin: 18px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    border: 1px solid #ffd1e4;
    background: #fff0f7;
    color: #b83c70;
    font-size: 18px;
    line-height: 1.9;
    transition: opacity .3s;
}

.hidden {
    display: none;
}

.small {
    color: #999;
    font-size: 12px;
    line-height: 1.6;
}

.footer {
    color: #aaa;
    margin-top: 25px;
    font-size: 13px;
}

#error {
    color: #d33;
    font-size: 14px;
}
</style>
</head>

<body>

<div class="container">

    <div class="heart">❤️</div>

    <h1>FRIENDSHIP</h1>

    <p class="subtitle">
        A little place filled with beautiful feelings.
    </p>

    <section id="welcome">
        <h3 style="color:#d94f85;">Welcome, beautiful soul 💗</h3>

        <p class="subtitle">
            Before we begin, what should we call you?
        </p>

        <input
            id="name"
            type="text"
            maxlength="50"
            placeholder="Enter your name..."
        >

        <button onclick="startJourney()">
            Continue ❤️
        </button>

        <p id="error"></p>
    </section>

    <section id="main" class="hidden">

        <h2 id="greeting" style="color:#d94f85;"></h2>

        <div class="counter">
            <h3>Our Journey Started On</h3>
            <div class="number" id="days">0</div>
            <p class="subtitle">Days of beautiful memories ❤️</p>
        </div>

        <div class="counter">
            <h3>Messages Opened 💌</h3>
            <div class="number" id="opened">0</div>
            <p class="subtitle">Every message is a little surprise.</p>
        </div>

        <h3 style="color:#d94f85;">A Special Message For You 💌</h3>

        <div class="message" id="message">
            Your surprise is waiting here.
            Press the button to open it. ❤️
        </div>

        <button id="messageButton" onclick="newMessage()">
            Open Your Message 💌
        </button>

        <p class="small">
            Your message-open count is saved so you can keep your progress.
        </p>

    </section>

    <div class="footer">
        Made with love ❤️ | FRIENDSHIP
    </div>

</div>

<script>

async function loadState() {
    const response = await fetch("/api/state");
    const data = await response.json();

    if (data.started) {
        showMain(data.name, data.opened_count);
    }
}

function showMain(name, count) {
    document.getElementById("welcome").classList.add("hidden");
    document.getElementById("main").classList.remove("hidden");

    document.getElementById("greeting").textContent =
        "Hello, " + name + " ❤️";

    document.getElementById("opened").textContent = count;

    updateDays();
}

async function startJourney() {
    const name = document.getElementById("name").value.trim();

    if (!name) {
        document.getElementById("error").textContent =
            "Please enter your name first.";
        return;
    }

    const response = await fetch("/api/start", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name: name})
    });

    const data = await response.json();

    if (!response.ok) {
        document.getElementById("error").textContent =
            data.error || "Something went wrong.";
        return;
    }

    showMain(data.name, data.opened_count);
}

function updateDays() {
    const startDate = new Date(2023, 8, 7);
    const today = new Date();

    const difference = today - startDate;

    const days = Math.max(
        0,
        Math.floor(difference / 86400000)
    );

    document.getElementById("days").textContent = days;
}

async function newMessage() {
    const button = document.getElementById("messageButton");
    const box = document.getElementById("message");

    button.disabled = true;
    button.textContent = "Opening your message...";

    try {
        const response = await fetch("/api/message", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to open message.");
        }

        box.style.opacity = 0;

        setTimeout(() => {
            box.textContent = data.message;
            box.style.opacity = 1;

            document.getElementById("opened").textContent =
                data.opened_count;
        }, 250);

    } catch (error) {
        box.textContent = error.message;
    }

    button.disabled = false;
    button.textContent = "Open Your Message 💌";
}

loadState();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/api/state")
def state():
    visitor_id = session.get("visitor_id")

    if not visitor_id:
        return jsonify({"started": False})

    con = connect_db()

    row = con.execute(
        "SELECT name, opened_count FROM visitors WHERE visitor_id = ?",
        (visitor_id,)
    ).fetchone()

    con.close()

    if not row:
        return jsonify({"started": False})

    return jsonify({
        "started": True,
        "name": row[0],
        "opened_count": row[1]
    })


@app.route("/api/start", methods=["POST"])
def start():
    data = request.get_json() or {}
    name = str(data.get("name", "")).strip()[:50]

    if not name:
        return jsonify({"error": "Please enter your name."}), 400

    visitor_id = session.get("visitor_id") or str(uuid.uuid4())

    session.permanent = True
    session["visitor_id"] = visitor_id

    con = connect_db()

    con.execute("""
        INSERT INTO visitors (visitor_id, name)
        VALUES (?, ?)
        ON CONFLICT(visitor_id)
        DO UPDATE SET name = excluded.name
    """, (visitor_id, name))

    con.commit()

    row = con.execute(
        "SELECT opened_count FROM visitors WHERE visitor_id = ?",
        (visitor_id,)
    ).fetchone()

    con.close()

    return jsonify({
        "name": name,
        "opened_count": row[0]
    })


@app.route("/api/message", methods=["POST"])
def message():
    visitor_id = session.get("visitor_id")

    if not visitor_id:
        return jsonify({"error": "Please enter your name first."}), 403

    con = connect_db()

    con.execute("BEGIN IMMEDIATE")

    visitor = con.execute(
        "SELECT cycle, opened_count FROM visitors WHERE visitor_id = ?",
        (visitor_id,)
    ).fetchone()

    if not visitor:
        con.close()
        return jsonify({"error": "Please start again."}), 403

    cycle, opened_count = visitor

    seen = con.execute(
        """
        SELECT message_id FROM opened_messages
        WHERE visitor_id = ? AND cycle = ?
        """,
        (visitor_id, cycle)
    ).fetchall()

    seen_ids = {row[0] for row in seen}

    remaining = [
        i for i in range(len(messages))
        if i not in seen_ids
    ]

    if not remaining:
        cycle += 1
        con.execute(
            "UPDATE visitors SET cycle = ? WHERE visitor_id = ?",
            (cycle, visitor_id)
        )
        remaining = list(range(len(messages)))

    message_id = random.choice(remaining)

    con.execute(
        """
        INSERT INTO opened_messages
        (visitor_id, cycle, message_id)
        VALUES (?, ?, ?)
        """,
        (visitor_id, cycle, message_id)
    )

    opened_count += 1

    con.execute(
        "UPDATE visitors SET opened_count = ? WHERE visitor_id = ?",
        (opened_count, visitor_id)
    )

    con.commit()
    con.close()

    return jsonify({
        "message": messages[message_id],
        "opened_count": opened_count
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
