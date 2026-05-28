from flask import Flask, render_template, request, redirect
import pytesseract
from PIL import Image
import sqlite3
import os

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_feedback(t, m):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("INSERT INTO feedback (type, message) VALUES (?, ?)", (t, m))
    conn.commit()
    conn.close()

def get_feedback():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute("SELECT type, message FROM feedback ORDER BY id DESC")
    data = c.fetchall()
    conn.close()
    return data

# ---------------- ERROR DB ----------------
error_database = {
    "vcruntime": "Install Visual C++ Redistributable",
    "msvcp": "Reinstall Visual C++ Redistributable",
    "d3dx": "Install DirectX Runtime",
    "dll": "Run SFC /scannow",
    "0xc000007b": "Install VC++ + DirectX"
}

@app.route("/", methods=["GET", "POST"])
def home():

    text = ""
    solution = "Upload image to detect error"
    category = ""

    # IMAGE PROCESS
    if request.method == "POST" and "image" in request.files:
        file = request.files.get("image")

        if file and file.filename != "":
            path = "temp.png"
            file.save(path)

            img = Image.open(path)
            text = pytesseract.image_to_string(img, config="--psm 6")
            low = text.lower()

            for k, v in error_database.items():
                if k in low:
                    solution = v
                    category = k
                    break

            if os.path.exists(path):
                os.remove(path)

    # FEEDBACK SAVE
    if request.method == "POST" and "feedback_text" in request.form:
        save_feedback(
            request.form.get("feedback_type"),
            request.form.get("feedback_text")
        )
        return redirect("/")

    feedbacks = get_feedback()

    return render_template(
        "index.html",
        text=text,
        solution=solution,
        category=category,
        feedbacks=feedbacks
    )

if __name__ == "__main__":
    app.run(debug=True)