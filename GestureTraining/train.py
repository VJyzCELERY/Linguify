import cv2
import numpy as np
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import joblib
import mediapipe as mp
from sklearn.metrics import classification_report

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

def extract_landmarks(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image at {image_path}")
        return None
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
    return None

dataset_path = "./GestureTraining/Dataset"

data = []
labels = []

for label_folder in os.listdir(dataset_path):
    class_folder = os.path.join(dataset_path, label_folder)
    
    if os.path.isdir(class_folder):
        for img_file in os.listdir(class_folder):
            img_path = os.path.join(class_folder, img_file)
            
            if os.path.isfile(img_path):
                landmarks = extract_landmarks(img_path)
                if landmarks is not None:
                    data.append(landmarks)
                    labels.append(label_folder)

data = np.array(data)
labels = np.array(labels)

label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)
joblib.dump(label_encoder, 'label_encoder.pkl')

df = pd.DataFrame(data)
df['label'] = labels_encoded
df.to_csv('sign_language_dataset.csv', index=False)

X_train, X_test, y_train, y_test = train_test_split(data, labels_encoded, test_size=0.2, random_state=42)

model = SVC(kernel='linear', probability=True)
model.fit(X_train, y_train)

joblib.dump(model, 'sign_language_model.pkl')

accuracy = model.score(X_test, y_test)
print(f"Model accuracy: {accuracy:.2f}")

y_pred = model.predict(X_test)
unique_labels_in_test = np.unique(y_test)

print("Classes in test data:", unique_labels_in_test)
print(
    classification_report(
        y_test,
        y_pred,
        labels=unique_labels_in_test,
        target_names=label_encoder.inverse_transform(unique_labels_in_test)
    )
)
