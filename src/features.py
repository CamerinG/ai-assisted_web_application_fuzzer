import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

# import fuzzing results and clean the data
df = pd.read_csv("data/fuzzing_results.csv")
df_cleaned = df.drop_duplicates().dropna()
print(f"Records after cleaning: {len(df_cleaned)}")

# Feature engineering. To give the model numerical signals about the payloads
df_cleaned['has_single_quote'] = df_cleaned['payload'].str.contains("'").astype(int)
df_cleaned['has_angle_bracket'] = df_cleaned['payload'].str.contains("<").astype(int)
df_cleaned['has_double_dash'] = df_cleaned['payload'].str.contains("--").astype(int)
df_cleaned['has_equals'] = df_cleaned['payload'].str.contains("=").astype(int)
df_cleaned['special_char_count'] = df_cleaned['payload'].str.count(r'[^a-zA-Z0-9\s]')

# Encode payload types (sqli/xss/benign -> 0/1/2)
le = LabelEncoder()
df_cleaned['payload_type_encoded'] = le.fit_transform(df_cleaned['payload_type'])

# Scale numerical features
scaler = StandardScaler()
numeric_cols = ['payload_length', 'response_code', 'response_length', 'special_char_count'] 
df_cleaned[numeric_cols] = scaler.fit_transform(df_cleaned[numeric_cols])

# save the preprocessed data for model training
df_cleaned.to_csv("data/processed.csv", index=False)
print(f"Preprocessed dataset saved with {len(df_cleaned)} records and {len(df_cleaned.columns)} features")
print(df_cleaned.columns.tolist())