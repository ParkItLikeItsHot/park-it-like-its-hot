import cv2
import math
import threading
import base64
import json
import boto3
from flask import Flask, jsonify

# --- Flask App Initialization ---
app = Flask(__name__)

# Try to enable CORS if flask_cors is available
try:
    from flask_cors import CORS

    CORS(app)
    print("flask_cors detected — CORS enabled for Flask app")
except Exception:
    print(
        "flask_cors not installed. If you get CORS errors in the browser, install it with: pip install flask-cors"
    )

# --- SageMaker Configuration ---
SAGEMAKER_ENDPOINT_NAME = "car-detection-endpoint"  # Update with your endpoint name
AWS_REGION = "us-east-1"  # Update with your region

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)


def detect_cars_sagemaker(frame):
    """Send frame to SageMaker for car detection"""
    try:
        # Encode frame as base64
        _, buffer = cv2.imencode(".jpg", frame)
        image_base64 = base64.b64encode(buffer).decode("utf-8")

        # Prepare payload
        payload = json.dumps({"image": image_base64})

        # Call SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=SAGEMAKER_ENDPOINT_NAME,
            ContentType="application/json",
            Accept="application/json",
            Body=payload,
        )

        # Parse response
        result = json.loads(response["Body"].read().decode())
        return result["detections"]

    except Exception as e:
        print(f"Error calling SageMaker: {e}")
        return []  # Fallback to empty list


# --- Car Detection and Tracking variables ---
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

        # Age all tracked objects
        for obj in tracked_objects:
            obj["frames_since_seen"] += 1

        # Use SageMaker for car detection instead of local OpenCV
        detections = detect_cars_sagemaker(frame)

        current_detections = []
        for x, y, w, h in detections:
            center_x = x + w // 2
            center_y = y + h // 2
            current_detections.append(
                {"box": (x, y, w, h), "center": (center_x, center_y)}
            )

        # Match detections to existing tracked objects
        for detection in current_detections:
            found_match = False
            for obj in tracked_objects:
                dist = math.hypot(
                    obj["center"][0] - detection["center"][0],
                    obj["center"][1] - detection["center"][1],
                )
                if dist < DIST_THRESHOLD:
                    obj["delta_x"] = detection["center"][0] - obj["center"][0]
                    obj["center"] = detection["center"]
                    obj["box"] = detection["box"]
                    obj["frames_since_seen"] = 0
                    found_match = True
                    break

            if not found_match:
                tracked_objects.append(
                    {
                        "id": next_object_id,
                        "box": detection["box"],
                        "crossed": False,
                        "list_of_directions": [],
                        "center": detection["center"],
                        "frames_since_seen": 0,
                        "delta_x": 0,
                    }
                )
                next_object_id += 1

        # Check for objects crossing the tracking line
        for obj in tracked_objects:
            (x, y, w, h) = obj["box"]
            obj_center_x = x + w // 2

            # Draw tracking line
            cv2.line(
                frame, (tracking_line_x, 0), (tracking_line_x, height), (255, 0, 0), 2
            )

            # Check if the object has crossed the line
            if (
                abs(obj_center_x - tracking_line_x) < 20
                and obj["frames_since_seen"] == 0
                and not obj["crossed"]
            ):
                obj["crossed"] = True
                print(f"Object ID {obj['id']} crossed the line.")

                if obj["list_of_directions"] and len(obj["list_of_directions"]) > 15:
                    avg_direction = sum(obj["list_of_directions"]) / len(
                        obj["list_of_directions"]
                    )
                    if avg_direction > 0:
                        print(
                            f"Object ID {obj['id']} is moving Right, one car added to parking lot."
                        )
                        cars_in_parking_lot += 1
                    elif avg_direction < 0:
                        print(
                            f"Object ID {obj['id']} is moving Left, one car removed from parking lot."
                        )
                        cars_in_parking_lot -= 1

        # Remove old tracks
        tracked_objects = [
            obj for obj in tracked_objects if obj["frames_since_seen"] < FRAMES_TO_LIVE
        ]

        # Draw rectangles and IDs for tracked objects
        for obj in tracked_objects:
            (x, y, w, h) = obj["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID: {obj['id']}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

            direction = ""
            if obj.get("delta_x", 0) > 2:
                direction = "Right"
                obj.setdefault("list_of_directions", []).append(1)
            elif obj.get("delta_x", 0) < -2:
                direction = "Left"
                obj.setdefault("list_of_directions", []).append(-1)

            if direction:
                cv2.putText(
                    frame,
                    direction,
                    (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    2,
                )

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print(f"Total cars in parking lot: {cars_in_parking_lot}")


# --- API Endpoint ---
@app.route("/cars-in-parking-lot", methods=["GET"])
def get_cars_in_parking_lot():
    """
    This endpoint returns the current number of cars in the parking lot.
    """
    return jsonify({"cars_in_parking_lot": cars_in_parking_lot})


# --- Main Execution ---
if __name__ == "__main__":
    # Create and start the car detection thread
    detection_thread = threading.Thread(target=run_car_detection)
    detection_thread.daemon = True
    detection_thread.start()

    # Run the Flask app
    app.run(host="0.0.0.0", port=6767, debug=True, use_reloader=False)
