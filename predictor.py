from sklearn.linear_model import LinearRegression
import numpy as np

class PerformancePredictor:
    """A small illustrative model estimating a study score from study habits."""
    def __init__(self):
        self.model = LinearRegression()
        # Example training data: [study hours, tasks completed] -> score / 100
        x = np.array([
            [0.5, 1], [1, 2], [1.5, 2], [2, 4], [2.5, 5],
            [3, 6], [4, 7], [5, 9], [6, 10], [7, 12]
        ])
        y = np.array([18, 25, 32, 42, 50, 59, 68, 78, 86, 95])
        self.model.fit(x, y)

    def predict_score(self, study_hours: float, tasks_completed: int) -> int:
        if study_hours < 0 or tasks_completed < 0:
            raise ValueError("Inputs must be zero or greater.")
        prediction = self.model.predict([[study_hours, tasks_completed]])[0]
        return max(0, min(100, round(float(prediction))))
