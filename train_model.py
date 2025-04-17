import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Charger les données extraites (baby_features.csv)
df = pd.read_csv("/Users/abdelbassirimane/Documents/baby_features.csv")

# Séparer les caractéristiques (X) et les étiquettes (y)
X = df.drop(columns=["label"])
y = df["label"]

# Encoder les étiquettes ("Cry" -> 1, "Non-Cry" -> 0)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Normalisation des données
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

# Créer et entraîner un modèle Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Faire des prédictions sur l'ensemble de test
y_pred = model.predict(X_test)

# Calculer l'accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Accuracy du modèle : {accuracy * 100:.2f}%\n")

# Afficher un rapport de classification
print("📊 Rapport de classification :\n", classification_report(y_test, y_pred))

# Sauvegarder le modèle entraîné pour une utilisation future
joblib.dump(model, "cry_non_cry_model.pkl")
joblib.dump(scaler, "scaler.pkl")  # Sauvegarde du scaler pour l'utiliser en prédiction

print("\n✅ Modèle sauvegardé sous 'cry_non_cry_model.pkl'")
