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



import os
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend — safe for scripts without a display
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

print("🚗 Loading the balanced dataset...")
df = pd.read_csv('data/combined_balanced_dataset.csv')

# 1. Fill blanks / None with HEALTHY
df['TROUBLE_CODES'] = df['TROUBLE_CODES'].fillna("HEALTHY")
df['TROUBLE_CODES'] = df['TROUBLE_CODES'].replace("None", "HEALTHY")

# 2. Inject realistic sensor noise for robustness
print("🌪️ Injecting real-world sensor noise...")
numeric_cols = ['ENGINE_RPM', 'VEHICLE_SPEED', 'ENGINE_LOAD', 'COOLANT_TEMP',
                'MAF_GRAMS_SEC', 'SHORT_TERM_TRIM', 'LONG_TERM_TRIM', 'THROTTLE_POS']

np.random.seed(42)
for col in numeric_cols:
    std_dev = df[col].std()
    noise = np.random.normal(0, std_dev * 0.40, size=len(df))
    df[col] = df[col] + noise

# 3. Encode categorical features
print("🔧 Encoding categorical features...")
model_encoder = LabelEncoder()
df['CAR_MODEL_ENC'] = model_encoder.fit_transform(df['CAR_MODEL'].astype(str))

label_encoder = LabelEncoder()
df['TARGET'] = label_encoder.fit_transform(df['TROUBLE_CODES'])

# 4. Define features and target
features = [
    'CAR_MODEL_ENC', 'YEAR', 'ENGINE_RPM', 'VEHICLE_SPEED',
    'ENGINE_LOAD', 'COOLANT_TEMP', 'MAF_GRAMS_SEC',
    'SHORT_TERM_TRIM', 'LONG_TERM_TRIM', 'THROTTLE_POS'
]

X = df[features]
y = df['TARGET']

# 5. Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 6. Train Random Forest
print("🧠 Training Random Forest Classifier...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train, y_train)

# 7. Evaluate
print("\n📊 Random Forest Model Evaluation:")
preds = model.predict(X_test)
y_test_labels = label_encoder.inverse_transform(y_test)
preds_labels = label_encoder.inverse_transform(preds)
print(classification_report(y_test_labels, preds_labels))

# --- Confusion Matrix ---
print("\n📊 Confusion Matrix:")
class_labels = label_encoder.classes_
cm = confusion_matrix(y_test_labels, preds_labels, labels=class_labels)
cm_df = pd.DataFrame(cm, index=class_labels, columns=class_labels)
cm_df.index.name = "Actual \\ Predicted"
print(cm_df.to_string())
print("\n(Rows = Actual class, Columns = Predicted class)")

# --- Save visual confusion matrix heatmap ---
print("\n🖼️  Generating confusion matrix heatmap...")
os.makedirs('models', exist_ok=True)

n_classes = len(class_labels)
# Scale figure size dynamically so labels never overlap
fig_size = max(10, n_classes * 0.9)
fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))

# Normalised matrix (row-wise, so each cell = recall for that class)
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)

# Draw heatmap with count annotations; colour intensity = normalised value
sns.heatmap(
    cm_norm,
    annot=cm,           # show raw counts inside cells
    fmt='d',
    cmap='Blues',
    linewidths=0.4,
    linecolor='#e0e0e0',
    xticklabels=class_labels,
    yticklabels=class_labels,
    ax=ax,
    cbar_kws={'label': 'Recall (normalised)', 'shrink': 0.75},
    annot_kws={'size': max(7, 11 - n_classes // 5)},
)

ax.set_title(
    'Random Forest — Confusion Matrix\n(cell = count  |  colour = per-class recall)',
    fontsize=14, fontweight='bold', pad=18
)
ax.set_xlabel('Predicted DTC', fontsize=12, labelpad=10)
ax.set_ylabel('Actual DTC', fontsize=12, labelpad=10)

# Rotate long x-axis labels for readability
plt.xticks(rotation=45, ha='right', fontsize=max(7, 10 - n_classes // 8))
plt.yticks(rotation=0, fontsize=max(7, 10 - n_classes // 8))

plt.tight_layout()

cm_path = 'models/confusion_matrix.png'
plt.savefig(cm_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"✅ Confusion matrix heatmap saved → {cm_path}")

print("Accuracy on test set:", model.score(X_test, y_test))

print("\n📊 Feature Importance:")
importances = model.feature_importances_
for col, imp in sorted(zip(features, importances), key=lambda x: -x[1]):
    print(f"  {col}: {imp:.4f}")

# 8. Sample confidence scores
print("\n🎯 Sample Confidence Scores (first 5 test samples):")
probas = model.predict_proba(X_test[:5])
classes = model.classes_
for i, (pred, proba) in enumerate(zip(preds[:5], probas)):
    confidence = max(proba) * 100
    dtc = label_encoder.inverse_transform([pred])[0]
    print(f"  Sample {i+1}: Predicted={dtc}, Confidence={confidence:.1f}%")

# 9. Save model artifacts (same paths as before so classifier_tool.py works)
print("\n💾 Saving model artifacts...")
joblib.dump(model, 'models/dtc_classifier.pkl')
joblib.dump(model_encoder, 'models/car_model_encoder.pkl')
joblib.dump(label_encoder, 'models/target_label_encoder.pkl')

print("✅ Random Forest model saved successfully!")
print("   - models/dtc_classifier.pkl")
print("   - models/car_model_encoder.pkl")
print("   - models/target_label_encoder.pkl")
