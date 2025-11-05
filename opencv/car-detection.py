import cv2
import math
import threading
from flask import Flask, jsonify

# --- Flask App Initialization ---
app = Flask(__name__)

# Try to enable CORS if flask_cors is available. This is non-fatal: if
# flask_cors isn't installed we print guidance instead of crashing.
try:
    from flask_cors import CORS
    CORS(app)
    print("flask_cors detected — CORS enabled for Flask app")
except Exception:
    print("flask_cors not installed. If you get CORS errors in the browser, install it with: pip install flask-cors")

# --- Car Detection and Tracking variables ---
# Face detection for testing
car_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
# load the pre-trained Haar Cascade classifier for car detection
# car_cascade = cv2.CascadeClassifier('cars.xml')

# Check if the cascade file loaded successfully
if car_cascade.empty():
    raise Exception("Error loading Haar cascade file. Make sure 'cars.xml' is in the correct path.")

# Read the image or video frame
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# --- Tracking variables ---
tracked_objects = []
next_object_id = 0
# Max distance in pixels to consider a detection the same object
DIST_THRESHOLD = 75
# Max number of frames to keep tracking an object without seeing it
FRAMES_TO_LIVE = 10
cars_in_parking_lot = 0

# --- Car Detection Logic in a separate thread ---
def run_car_detection():
    """
    This function runs the car detection and tracking logic in a loop.
    It's designed to be run in a separate thread.
    """
    global cars_in_parking_lot, next_object_id, tracked_objects
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width = frame.shape[:2]
        tracking_line_x = width // 2
        # Convert the frame to grayscale for cascade detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Age all tracked objects. If an object is not seen in the current frame,
        # this counter will increase.
        for obj in tracked_objects:
            obj['frames_since_seen'] += 1

        # Detect cars in the grayscale image
        detections = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        current_detections = []
        for (x, y, w, h) in detections:
            center_x = x + w // 2
            center_y = y + h // 2
            current_detections.append({'box': (x, y, w, h), 'center': (center_x, center_y)})

        # Match detections to existing tracked objects
        for detection in current_detections:
            found_match = False
            for obj in tracked_objects: # Create a distance value with hypotenuse from the center points of the tracked object (from last frame) and the detected object (from current frame)
                dist = math.hypot(obj['center'][0] - detection['center'][0], obj['center'][1] - detection['center'][1])
                if dist < DIST_THRESHOLD:
                    # This is the same object
                    obj['delta_x'] = detection['center'][0] - obj['center'][0]
                    obj['center'] = detection['center']
                    obj['box'] = detection['box']
                    obj['frames_since_seen'] = 0
                    found_match = True
                    break
            
            if not found_match:
                # This is a new object
                tracked_objects.append({
                    'id': next_object_id,
                    'box': detection['box'],
                    'crossed': False,
                    'list_of_directions': [],
                    'center': detection['center'],
                    'frames_since_seen': 0,
                    'delta_x': 0
                })
                next_object_id += 1

        # Check for objects crossing the tracking line
        for obj in tracked_objects:
            (x, y, w, h) = obj['box']
            obj_center_x = x + w // 2

            # Draw tracking line
            cv2.line(frame, (tracking_line_x, 0), (tracking_line_x, height), (255, 0, 0), 2)
            # Check if the object has crossed the line
            if abs(obj_center_x - tracking_line_x) < 20 and obj['frames_since_seen'] == 0 and not obj['crossed']: #only tracks if it is currently within 20 pixels of tracking line
                obj['crossed'] = True # ensures we only count once
                print(f"Object ID {obj['id']} crossed the line.")

                # average out the list of directions and check if it is positive or negative
                if obj['list_of_directions'] and len(obj['list_of_directions']) > 15: #ensures only counts if there is enough data to make a decision, filtering out random objects
                    avg_direction = sum(obj['list_of_directions']) / len(obj['list_of_directions'])
                    if avg_direction > 0:
                        print(f"Object ID {obj['id']} is moving Right, one car added to parking lot.")
                        cars_in_parking_lot += 1
                    elif avg_direction < 0:
                        print(f"Object ID {obj['id']} is moving Left, one car removed from parking lot.")
                        cars_in_parking_lot -= 1

        # Remove old tracks that haven't been seen for a while
        tracked_objects = [obj for obj in tracked_objects if obj['frames_since_seen'] < FRAMES_TO_LIVE]

        # Draw rectangles and IDs for tracked objects
        for obj in tracked_objects:
            (x, y, w, h) = obj['box']
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {obj['id']}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            direction = ""
            # A small threshold to prevent jitter from being reported as movement
            if obj.get('delta_x', 0) > 2:
                direction = "Right"
                obj.setdefault('list_of_directions', []).append(1)

            elif obj.get('delta_x', 0) < -2:
                direction = "Left"
                obj.setdefault('list_of_directions', []).append(-1)
            
            if direction:
                # Display the direction below the bounding box
                cv2.putText(frame, direction, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) #temporary, don't need visuals

        # Display the result
        #cv2.imshow('Object Tracking', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print(f"Total cars in parking lot: {cars_in_parking_lot}")

# --- API Endpoint ---
@app.route('/cars-in-parking-lot', methods=['GET'])
def get_cars_in_parking_lot():
    """
    This endpoint returns the current number of cars in the parking lot.
    """
    return jsonify({'cars_in_parking_lot': cars_in_parking_lot})

# --- Main Execution ---
if __name__ == '__main__':
    # Create and start the car detection thread
    detection_thread = threading.Thread(target=run_car_detection)
    detection_thread.daemon = True
    detection_thread.start()

    # Run the Flask app
    # use_reloader=False is important to prevent the script from running twice
    app.run(host='0.0.0.0', port=6767, debug=True, use_reloader=False)