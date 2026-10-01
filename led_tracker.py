import cv2
import numpy as np

CAM_INDEX = 0  
USING_LIMELIGHT = False 
USING_RECORDING = True
LIMELIGHT_URL = "http://10.0.127.18:5802"
RECORDING_PATH = "recording_20260930_185231.mp4"

BRIGHTNESS_THRESH = 100
MIN_AREA = 0

if USING_RECORDING:
    stream_type = RECORDING_PATH
    window_name = "Recording Stream"
    frame_delay = 30
elif USING_LIMELIGHT:
    stream_type = LIMELIGHT_URL
    window_name = "Limelight Stream"
    frame_delay = 1
else:
    stream_type = CAM_INDEX
    window_name = "Camera Stream"
    frame_delay = 1

capture = cv2.VideoCapture(stream_type)

if not capture.isOpened():
    print(f"Error: Cannot open stream at {stream_type}")
    exit()

while True:
    ret, frame = capture.read()
    if not ret:
        print("End of video or failed to get frame")
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    _, thresh = cv2.threshold(gray_frame, BRIGHTNESS_THRESH, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    led_centers = []

    for c in contours:
        area = cv2.contourArea(c)

        if area > MIN_AREA:
            x, y, w, h = cv2.boundingRect(c)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            center_x = x + (w // 2)
            center_y = y + (h // 2)
            led_centers.append((center_x, center_y))

            cv2.circle(frame, (center_x, center_y), 1, (0, 0, 255), -1)

    cv2.imshow(window_name, frame)
    cv2.imshow("Threshold Mask", thresh)

    # Wait until either the escape key is pressed or 'q'.
    key = cv2.waitKey(frame_delay) & 0xFF
    if key == ord('q') or key == 27:
        break

capture.release()
cv2.destroyAllWindows()