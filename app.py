import sqlite3
import os
from flask import Flask, request, render_template, redirect

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


# ---------------- FIX BOX BUILDER ----------------
def build_fix_box():
    basic_fixes = [
        ("Restart the Program",             "Close the application completely and relaunch it."),
        ("Restart Your PC",                 "Clears temporary DLL / runtime errors held in memory."),
        ("Run as Administrator",            "Right-click the app icon and choose <b>Run as Administrator</b>."),
        ("Install Visual C++ Redistributable",
         "Download and install <b>Microsoft Visual C++ 2015–2022</b> from the official Microsoft website."),
        ("Install DirectX Runtime",
         "Download and install <b>DirectX End-User Runtime</b> from the Microsoft Download Center."),
    ]

    advanced_fixes = [
        ("Run System File Checker",
         "Open <b>Command Prompt as Admin</b>, type <code>sfc /scannow</code> and press Enter. Wait for the scan to complete."),
        ("Update Windows Fully",
         "Go to <b>Settings → Windows Update</b> and install all pending updates, then restart."),
        ("Reinstall the Software",
         "Uninstall the application causing the error via <b>Control Panel → Programs</b>, then reinstall the latest version."),
    ]

    def render_cards(fixes, start=1):
        html = ""
        for i, (title, desc) in enumerate(fixes, start=start):
            html += f"""
                <div class="fix-card">
                    <div class="fix-number">{i}</div>
                    <div class="fix-body">
                        <div class="fix-title">{title}</div>
                        <div class="fix-desc">{desc}</div>
                    </div>
                </div>"""
        return html

    return f"""
    <div class="fix-wrapper">

        <div class="fix-section">
            <div class="fix-section-header basic">
                <span class="fix-section-icon">🛠</span>
                <span>Basic Fixes</span>
            </div>
            <div class="fix-cards">
                {render_cards(basic_fixes, start=1)}
            </div>
        </div>

        <div class="fix-section">
            <div class="fix-section-header advanced">
                <span class="fix-section-icon">⚙</span>
                <span>Advanced Fixes</span>
            </div>
            <div class="fix-cards">
                {render_cards(advanced_fixes, start=len(basic_fixes) + 1)}
            </div>
        </div>

        <div class="fix-tip">
            💡 <b>Pro Tip:</b> Always restart your PC after installing any DLL or runtime package.
        </div>

    </div>
    """


# ---------------- HOME ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    text     = ""
    solution = "Upload a screenshot to detect the error."
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

                    img  = Image.open(path)
                    text = pytesseract.image_to_string(img, config="--psm 6")

                    # Always show the structured fix box
                    solution = build_fix_box()
                    category = "dll_error"

                else:
                    solution = "<p>OCR is currently disabled.</p>"

            except Exception as e:
                solution = """
                <div class='fix-wrapper'>
                    <div class='fix-tip' style='border-color:#fca5a5; background:#fef2f2; color:#991b1b;'>
                        ⚠ <b>Error during OCR processing.</b><br>
                        1. Restart the server.<br>
                        2. Upload a clearer screenshot.<br>
                        3. Make sure Tesseract is installed correctly.
                    </div>
                </div>"""
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
        path    = os.popen("which tesseract").read().strip()
        version = os.popen("tesseract --version").read().strip()

        if not path:
            return "Tesseract NOT FOUND in PATH"

        return f"Tesseract Path:\n{path}\n\nTesseract Version:\n{version}"

    except Exception as e:
        return f"Error checking tesseract: {str(e)}"


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)