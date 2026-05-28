from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ---------------- OCR ENABLED ----------------
OCR_ENABLED = True

# ---------------- COMMON FIX DATA ----------------
COMMON_STEPS = [
    "Restart the program and try again",
    "Restart your PC (fixes temporary DLL/runtime issues)",
    "Run the program as Administrator",
    "Reinstall the application showing the error",
    "Check Windows Update and install latest updates"
]

COMMON_DLL_FIXES = [
    "Install Microsoft Visual C++ Redistributable (2015–2022)",
    "Install DirectX End-User Runtime",
    "Run 'sfc /scannow' in Command Prompt (repairs system files)"
]

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

# ---------------- HOME ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    text = ""
    solution = "Upload image to detect error"
    category = ""

    if request.method == "POST" and "image" in request.files:
        file = request.files.get("image")

        if file and file.filename != "":
            path = "temp.png"
            file.save(path)

            try:
                if OCR_ENABLED:
                    import pytesseract
                    from PIL import Image

                    img = Image.open(path)
                    text = pytesseract.image_to_string(img, config="--psm 6")

                    solution = f"""
🧾 Detected Text:
{text}

🛠 5 Basic Fixes:
1. {COMMON_STEPS[0]}
2. {COMMON_STEPS[1]}
3. {COMMON_STEPS[2]}
4. {COMMON_STEPS[3]}
5. {COMMON_STEPS[4]}

📦 Common DLL Fixes:
1. {COMMON_DLL_FIXES[0]}
2. {COMMON_DLL_FIXES[1]}
3. {COMMON_DLL_FIXES[2]}

💡 Tip:
If text is incorrect, upload a clearer or cropped screenshot of the error box.
"""

                else:
                    text = "OCR is turned off"
                    solution = "Enable OCR_ENABLED = True"

            except Exception as e:
                text = "OCR processing failed"
                solution = """
OCR error occurred.

Try:
1. Restart server
2. Check Tesseract installation
3. Upload clearer image
"""

                print("OCR ERROR:", e)

            finally:
                if os.path.exists(path):
                    os.remove(path)

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

# ---------------- CHECK TESSERACT ----------------
@app.route("/check")
def check():
    try:
        path = os.popen("which tesseract").read().strip()
        version = os.popen("tesseract --version").read().strip()

        if not path:
            return "Tesseract NOT FOUND in PATH"

        return f"""
Tesseract Path:
{path}

Tesseract Version:
{version}
"""

    except Exception as e:
        return f"Error checking tesseract: {str(e)}"

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)