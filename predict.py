import librosa
import numpy as np
import joblib
import pandas as pd

# Charger le modèle pré-entraîné et le scaler
model = joblib.load("cry_non_cry_model.pkl")
scaler = joblib.load("scaler.pkl")  # Charger le scaler

# Charger les noms de colonnes depuis le fichier d'entraînement
df_train = pd.read_csv("/Users/abdelbassirimane/Documents/baby_features.csv")
feature_columns = df_train.drop(columns=["label"]).columns  # Récupérer les noms des colonnes MFCC

# Fonction pour extraire les MFCC d'un fichier audio
def extract_mfcc(audio_file):
    y, sr = librosa.load(audio_file, sr=None)  # Charger l'audio
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # Extraire les MFCC
    mfccs_mean = np.mean(mfccs, axis=1)  # Moyenne des MFCC sur le temps
    return mfccs_mean

def predict(audio_file):
    mfccs = extract_mfcc(audio_file)
    
    if mfccs.shape[0] != len(feature_columns):
        print(f"⚠️ Problème avec l'extraction MFCC du fichier : {audio_file}")
        return "Erreur de prédiction"
    
    mfccs_df = pd.DataFrame([mfccs], columns=feature_columns)
    mfccs_scaled = scaler.transform(mfccs_df)  # Appliquer le même scaler

    # Obtenir les probabilités
    probabilities = model.predict_proba(mfccs_scaled)
    print(f"Probabilités du modèle pour 'Pleur' (1) et 'Non-Pleur' (0) : {probabilities}")
    
    # Ajuster le seuil pour décider
    seuil = 0.65  # Seuil ajusté

    # Vérifier la probabilité pour le "pleur" (0)
    if probabilities[0][0] > seuil:
        return "Pleur détecté"  # Retourner Pleur si la probabilité pour le pleur est plus élevée que le seuil
    else:
        return "Non-pleur"  # Sinon, retourner Non-pleur




# Tester plusieurs fichiers
test_files = [
    "/Users/abdelbassirimane/Desktop/IA_IOT/audio_data/Cry_test.wav",
    "/Users/abdelbassirimane/Desktop/IA_IOT/audio_data/test.wav"
]

print("\n📌 Résultats des prédictions :")
for file in test_files:
    print(f"🔊 Fichier : {file} → {predict(file)}")
