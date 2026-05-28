from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

# ---------------- OCR ENABLED ----------------
OCR_ENABLED = True

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

# ---------------- FIX TEMPLATES ----------------
def build_solution():
    return """
🛠 DLL ERROR FIX GUIDE

🔹 STEP 1: Basic Fixes
1. Restart the program
2. Restart your PC
3. Run the program as Administrator
4. Reinstall the application
5. Update Windows

🔹 STEP 2: DLL Fix (Most Important)
1. Install Microsoft Visual C++ Redistributable (2015–2022)
2. Install DirectX End-User Runtime
3. Run System File Checker:
   → Open CMD as Admin
   → Type: sfc /scannow

🔹 STEP 3: Advanced Fixes
1. Update graphics drivers
2. Reinstall affected software completely
3. Install latest Windows updates

💡 NOTE:
If error still exists, reinstall the program cleanly and restart system.
"""

# ---------------- HOME ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    text = ""
    solution = "Upload screenshot to analyze error"
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

                    # OCR ONLY FOR INTERNAL USE (NOT SHOWN TO USER)
                    text = pytesseract.image_to_string(img, config="--psm 6")

                    # ALWAYS SHOW CLEAN OUTPUT ONLY
                    solution = build_solution()
                    category = "dll_error"

                else:
                    solution = "OCR is disabled. Enable OCR_ENABLED = True"

            except Exception as e:
                solution = """
🛠 ERROR PROCESSING IMAGE

Try:
1. Restart server
2. Upload clearer screenshot
3. Check Tesseract installation
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

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)