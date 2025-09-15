import asyncio
import websockets
import threading
import json
import numpy as np
import cv2
import joblib
import base64
from io import BytesIO
from PIL import Image
import mediapipe as mp
from scipy.signal import resample
import traceback
from RealtimeSTT import AudioToTextRecorder as STTC

gesture_model = joblib.load('sign_language_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

recorder = None
recorder_ready = threading.Event()
client_websocket = None
gesture_websocket = None
main_event_loop = None 

def decode_image(data_url):
    try:
        img_data = base64.b64decode(data_url.split(',')[1])
        img = Image.open(BytesIO(img_data))
        return np.array(img)
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def extract_landmarks(image):
    result = hands.process(image)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            return np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
    return None

async def send_audio_to_client(message, websocket):
    try:
        await websocket.send(message)
    except Exception as e:
        print(f"Error sending audio message: {e}")

def text_detected(text):
    try:

        if client_websocket:
            asyncio.run_coroutine_threadsafe(
                send_audio_to_client(
                    json.dumps({
                        'type': 'realtime',
                        'text': text
                    }),
                    client_websocket
                ),
                main_event_loop
            )
        print(f"\r{text}", flush=True, end='')
    except Exception as e:
        print(f"Error in text_detected: {e}")

recorder_config = {
    'spinner': False,
    'use_microphone': False,
    'model': 'large-v2',
    'language': 'id',
    'device': 'cpu',
    'silero_sensitivity': 0.4,
    'webrtc_sensitivity': 2,
    'post_speech_silence_duration': 0.7,
    'batch_size': 16,
    'realtime_batch_size': 6,
    'min_length_of_recording': 0,
    'min_gap_between_recordings': 0,
    'enable_realtime_transcription': True,
    'realtime_processing_pause': 0,
    'realtime_model_type': 'base',
    'on_realtime_transcription_stabilized': text_detected,
    'no_log_file': True
}

def recorder_thread():
    global recorder
    print("Initializing RealtimeSTT...")
    asyncio.set_event_loop(asyncio.new_event_loop()) 
    thread_event_loop = asyncio.get_event_loop()

    recorder = STTC(**recorder_config)
    print("RealtimeSTT initialized")
    recorder_ready.set()

    while True:
        try:
            full_sentence = recorder.text()
            asyncio.run_coroutine_threadsafe(
                send_audio_to_client(
                    json.dumps({
                        'type': 'fullSentence',
                        'text': full_sentence
                    }),
                    client_websocket
                ),
                main_event_loop
            )
            print(f"\rSentence: {full_sentence}")
        except Exception as e:
            print(f"Error in recorder thread: {e}")

def decode_and_resample(audio_data, original_sample_rate, target_sample_rate):
    try:
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        num_original_samples = len(audio_np)
        num_target_samples = int(num_original_samples * target_sample_rate / original_sample_rate)
        resampled_audio = resample(audio_np, num_target_samples)
        return resampled_audio.astype(np.int16).tobytes()
    except Exception as e:
        print(f"Error in resampling: {e}")
        return audio_data

async def echo_audio(websocket):
    print("Audio client connected")
    global client_websocket
    client_websocket = websocket

    async for message in websocket:
        if not recorder_ready.is_set():
            print("Recorder not ready")
            continue
        try:
            metadata_length = int.from_bytes(message[:4], byteorder='little')
            metadata_json = message[4:4 + metadata_length].decode('utf-8')
            metadata = json.loads(metadata_json)
            sample_rate = metadata['sampleRate']
            chunk = message[4 + metadata_length:]
            resampled_chunk = decode_and_resample(chunk, sample_rate, 16000)
            recorder.feed_audio(resampled_chunk)
        except Exception as e:
            print(f"Error in audio echo: {e}")

async def send_gesture_to_client(message, websocket):
    try:
        await websocket.send(message)
    except Exception as e:
        print(f"Error sending gesture message: {e}")

async def echo_gesture(websocket):
    print("Gesture client connected")
    global gesture_websocket
    gesture_websocket = websocket

    async for message in websocket:
        try:
            print("Received message for gesture")
            data = json.loads(message)
            img_data_url = data['image']
            
            img = decode_image(img_data_url)
            if img is None:
                print("Failed to decode image.")
                response = {'error': 'Failed to decode image'}
                await send_gesture_to_client(json.dumps(response), gesture_websocket)
                continue

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            landmarks = extract_landmarks(img_rgb)
            if landmarks is None:
                print("No landmarks detected.")
                response = {'error': 'No hand detected'}
                await send_gesture_to_client(json.dumps(response), gesture_websocket)
                continue

            print("Landmarks detected:", landmarks)

            prediction = gesture_model.predict([landmarks])
            print("Prediction:", prediction)

            predicted_label = label_encoder.inverse_transform(prediction)

            response = {'prediction': predicted_label[0]}
            await send_gesture_to_client(json.dumps(response), gesture_websocket)
        except Exception as e:
            print(f"Error in gesture echo: {e}")
            traceback.print_exc()

async def main():
    global main_event_loop
    main_event_loop = asyncio.get_event_loop() 
    start_server_audio = await websockets.serve(echo_audio, "localhost", 8001)
    start_server_gesture = await websockets.serve(echo_gesture, "localhost", 8002)

    recorder_thread_instance = threading.Thread(target=recorder_thread, daemon=True)
    recorder_thread_instance.start()
    recorder_ready.wait()

    print("Server started. Press Ctrl+C to stop the server.")
    await asyncio.gather(start_server_audio.wait_closed(), start_server_gesture.wait_closed())

if __name__ == '__main__':
    print("Starting server, please wait...")
    asyncio.run(main())
