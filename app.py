from flask import Flask, render_template, redirect, flash, request, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "NUR1overhere"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

current_survey = "current_survey"

@app.before_request
def print_cookies():
    print("****************")
    responses = session["responses"]
    for response in responses:

        print(response['question'], response['answer'], response.get('text'))
    print("*****************")


@app.route('/')
def choose_survey():
    """Shows the survey option for user to select"""

    return render_template("select_survey.html", surveys = surveys)

@app.route("/", methods=["POST"])
def select_survey():
    """Selects a survey"""

    # this part request.form beacuse methods post
    survey_id = request.form['survey_code']
    survey = surveys[survey_id]
    session["current_survey"] = survey_id
    return render_template("survey_start.html", survey_id = survey_id, title = survey.title, instruction = survey.instructions)

@app.route("/start", methods=["POST"])
def start_survey():
    """Starts survey"""

    session["responses"] = []
    responses = session["responses"]
    return redirect(f"/questions/{len(responses)}")

@app.route("/questions/<int:qid>")
def show_questions(qid):
    """Shows question"""
    session["question_id"] = qid
    survey_id = session["current_survey"]
    survey = surveys[survey_id]
    responses = session.get("responses")

    if len(responses) == len(survey.questions):
        # if all the questions are answered, we thank them
        return redirect("/completed")

    if qid > len(survey.questions) :
        #if qid is out of bound, we return them to the last place they were redirected
        flash(f"Question is out of bound:question/{qid}.")
        return redirect(f'/questions/{len(responses)}')

    if qid > len(responses):
        # if they try to go too, fast
        flash(f"You're not there yet. BE PATIENT")
        return redirect(f'/questions/{len(responses)}')
    
    question = survey.questions[qid]
    return render_template("question.html", qid = qid, question = question)

@app.route("/answer", methods=["POST"])
def save_answer_data():
    """Posts answer to the server adn redirects to the next question"""

    survey_id = session["current_survey"]
    survey = surveys[survey_id]
    qid = session["question_id"]
    question_obj = survey.questions[qid]
    question = question_obj.question
    responses = session.get("responses")
    answer = request.form["answer"]
    text = request.form.get("text", "")
    responses.append({'answer':answer, 'text':text, 'question': question})
    session["responses"] = responses

    if len(responses) == len(survey.questions):
        return redirect('/completed')

    return redirect(f'/questions/{len(responses)}')

@app.route("/completed")
def handle_completion():
    """Thanks the user for fillign the form"""
    survey_id = session["current_survey"]
    survey = surveys[survey_id]
    responses = session["responses"]

    return render_template("thanks.html", survey=survey, responses = responses)

    