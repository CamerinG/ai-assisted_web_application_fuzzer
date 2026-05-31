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

    # Load some sample payloads for testing the prediction of the model. In a real scenario, you would want to test with a wider variety of payloads.
    with open("payloads/sqli_payloads.txt", "r", encoding="utf-8", errors="ignore") as f:
        sqli_payloads = [line.strip() for line in f if line.strip()][:10]
    
    with open("payloads/xss_payloads.txt", "r", encoding="utf-8", errors="ignore") as f:
        xss_payloads = [line.strip() for line in f if line.strip()][:10]

    for payload in sqli_payloads + xss_payloads:
        pred, prob = predict_vulnerability(payload)
        print(f"Payload: {payload[:35]:<35} | Predicted: {pred} | Confidence: {prob:.2f}")