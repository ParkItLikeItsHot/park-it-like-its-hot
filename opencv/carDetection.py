from PIL import Image
import cv2 as cv
import numpy as np

# load the pre-trained Haar Cascade classifier for car detection
car_cascade = cv.CascadeClassifier("cars.xml")

# Check if the cascade file loaded successfully
if car_cascade.empty():
    raise Exception(
        "Error loading Haar cascade file. Make sure 'cars.xml' is in the correct path."
    )

# Read the image or video frame

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for cascade detection, blur it, and dilate it
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5, 5), 0)
    dilated = cv.dilate(blur, np.ones((3, 3)))
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (2, 2))
    closing = cv.morphologyEx(dilated, cv.MORPH_CLOSE, kernel)

    # Detect cars in the grayscale image
    cars = car_cascade.detectMultiScale(
        closing, scaleFactor=1.1, minNeighbors=4, minSize=(70, 70)
    )
    # Draw rectangles around the detected cars
    # x, y is the top left corner, w, h is width and height of the rectangle

    for x, y, w, h in cars:
        cv.rectangle(
            frame, (x, y), (x + w, y + h), (0, 255, 0), 2
        )  # Green rectangle, thickness 2
        cv.imshow("Car Detection", frame)

        cv.putText(
            frame, "Car", (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2
        )

    # Display the result
    # Break the loop on 'q' key press
    if cv.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv.destroyAllWindows()
