from gpt4all import GPT4All
from flask import Flask, render_template, request
import sqlite3
from datetime import date

app = Flask(__name__)
model = GPT4All(
    model_name="Phi-3-mini-4k-instruct.Q4_0.gguf",   
    model_path="C:/Users/shikh/AppData/Local/nomic.ai/GPT4All/",
    device="cpu"
)

def get_feedback(glasses):
    try:
        prompt = f"""
        I drank {glasses} glasses of water today.
        My goal is 8 glasses.
        Give short health advice in 1 line.
        """
        response = model.generate(prompt, max_tokens=50)
        return response.replace("<assistant>", "").strip()

    except Exception as e:
        print("AI Error:", e)
        return "Try to drink 8 glasses of water for good health!"

    
@app.route("/", methods=["GET","POST"])
def  home():
    feedback = None
    if request.method=="POST":
        glasses = request.form["glasses"]
        today= date.today()
        
        conn=sqlite3.connect("water.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_log (
            date TEXT PRIMARY KEY,
                glasses INTEGER
            )
            """)
        cursor.execute("""
        INSERT OR REPLACE INTO water_log (date, glasses)
        VALUES (?,?)
        """, (today, glasses))

        conn.commit()
        conn.close()

        print("Saved:", today,glasses)
        feedback = get_feedback(glasses)
        

    conn = sqlite3.connect("water.db")
    cursor = conn.cursor()

    cursor.execute("SELECT glasses FROM water_log WHERE date = ?", (date.today(),))
    result = cursor.fetchone()

    conn.close()

    water = result[0] if result else None

    return render_template("index.html", water=water, feedback=feedback)

if __name__=="__main__":
    app.run(debug=True)

#conda activate water-tracker
#python app.py