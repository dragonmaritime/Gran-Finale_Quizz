from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Charge les questions depuis questions.json (même dossier)
def load_questions():
    path = os.path.join(os.path.dirname(__file__), "questions.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Page principale : affiche le quiz (GET) et reçoit les réponses (POST)
@app.route("/", methods=["GET", "POST"])
def quiz():
    questions = load_questions()

    if request.method == "POST":
        # Récupère les réponses envoyées depuis le formulaire
        answers = {}
        for q in questions:
            qid = str(q.get("id", q.get("question", "")))
            answers[qid] = request.form.get(qid, "")

        # Calcul du score : compare la réponse à la bonne réponse ou aux mots-clés
        score = 0
        results = []
        for q in questions:
            qid = str(q.get("id", q.get("question", "")))
            user_ans = (answers.get(qid) or "").strip().lower()

            is_correct = False
            correct_ans = ""

            # Cas 1 : réponse exacte
            if "answer" in q:
                correct_ans = str(q.get("answer", "")).strip().lower()
                is_correct = user_ans == correct_ans

            # Cas 2 : validation par mots-clés
            elif "keywords" in q:
                required_keywords = [kw.lower() for kw in q["keywords"]]
                is_correct = any(kw in user_ans for kw in required_keywords)
                correct_ans = "Mots-clés attendus : " + ", ".join(required_keywords)

            if is_correct:
                score += 1

            results.append({
                "question": q.get("question"),
                "your_answer": user_ans,
                "correct_answer": correct_ans,
                "correct": is_correct
            })

        # 👉 Ce return doit être DANS le if POST
        return render_template("quiz.html", questions=questions, results=results, score=score, total=len(questions))

    # 👉 Ce return est pour le GET
    return render_template("quiz.html", questions=questions, results=None, score=0, total=len(questions))

# Health check simple (utile pour Render)
@app.route("/healthz")
def healthz():
    return "OK", 200

if __name__ == "__main__":
    # Mode debug pour dev local uniquement
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
