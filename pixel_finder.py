import cv2

# A tool to find the pixel coordinates of points in a video stream or recording


CAM_INDEX = 1
USING_LIMELIGHT = False
USING_RECORDING = False

LIMELIGHT_URL = "http://10.0.127.18:5802"
RECORDING_PATH = r"C:\Users\liorp\Projects\roboticsTesting\VisionTesting\recording_20260930_185231.mp4"

if USING_RECORDING:
    stream_type = RECORDING_PATH
    window_name = "Pixel Finder - Recording"
    frame_delay = 30
elif USING_LIMELIGHT:
    stream_type = LIMELIGHT_URL
    window_name = "Pixel Finder - Limelight"
    frame_delay = 1
else:
    stream_type = CAM_INDEX
    window_name = "Pixel Finder - Camera"
    frame_delay = 1

capture = cv2.VideoCapture(stream_type)

if not capture.isOpened():
    print("Error opening video stream.")
    exit()


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked Pixel -> X: {x}, Y: {y}")


cv2.namedWindow(window_name)
cv2.setMouseCallback(window_name, mouse_callback)

while True:
    ret, frame = capture.read()
    if not ret:
        break

    cv2.imshow(window_name, frame)

    key = cv2.waitKey(frame_delay) & 0xFF
    if key == ord('q') or key == 27:
        break

capture.release()
cv2.destroyAllWindows()
