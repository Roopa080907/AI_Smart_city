import pandas as pd
import joblib
import os

# Load model
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model.pkl")
model = joblib.load(model_path)


def predict_brightness(time, movement, traffic):
    input_data = pd.DataFrame([[time, movement, traffic]],
                              columns=['time', 'movement', 'traffic'])

    result = model.predict(input_data)[0]

    if result < 30:
        level = "LOW"
    elif result < 70:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return result, level


def run_streetlight(night, motion):
    time = 20 if night else 12
    movement = 1 if motion else 0
    traffic = 1 if movement else 0

    result, level = predict_brightness(time, movement, traffic)

    before = 100.0
    after = float(result)
    savings = before - after

    return {
        "before": before,
        "after": after,
        "savings": savings,
        "level": level
    }


if __name__ == "__main__":
    print(run_streetlight(True, True))
