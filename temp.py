from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Dummy data for questions
questions = [
    {
        "id": 1,
        "question": "What is Python?",
        "options": ["A programming language", "A reptile", "A type of bird", "A fruit"],
        "answer": "A programming language"
    },
    {
        "id": 2,
        "question": "What is 2 + 2?",
        "options": ["1", "3", "4", "5"],
        "answer": "4"
    },
    {
        "id": 3,
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "answer": "Paris"
    },
    # Add more questions as needed
]

# User's selected answers
selected_answers = {}

# Timer duration (in seconds)
timer_duration = 15 * 60  # 15 minutes

@app.route('/')
def index():
    return render_template('index.html', questions=questions, timer_duration=timer_duration)

@app.route('/fetch_questions', methods=['GET'])
def fetch_questions():
    return jsonify(questions)

@app.route('/save_answer', methods=['POST'])
def save_answer():
    data = request.get_json()
    question_id = int(data['question_id'])
    selected_answer = data['selected_answer']
    selected_answers[question_id] = selected_answer
    return jsonify({'message': 'Answer saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)
