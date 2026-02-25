# # scripts/train_classifier.py
# import pandas as pd
# import numpy as np
# import joblib
# import os
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.pipeline import Pipeline

# # 1. Setup Paths
# DATA_PATH = "data/exp1_14drivers_14cars_dailyRoutes.csv"
# MODEL_PATH = "models/dtc_classifier.pkl"
# os.makedirs("models", exist_ok=True)

# # 2. Define Synthetic Knowledge Base (DTC -> Root Cause)
# # This maps the codes from your CSV to likely causes
# knowledge_base = {
#     'P0133': 'O2 Sensor Slow Response (Bank 1 Sensor 1)',
#     'P0079': 'Exhaust Valve Control Solenoid Circuit Low (Bank 1)',
#     'P2004': 'Intake Manifold Runner Control Stuck Open (Bank 1)',
#     'P0300': 'Random/Multiple Cylinder Misfire Detected',
#     'U1004': 'Loss of Communication with TCM',
#     'C0300': 'Rear Speed Sensor Circuit Malfunction',
#     'P0171': 'System Too Lean (Bank 1) - Vacuum Leak',
#     'P0420': 'Catalyst System Efficiency Below Threshold (Bank 1)'
# }

# # 3. Generate Synthetic Training Data
# print("Generating synthetic training data...")
# training_data = []
# for _ in range(1000):  # Generate 1000 examples
#     dtc = np.random.choice(list(knowledge_base.keys()))
#     root_cause = knowledge_base[dtc]
    
#     # Simulate different ways a user or scanner might present the issue
#     templates = [
#         f"Scanner shows error {dtc}",
#         f"I have a check engine light with code {dtc}",
#         f"The car is driving poorly and gives {dtc}",
#         f"Diagnostic Trouble Code: {dtc}",
#         f"Fault {dtc} detected during scan"
#     ]
#     text = np.random.choice(templates)
    
#     training_data.append({'text': text, 'label': root_cause})

# df = pd.DataFrame(training_data)

# # 4. Train the Pipeline
# print("Training classification model...")
# pipeline = Pipeline([
#     ('tfidf', TfidfVectorizer()),
#     ('clf', RandomForestClassifier(n_estimators=100))
# ])

# pipeline.fit(df['text'], df['label'])

# # 5. Save the Model
# joblib.dump(pipeline, MODEL_PATH)
# print(f"✅ Model saved to {MODEL_PATH}")




# # scripts/train_classifier.py
# import pandas as pd
# import numpy as np
# import joblib
# import os
# from sklearn.feature_extraction.text import TfidfVectorizer
# from xgboost import XGBClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.pipeline import Pipeline

# # 1. Setup Paths
# MODEL_PATH = "models/dtc_classifier_xgb.json" # XGBoost prefers .json for its own format
# ENCODER_PATH = "models/label_encoder.pkl"
# os.makedirs("models", exist_ok=True)

# # 2. Synthetic Knowledge Base
# knowledge_base = {
#     'P0133': 'O2 Sensor Slow Response (Bank 1 Sensor 1)',
#     'P0079': 'Exhaust Valve Control Solenoid Circuit Low (Bank 1)',
#     'P2004': 'Intake Manifold Runner Control Stuck Open (Bank 1)',
#     'P0300': 'Random/Multiple Cylinder Misfire Detected',
#     'U1004': 'Loss of Communication with TCM',
#     'C0300': 'Rear Speed Sensor Circuit Malfunction',
#     'P0171': 'System Too Lean (Bank 1) - Vacuum Leak',
#     'P0420': 'Catalyst System Efficiency Below Threshold (Bank 1)'
# }

# # 3. Generate Training Data
# training_data = []
# for _ in range(1200): # Increased sample size for XGBoost
#     dtc = np.random.choice(list(knowledge_base.keys()))
#     root_cause = knowledge_base[dtc]
#     templates = [f"Code {dtc}", f"Scanner shows {dtc}", f"Check engine light {dtc}", f"Error {dtc} detected"]
#     training_data.append({'text': np.random.choice(templates), 'label': root_cause})

# df = pd.DataFrame(training_data)

# # 4. Encode Labels (Required for XGBoost)
# le = LabelEncoder()
# df['label_encoded'] = le.fit_transform(df['label'])

# # 5. Build and Train Pipeline
# # Note: We use Tfidf to convert text to vectors first
# tfidf = TfidfVectorizer()
# X = tfidf.fit_transform(df['text'])
# y = df['label_encoded']

# print("Training XGBoost model...")
# xgb_model = XGBClassifier(
#     n_estimators=100,
#     learning_rate=0.1,
#     max_depth=5,
#     use_label_encoder=False,
#     eval_metric='mlogloss'
# )

# xgb_model.fit(X, y)

# # 6. Save Everything
# # Save the model, the TF-IDF vectorizer, and the Label Encoder
# joblib.dump(tfidf, "models/tfidf_vectorizer.pkl")
# joblib.dump(le, ENCODER_PATH)
# xgb_model.save_model(MODEL_PATH)

# print(f"✅ XGBoost Model and Encoder saved to models/")



import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the combined dataset
df = pd.read_csv('data/combined_balanced_dataset.csv')

# Encoding Categorical Data
model_encoder = LabelEncoder()
df['CAR_MODEL_ENC'] = model_encoder.fit_transform(df['CAR_MODEL'])

label_encoder = LabelEncoder()
df['TARGET'] = label_encoder.fit_transform(df['TROUBLE_CODES'])

# Define Features
features = [
    'CAR_MODEL_ENC', 'YEAR', 'ENGINE_RPM', 'VEHICLE_SPEED', 
    'ENGINE_LOAD', 'COOLANT_TEMP', 'MAF_GRAMS_SEC', 
    'SHORT_TERM_TRIM', 'LONG_TERM_TRIM', 'THROTTLE_POS'
]

X = df[features]
y = df['TARGET']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    objective='multi:softprob',
    use_label_encoder=False
)

model.fit(X_train, y_train)

# Save the model and encoders
joblib.dump(model, 'models/dtc_classifier.pkl')
joblib.dump(model_encoder, 'models/car_model_encoder.pkl')
joblib.dump(label_encoder, 'models/target_label_encoder.pkl')

print("Model Training Complete. Accuracy on test set: ", model.score(X_test, y_test))
