class AutodidacticLearner:
    def __init__(self, num_features):
        self.num_features = num_features
        self.hypothesis = set()
        for i in range(num_features):
            self.hypothesis.add(f"x{i+1}")
            self.hypothesis.add(f"¬x{i+1}")

    def refine_hypothesis(self, example, label):
        previous_hypothesis = self.hypothesis.copy()

        if label == '1':
            for i, val in enumerate(example):
                if val == '1':
                    self.hypothesis.discard(f"¬x{i+1}")
                elif val == '0':
                    self.hypothesis.discard(f"x{i+1}")
        elif label == '0':
            example = example.replace('?', '0')

    def get_hypothesis(self):
        return sorted(list(self.hypothesis))
