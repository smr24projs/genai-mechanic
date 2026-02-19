"""
Random Forest DTC Classifier Training Script
=============================================
Trains a Random Forest model on combined_balanced_dataset.csv for DTC code classification.
Outputs: rf_dtc_model.pkl, rf_label_encoder.pkl, rf_class_names.pkl
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

print("🚗 Loading the balanced dataset...")
df = pd.read_csv("combined_balanced_dataset.csv")

# 1. Fill blanks with HEALTHY
df['TROUBLE_CODES'] = df['TROUBLE_CODES'].fillna("HEALTHY")

# 2. Inject realistic sensor noise (same approach as train_realisitc_model.py)
print("🌪️ Injecting real-world sensor noise...")
numeric_cols = ['ENGINE_RPM', 'VEHICLE_SPEED', 'ENGINE_LOAD', 'COOLANT_TEMP',
                'MAF_GRAMS_SEC', 'SHORT_TERM_TRIM', 'LONG_TERM_TRIM', 'THROTTLE_POS']

np.random.seed(42)
for col in numeric_cols:
    std_dev = df[col].std()
    noise = np.random.normal(0, std_dev * 0.40, size=len(df))
    df[col] = df[col] + noise

# 3. Encode categorical feature (CAR_MODEL)
print("🔧 Encoding categorical features...")
le_car = LabelEncoder()
df['CAR_MODEL_ENCODED'] = le_car.fit_transform(df['CAR_MODEL'].astype(str))

# 4. Prepare features and target
feature_cols = ['CAR_MODEL_ENCODED', 'YEAR', 'ENGINE_RPM', 'VEHICLE_SPEED',
                'ENGINE_LOAD', 'COOLANT_TEMP', 'MAF_GRAMS_SEC',
                'SHORT_TERM_TRIM', 'LONG_TERM_TRIM', 'THROTTLE_POS']

X = df[feature_cols]
y = df['TROUBLE_CODES']

# 5. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 6. Train Random Forest
print("🧠 Training Random Forest Classifier...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',  # Handle any remaining imbalance
    random_state=42,
    n_jobs=-1,
    verbose=1
)

rf_model.fit(X_train, y_train)

# 7. Evaluate
print("\n📊 Random Forest Model Evaluation:")
preds = rf_model.predict(X_test)
print(classification_report(y_test, preds))

print("\n📊 Confusion Matrix:")
print(confusion_matrix(y_test, preds))

# 8. Feature Importance
print("\n📊 Feature Importance:")
importances = rf_model.feature_importances_
for col, imp in sorted(zip(feature_cols, importances), key=lambda x: -x[1]):
    print(f"  {col}: {imp:.4f}")

# 9. Demonstrate confidence scoring
print("\n🎯 Sample Confidence Scores (first 5 test samples):")
probas = rf_model.predict_proba(X_test[:5])
classes = rf_model.classes_
for i, (pred, proba) in enumerate(zip(preds[:5], probas)):
    confidence = max(proba) * 100
    print(f"  Sample {i+1}: Predicted={pred}, Confidence={confidence:.1f}%")
    # Show top 3 class probabilities
    top3_idx = np.argsort(proba)[-3:][::-1]
    for idx in top3_idx:
        print(f"    {classes[idx]}: {proba[idx]*100:.1f}%")

# 10. Save model artifacts
print("\n💾 Saving model artifacts...")
joblib.dump(rf_model, "rf_dtc_model.pkl")
joblib.dump(le_car, "rf_label_encoder.pkl")
joblib.dump(list(rf_model.classes_), "rf_class_names.pkl")

print("✅ Random Forest model saved successfully!")
print("   - rf_dtc_model.pkl (model)")
print("   - rf_label_encoder.pkl (label encoder for CAR_MODEL)")
print("   - rf_class_names.pkl (class names)")
