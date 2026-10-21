# 🤖 Overhead Robot Vision Tracking System

A lightweight, self-contained Python tracking system for overhead cameras (live USB cameras, Limelight network streams, or local MP4 recordings). It converts pixel coordinates into real-world field positions (in decimal meters) and heading angles using a 2-point linear calibration model.

---

## 📁 File Structure & Tools

* 📍 **`pixel_finder.py`**: Interactive helper utility. Click anywhere on the live camera or recording frame to instantly print exact pixel coordinates `(X, Y)` to your terminal.
* 🎯 **`field_tracker.py`**: The main coordinate tracking engine. Isolates bright LED markers, translates pixel offsets into field-relative meters using your calibration, and computes the robot's heading angle.
* 💡 **`led_detector.py`**: A lightweight visual testing script that purely detects and draws contours around illuminated LEDs without calculating field positions or headings.

---

## ⚙️ Step 1: Configure Video Source & Camera Exposure

Both `pixel_finder.py` and `field_tracker.py` use a unified configuration block at the top of the script.

### 1. Select Stream Mode
Set flags to switch between live hardware streams and video recordings:

```python
CAM_INDEX = 0  
USING_LIMELIGHT = False 
USING_RECORDING = False  # Set to True when analyzing a saved MP4 file
```

### 2. Lock Manual Camera Exposure (USB Cameras Only)
To eliminate background glare and room reflections, manual exposure settings darken the background so only bright LEDs register:

```python
if not USING_RECORDING and not USING_LIMELIGHT:
    # Disable auto-exposure (0.25 or 0 forces manual control)
    capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) 
    
    # Set manual exposure (negative values produce darker images: -4, -5, -6)
    capture.set(cv2.CAP_PROP_EXPOSURE, -5)
    
    # Adjust overall frame brightness (0–255)
    capture.set(cv2.CAP_PROP_BRIGHTNESS, 120)
```

---

## 🎯 Step 2: Get Calibration Pixels (`pixel_finder.py`)

1. Place two permanent tape markers (with cross-hairs drawn in the exact center) near opposite corners inside the camera's field of view.
2. Launch `pixel_finder.py`.
3. Left-click on the center of **Tape Marker 1**, then left-click on **Tape Marker 2**.
4. Copy the printed `(X, Y)` pixel values from your terminal output.

---

## 📏 Step 3: Measure Real-World Distances (IRL)

Even if your physical field origin `(0.0, 0.0)` is off-screen outside the camera's field of view, measure the exact distance in meters from that origin corner to both tape markers:

1. **Point 1 (`P1_FIELD`)**: Distance in meters `(X_meters, Y_meters)` from the field `(0, 0)` corner to Tape Marker 1 center.
2. **Point 2 (`P2_FIELD`)**: Distance in meters `(X_meters, Y_meters)` from the field `(0, 0)` corner to Tape Marker 2 center.

> ⚠️ **Precision Tip:** Always input measurements with decimal precision (e.g., `2.15` meters instead of `2` meters) to ensure accurate spatial scaling.

---

## 🔧 Step 4: Update Calibration & Launch (`field_tracker.py`)

Open `field_tracker.py` and input your pixel clicks and physical measurements:

```python
# ============ POINTS CALIBRATION ===========
P1_PIXEL = (150, 600)       # Clicked pixel location for Point 1
P1_FIELD = (2.15, 1.08)     # Measured meters (X, Y) from field origin

P2_PIXEL = (750, 600)       # Clicked pixel location for Point 2
P2_FIELD = (5.80, 1.08)     # Measured meters (X, Y) from field origin
# ============================================
```

Run `field_tracker.py` to stream live field coordinates and heading calculations:

```text
X: 3.42m | Y: 1.50m | Heading: 42.5 deg
```

Press `q` or `ESC` inside the video display window to exit the application.