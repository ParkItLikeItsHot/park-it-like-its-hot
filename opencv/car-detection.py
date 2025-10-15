import cv2

# Load the pre-trained car cascade classifier
# You'll need to download 'cars.xml' (or a similar cascade)
# from the OpenCV GitHub repository or other sources.
car_cascade = cv2.CascadeClassifier('cars.xml') 

# Check if the cascade file loaded successfully
if car_cascade.empty():
    raise Exception("Error loading Haar cascade file. Make sure 'cars.xml' is in the correct path.")

# Read the image or video frame
# For an image:
# img = cv2.imread('car_image.jpg') 
# For a video frame (within a loop):
cap = cv2.VideoCapture(0) # or 0 for webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for cascade detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect cars in the grayscale image
    # detectMultiScale(image, scaleFactor, minNeighbors)
    # scaleFactor: Parameter specifying how much the image size is reduced at each image scale.
    # minNeighbors: Parameter specifying how many neighbors each candidate rectangle should have to retain it.
    cars = car_cascade.detectMultiScale(gray, 1.1, 3)

    # Draw rectangles around the detected cars
    for (x, y, w, h) in cars:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Green rectangle, thickness 2

    # Display the result
    cv2.imshow('Car Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()