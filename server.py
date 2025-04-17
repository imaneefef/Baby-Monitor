from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import librosa
import joblib
import pandas as pd
import traceback
from datetime import datetime
import time

app = Flask(__name__)
CORS(app)  # Activation CORS pour toutes les routes

# Chargement des modèles
try:
    model = joblib.load("cry_non_cry_model.pkl")
    scaler = joblib.load("scaler.pkl")
    df_train = pd.read_csv("/Users/abdelbassirimane/Documents/baby_features.csv")
    feature_columns = df_train.drop(columns=["label"]).columns
    print("✅ Modèles chargés avec succès!")
except Exception as e:
    print(f"❌ Erreur de chargement des modèles: {str(e)}")
    raise

def process_audio(audio_bytes):
    """Transforme les bytes audio en un signal exploitable et extrait les MFCC."""
    try:
        print(f"📥 Longueur des données reçues: {len(audio_bytes)} bytes")

        # 📌 Vérifier les 10 premiers octets reçus
        print(f"🔍 Premiers octets bruts: {audio_bytes[:10]}")

        # 📌 Convertir en entiers (Arduino envoie des uint16)
        audio_data = np.frombuffer(audio_bytes, dtype=np.uint16).astype(np.float32)

        # 📌 Ajuster l'échelle de 0-1023 (Arduino) vers -1 à 1
        audio_data = (audio_data - 512) / 512.0  # Centre autour de 0

        # 🔥 Vérifier si le signal est bien centré autour de zéro
        print(f"📊 Signal - Min: {audio_data.min()}, Max: {audio_data.max()}")
        print(f"🔍 Premières valeurs du signal après conversion: {audio_data[:10]}")

        # 📌 Extraire MFCC
        mfccs = librosa.feature.mfcc(
            y=audio_data,
            sr=4000,  # Fréquence de l'arduino
            n_mfcc=13,
            n_fft=512,
            hop_length=256
        )

        # 📌 Vérifier les valeurs MFCC obtenues
        mfcc_mean = np.mean(mfccs.T, axis=0)
        print(f"🎵 MFCC Features (moyenne): {mfcc_mean}")

        return mfcc_mean

    except Exception as e:
        print(f"❌ Erreur de traitement audio: {str(e)}")
        raise
        
@app.route('/predict', methods=['POST'])
def predict():
    try:
        start_time = time.time()
        
        if not request.data or len(request.data) == 0:
            print("❌ Erreur: aucune donnée reçue")
            return jsonify({"error": "Aucune donnée audio reçue"}), 400

        print(f"\n📦 Données reçues ({len(request.data)} bytes) à {datetime.now().strftime('%H:%M:%S')}")

        # Traitement audio
        mfcc_features = process_audio(request.data)
        
        # Préparation des features
        features_df = pd.DataFrame([mfcc_features], columns=feature_columns)
        features_scaled = scaler.transform(features_df)
        
        # Prédiction
        probabilities = model.predict_proba(features_scaled)[0]
        is_cry = probabilities[1] > 0.8  # Seuil à 60%
        
        # 📌 Logs des probabilités
        print(f"📊 Probabilités - Non Cry: {probabilities[0]*100:.1f}%, Cry: {probabilities[1]*100:.1f}%")

        # Formatage réponse
        response = {
            "is_cry": bool(is_cry),
            "probabilities": {
                "non_cry": float(probabilities[0]),
                "cry": float(probabilities[1])
            },
            "mfcc_features": [float(x) for x in mfcc_features],
            "processing_time": round(time.time() - start_time, 3)
        }
        
        print(f"📤 Résultat: {'CRY' if is_cry else 'NO_CRY'} (Confiance: {probabilities[1]*100:.1f}%)")
        return jsonify(response)
        
    except Exception as e:
        print(f"🔥 ERREUR CRITIQUE: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Erreur de traitement",
            "details": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "OK",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model is not None
    })

if __name__ == '__main__':
    print("\n🚀 Serveur Baby Monitor en écoute sur http://0.0.0.0:5050")
    app.run(host='0.0.0.0', port=5050, debug=True)