import os
import librosa
import numpy as np
import pandas as pd

# Dossier contenant les données
audio_folder = "/Users/abdelbassirimane/Desktop/IA_IOT/babydatacry_Final_for_project/Cry_or_Non-Cry"

# Fonction pour extraire les MFCC d'un fichier audio
def extract_mfcc(file_path):
    audio, sr = librosa.load(file_path, sr=None)  # Chargement de l'audio avec la fréquence d'échantillonnage native
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)  # Extraction des 13 coefficients MFCC
    mfcc_mean = np.mean(mfcc, axis=1)  # Moyenne des coefficients pour chaque feature
    return mfcc_mean

# Vérification du nombre de fichiers dans chaque catégorie
print("📊 Vérification du dataset :")
for label in ["Cry", "Non_Cry"]:
    label_folder = os.path.join(audio_folder, label)
    count = len([f for f in os.listdir(label_folder) if f.endswith(".wav")])
    print(f" - {label} : {count} fichiers")

# Liste pour stocker les données
data = []
labels = []

# Parcours des fichiers dans le dossier "Cry" et "Non-Cry"
#revoir cette partie pour être sur que ça les labels bien
for label in ["Cry", "Non_Cry"]:
    label_folder = os.path.join(audio_folder, label)
    for file_name in os.listdir(label_folder):
        if file_name.endswith(".wav"):
            file_path = os.path.join(label_folder, file_name)
            mfcc_features = extract_mfcc(file_path)
            data.append(mfcc_features)
            labels.append(label)

# Convertir les données en DataFrame pour une utilisation facile avec pandas
df = pd.DataFrame(data)
df['label'] = labels

# Afficher les 5 premières lignes pour vérifier
print("\n🔍 Aperçu des données MFCC extraites :")
print(df.head())

# Sauvegarder les données dans un fichier CSV
df.to_csv("/Users/abdelbassirimane/Documents/baby_features.csv", index=False)

print("\n✅ Données MFCC extraites et sauvegardées dans 'baby_features.csv'")
