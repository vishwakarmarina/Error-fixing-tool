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

# ---------------- ERROR DATABASE ----------------
error_database = {
    "vcruntime": "Install Visual C++ Redistributable",
    "msvcp": "Reinstall Visual C++ Redistributable",
    "d3dx": "Install DirectX Runtime",
    "dll": "Run SFC /scannow",
    "0xc000007b": "Install VC++ + DirectX"
}

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

                    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

                    img = Image.open(path)
                    text = pytesseract.image_to_string(img, config="--psm 6")

                    low = text.lower()

                    found = False
                    for k, v in error_database.items():
                        if k in low:
                            solution = v
                            category = k
                            found = True
                            break

                    if not found:
                        solution = "No known error detected"

                else:
                    text = "OCR is turned off"
                    solution = "Enable OCR_ENABLED = True"

            except Exception as e:
                text = "OCR processing failed"
                solution = "Server OCR error (check Tesseract installation)"
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

# ---------------- CHECK ROUTE ----------------
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