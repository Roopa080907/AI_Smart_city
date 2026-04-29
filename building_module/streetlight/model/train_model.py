
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

# Get current file directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build correct path to data file
file_path = os.path.join(current_dir, '..', 'data', 'streetlight_data.csv')



data = pd.read_csv(file_path)


# Features (inputs)
X = data[['time', 'movement', 'traffic']]

# Target (output)
y = data['brightness']

# Train model
model = LinearRegression()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("\nModel trained and saved successfully!")

