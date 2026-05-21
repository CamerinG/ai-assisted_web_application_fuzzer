import joblib
import pandas as pd



def predict_vulnerability(payload):
    """Predict if the payload is likely to be a vulnerability."""
    features = {
    'payload_length': len(payload),
    'has_single_quote': int("'" in payload), 
    'has_angle_bracket': int("<" in payload),
    'has_double_dash': int("--" in payload),
    'has_equals': int("=" in payload),
    'special_char_count': sum(1 for c in payload if not c.isalnum() and not c.isspace()),
    }
    
    # Load the trained model
    model = joblib.load("models/random_forest_model.pkl")
    
    # Create a DataFrame for the input payload
    df = pd.DataFrame([features])
    
    # Predict using the model
    prediction = model.predict(df)

    # probability of being a vulnerability
    probability = model.predict_proba(df)[0][1]  
    
    return prediction[0], probability

if __name__ == "__main__":
    test_payloads = [
        "SELECT * FROM users WHERE username='admin'--",
        "<script>alert('XSS')</script>",
        "normalpayload123",
        "DROP TABLE users;--",
        "Hello World!"
    ]
    for payload in test_payloads:
        pred, prob = predict_vulnerability(payload)
        print(f"Payload: {payload[:30]:<30} | Predicted: {pred} | Confidence: {prob:.2f}")