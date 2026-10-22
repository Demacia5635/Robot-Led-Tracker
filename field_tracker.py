import cv2
import numpy as np
import math

CAM_INDEX = 0

USING_LIMELIGHT = False
USING_RECORDING = False

LIMELIGHT_URL = "http://10.0.127.18:5802"
RECORDING_PATH = r"recording_20260930_185231.mp4"

if USING_RECORDING:
    stream_type = RECORDING_PATH
    window_name = "Tracking Stream"
    frame_delay = 30
elif USING_LIMELIGHT:
    stream_type = LIMELIGHT_URL
    window_name = "Tracking Stream"
    frame_delay = 1
else:
    stream_type = CAM_INDEX
    window_name = "Tracking Stream"
    frame_delay = 1

if not USING_RECORDING and not USING_LIMELIGHT:
    capture = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
else:
    capture = cv2.VideoCapture(stream_type)

if not capture.isOpened():
    print("Error opening video stream.")
    exit()

# Control window
control_window = "Camera Controls"
cv2.namedWindow(control_window)


def nothing(x):
    pass


cv2.createTrackbar("Exposure (-10 to 0)", control_window, 5, 10, nothing)
cv2.createTrackbar("Brightness", control_window, 120, 255, nothing)
cv2.createTrackbar("Threshold", control_window, 100, 255, nothing)
cv2.createTrackbar("Min Area", control_window, 0,
                   100, nothing)  # Default set to 0

last_exp = -1
last_bright = -1

# ============ POINTS CALIBRATION ===========
# 1. Get pixels from pixel_finder.py
# 2. Measure physical meters from field (0,0) corner
P1_PIXEL = (540, 422)       # Clicked pixel coordinates for Point 1
P1_FIELD = (5.35, 1.35)     # Real world meters for Point 1

P2_PIXEL = (90, 220)        # Clicked pixel coordinates for Point 2
P2_FIELD = (7.63, 1.7)      # Real world meters for Point 2
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

while True:
    ret, frame = capture.read()
    if not ret:
        break

    exp_slider = cv2.getTrackbarPos("Exposure (-10 to 0)", control_window)
    brightness_val = cv2.getTrackbarPos("Brightness", control_window)
    thresh_val = cv2.getTrackbarPos("Threshold", control_window)
    min_area_val = cv2.getTrackbarPos("Min Area", control_window)

    # only send slider commands if the sliders were actually moved
    if not USING_RECORDING and not USING_LIMELIGHT:
        real_exposure = exp_slider - 10
        if real_exposure != last_exp or brightness_val != last_bright:
            capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            capture.set(cv2.CAP_PROP_EXPOSURE, real_exposure)
            capture.set(cv2.CAP_PROP_BRIGHTNESS, brightness_val)
            last_exp = real_exposure
            last_bright = brightness_val

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    led_points = []
    for C in contours:
        if cv2.contourArea(C) > min_area_val:
            X, Y, W, H = cv2.boundingRect(C)
            cx, cy = X + (W // 2), Y + (H // 2)
            led_points.append((cx, cy))
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)

    if len(led_points) >= 2:
        led_points.sort(key=lambda pt: pt[0])
        position_px = led_points[0]
        heading_px = led_points[1]

        field_x = FIELD_ORIGIN_X + \
            (position_px[0] - ORIGIN_PIXEL_X) / PIXELS_PER_METER
        field_y = FIELD_ORIGIN_Y + \
            (ORIGIN_PIXEL_Y - position_px[1]) / PIXELS_PER_METER

        dx = heading_px[0] - position_px[0]
        dy = position_px[1] - heading_px[1]
        heading_deg = math.degrees(math.atan2(dy, dx))

        info_text = f"X: {field_x:.2f}m | Y: {field_y:.2f}m | Heading: {heading_deg:.1f} deg"
    else:
        info_text = "Searching for LEDs..."

    cv2.putText(frame, info_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow(window_name, frame)

    key = cv2.waitKey(frame_delay) & 0xFF
    if key == ord('q') or key == 27:
        break

capture.release()
cv2.destroyAllWindows()
