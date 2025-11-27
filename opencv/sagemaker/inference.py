import json
import cv2
import numpy as np
import base64
from io import BytesIO


def model_fn(model_dir):
    """Load the Haar Cascade classifier"""
    car_cascade = cv2.CascadeClassifier("cars.xml")
    if car_cascade.empty():
        # Fallback to face detection for testing
        car_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
    return car_cascade


def input_fn(request_body, content_type):
    """Parse input data"""
    if content_type == "application/json":
        data = json.loads(request_body)
        # Decode base64 image
        image_data = base64.b64decode(data["image"])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return frame
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def predict_fn(input_data, model):
    """Run car detection"""
    gray = cv2.cvtColor(input_data, cv2.COLOR_BGR2GRAY)
    detections = model.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if isinstance(detections, tuple):
        return []
    return detections.tolist()


def output_fn(prediction, accept):
    """Format output"""
    if accept == "application/json":
        return json.dumps({"detections": prediction}), accept
    else:
        raise ValueError(f"Unsupported accept type: {accept}")
