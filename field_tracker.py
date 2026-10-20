import cv2
import numpy as np
import math

CAM_INDEX = 0

# ===== CONFIGURATION (check before running) =====
USING_LIMELIGHT = False
USING_RECORDING = False
# If both are False it defaults to the camera stream

LIMELIGHT_URL = "http://10.0.127.18:5802"
RECORDING_PATH = "recording_20260930_185231.mp4"

BRIGHTNESS_THRESH = 100
MIN_AREA = 0

# ============ POINTS CALIBRATION ===========
P1_PIXEL = (150, 600)
P1_FIELD = (0.0, 0.0)
P2_PIXEL = (750, 600)
P2_FIELD = (4.0, 0.0)
# ============================================

pixel_distance = math.hypot(
    P2_PIXEL[0] - P1_PIXEL[0], P2_PIXEL[1] - P1_PIXEL[1])
field_distance = math.hypot(
    P2_FIELD[0] - P1_FIELD[0], P2_FIELD[1] - P1_FIELD[1])
PIXELS_PER_METER = pixel_distance / \
    field_distance if field_distance > 0 else 100.0

ORIGIN_PIXEL_X = P1_PIXEL[0]
ORIGIN_PIXEL_Y = P1_PIXEL[1]
FIELD_ORIGIN_X = P1_FIELD[0]
FIELD_ORIGIN_Y = P1_FIELD[1]

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
    print("Error opening video stream.")
    exit()

while True:
    ret, frame = capture.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, BRIGHTNESS_THRESH, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    led_points = []
    for c in contours:
        if cv2.contourArea(c) > MIN_AREA:
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + (w // 2), y + (h // 2)
            led_points.append((cx, cy))
            cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

    if len(led_points) >= 2:
        led_points.sort(key=lambda pt: pt[0])

        position_px = led_points[0]
        heading_px = led_points[1]

        field_x = FIELD_ORIGIN_X + \
            (position_px[0] - ORIGIN_PIXEL_X) / PIXELS_PER_METER
        field_y = FIELD_ORIGIN_Y + \
            (ORIGIN_PIXEL_Y - position_px[1]) / PIXELS_PER_METER

        dx = heading_px[0] - position_px[0]
        dy = heading_px[1] - position_px[1]
        heading_rad = math.atan2(dy, dx)

        print(
            f"X: {field_x:.2f}m | Y: {field_y:.2f}m | Heading: {math.degrees(heading_rad):.1f} deg")

    cv2.imshow(window_name, frame)

    # Wait until either 'q' is pressed or the escape key
    key = cv2.waitKey(frame_delay) & 0xFF
    if key == ord('q') or key == 27:
        break

capture.release()
cv2.destroyAllWindows()
