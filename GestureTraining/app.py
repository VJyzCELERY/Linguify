import asyncio
import websockets
import json
import cv2
import numpy as np
import joblib
import base64
from io import BytesIO
from PIL import Image
import mediapipe as mp
import traceback

# Load the model and label encoder
model = joblib.load('sign_language_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

# Function to extract hand landmarks from the image
def extract_landmarks(image):
    result = hands.process(image)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
    return None

# Decode the base64 image string
def decode_image(data_url):
    img_data = base64.b64decode(data_url.split(',')[1])
    img = Image.open(BytesIO(img_data))
    return np.array(img)

# WebSocket handler function to process incoming messages
async def process_message(websocket):
    try:
        async for message in websocket:
            data = json.loads(message)
            img_data_url = data['image']
            
            # Decode the image from base64
            img = decode_image(img_data_url)
            
            # Convert the image to RGB (OpenCV default is BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Extract hand landmarks from the image
            landmarks = extract_landmarks(img_rgb)
            
            if landmarks is not None:
                # Make prediction using the pre-trained model
                prediction = model.predict([landmarks])
                
                # Decode the predicted label using label encoder
                predicted_label = label_encoder.inverse_transform(prediction)
                
                # Send the result back to the client
                response = {'prediction': predicted_label[0]}
                await websocket.send(json.dumps(response))
            else:
                response = {'error': 'No hand detected'}
                await websocket.send(json.dumps(response))
    except Exception as e:
        print("Error processing the message:", str(e))
        traceback.print_exc()
        response = {'error': f'Error processing the image: {str(e)}'}
        await websocket.send(json.dumps(response))

# Start WebSocket server
async def main():
    server = await websockets.serve(process_message, "localhost", 8001)
    print("WebSocket server started on ws://localhost:8001")
    await server.wait_closed()

# Run the WebSocket server
if __name__ == '__main__':
    asyncio.run(main())
