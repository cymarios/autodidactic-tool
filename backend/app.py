from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# -------------------------------
# Autodidactic Learner Definition
# -------------------------------

class AutodidacticLearner:
    def __init__(self, num_features):
        self.num_features = num_features
        self.reset()

    def reset(self):
        self.hypothesis = set()
        self.log = []
        for i in range(self.num_features):
            self.hypothesis.add(f"x{i+1}")
            self.hypothesis.add(f"¬x{i+1}")

    def refine_hypothesis(self, example, label):
        if label == "1":
            resolved = ''.join(c if c in '01' else '1' for c in example)
        elif label == "0":
            resolved = ''.join(c if c in '01' else '0' for c in example)
        else:
            resolved = example

        log_entry = f"Example: {resolved}:{label} | "

        if label == "":
            log_entry += "No label; ignored."
        elif label == "?":
            log_entry += "Unlabeled example; ignored."
        elif label == "0":
            log_entry += "Negative example; unchanged."
        elif label == "1":
            removed = set()
            for i, val in enumerate(resolved):
                if val == '1':
                    if f"¬x{i+1}" in self.hypothesis:
                        self.hypothesis.remove(f"¬x{i+1}")
                        removed.add(f"¬x{i+1}")
                elif val == '0':
                    if f"x{i+1}" in self.hypothesis:
                        self.hypothesis.remove(f"x{i+1}")
                        removed.add(f"x{i+1}")
            log_entry += f"Positive; eliminated: {', '.join(sorted(removed))}" if removed else "Positive; no change."
        else:
            log_entry += "Invalid label; ignored."

        self.log.append(log_entry)

    def get_hypothesis(self):
        ordered = []
        for i in range(1, self.num_features + 1):
            if f"x{i}" in self.hypothesis:
                ordered.append(f"x{i}")
            if f"¬x{i}" in self.hypothesis:
                ordered.append(f"¬x{i}")
        return ordered

    def get_log(self):
        return self.log

# -------------------------------
# Flask Setup
# -------------------------------

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

learner = AutodidacticLearner(num_features=5)

@app.route('/')
def home():
    return "Autodidactic Learner API is running!"

@app.route('/submit_example', methods=['POST'])
def submit_example():
    data = request.json
    example = data.get('example', '')
    label = data.get('label', '')
    learner.refine_hypothesis(example, label)
    return jsonify({
        "status": "success",
        "current_hypothesis": learner.get_hypothesis(),
        "log": learner.get_log()
    })

@app.route('/reset', methods=['POST'])
def reset():
    learner.reset()
    return jsonify({
        "status": "reset",
        "current_hypothesis": learner.get_hypothesis(),
        "log": learner.get_log()
    })

@app.route('/guess', methods=['POST'])
def guess():
    data = request.json
    guessed_literals = set(data.get("guess", []))
    correct_hypothesis = set(learner.get_hypothesis())
    all_literals = set(f"x{i+1}" for i in range(learner.num_features)) | set(f"¬x{i+1}" for i in range(learner.num_features))

    # Handle edge case: user guesses before submitting any example
    if correct_hypothesis == all_literals:
        return jsonify({
            "status": "error",
            "message": "You must submit at least one labeled example before making a guess."
        }), 400

    correct_inclusions = guessed_literals & correct_hypothesis
    correct_exclusions = (all_literals - guessed_literals) & (all_literals - correct_hypothesis)
    total_correct = len(correct_inclusions) + len(correct_exclusions)

    score_percentage = round((total_correct / len(all_literals)) * 100)

    return jsonify({
        "status": "success",
        "score": f"{total_correct}/10",
        "percentage": f"{score_percentage}%",
        "correct_inclusions": sorted(list(correct_inclusions)),
        "correct_exclusions": sorted(list(correct_exclusions)),
        "actual_hypothesis": sorted(list(correct_hypothesis))
    })

