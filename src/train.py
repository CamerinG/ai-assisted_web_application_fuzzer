from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import pandas as pd

data_preprocessed = pd.read_csv("data/processed.csv")

feature_x = data_preprocessed[[
    "payload_length", "has_single_quote",
    "has_angle_bracket", "has_double_dash", "has_equals",
    "special_char_count"
]]

target_y = data_preprocessed["triggered"]

# Split the dataset into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(feature_x, target_y, test_size=0.2, random_state=42)

print(f"Training set: {len(X_train)} records")
print(f"Testing set: {len(X_test)} records")

# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)
print("Model training completed.")

# Evaluate the model on the test set
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy:.2f}")

# feature importance analysis
feature_importance = pd.Series(
    model.feature_importances_, index=feature_x.columns
).sort_values(ascending=False)
print(f"\nFeature Importances:\n{feature_importance}" )

# classification report and model evaluation
y_pred = model.predict(X_test)
print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")

joblib.dump(model, "models/random_forest_model.pkl")
print("Model saved to models/random_forest_model.pkl")

# cross validation
cross_val_scores = cross_val_score(model, feature_x, target_y, cv=5)
print(f"\nCross-validation scores: {cross_val_scores}")
print(f"Average cross-validation score: {cross_val_scores.mean():.2f}")

# hyperparameter tuning with GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10]
}
grid = GridSearchCV(estimator=model, param_grid=param_grid, cv=5)
grid.fit(feature_x, target_y)
print(f"\nBest hyperparameters: {grid.best_params_}")

best_model = grid.best_estimator_
joblib.dump(best_model, "models/random_forest_model.pkl")
print("Optimized model saved")