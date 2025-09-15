import cv2
import os

dataset_path = './GestureTraining/DatasetUnlabeled'
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

cap = cv2.VideoCapture(0)

frame_number = len(os.listdir(dataset_path)) + 1

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Webcam', frame)
        # Press 's' to save frame
        if cv2.waitKey(1) & 0xFF == ord('s'):
        
            filename = f'{dataset_path}/frame_{frame_number}.jpg'
            cv2.imwrite(filename, frame)
            frame_number += 1 
        elif cv2.waitKey(1) & 0xFF == ord('q'): #Press 'q' to quit
            break

cap.release()
cv2.destroyAllWindows()
