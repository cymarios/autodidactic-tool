from flask import Flask, request, jsonify
from flask_cors import CORS

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
        # Resolve ? based on label
        if label == "1":
            resolved = ''.join(c if c in '01' else '1' for c in example)
        elif label == "0":
            resolved = ''.join(c if c in '01' else '0' for c in example)
        else:
            resolved = example  # keep ? for unlabeled

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
            if removed:
                log_entry += f"Positive; eliminated: {', '.join(sorted(removed))}"
            else:
                log_entry += "Positive; no change."
        else:
            log_entry += "Invalid label; ignored."

        self.log.append(log_entry)

    def get_hypothesis(self):
        # Ordered: x1, ¬x1, x2, ¬x2, ...
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
CORS(app)

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

# -------------------------------
# Run the app
# -------------------------------

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

