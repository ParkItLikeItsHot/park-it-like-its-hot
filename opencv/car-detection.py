import cv2

# load the pre-trained Haar Cascade classifier for car detection
car_cascade = cv2.CascadeClassifier('cars.xml') 

# Check if the cascade file loaded successfully
if car_cascade.empty():
    raise Exception("Error loading Haar cascade file. Make sure 'cars.xml' is in the correct path.")

# Read the image or video frame
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()


def find_center_x(x, w):
    return (x + (w // 2))

center_x_list = [0, 0, 0]




while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for cascade detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect cars in the grayscale image
    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60))
    print(f"Detected {len(cars)} cars")
    print(f"Car coordinates: {cars}")
    # Draw rectangles around the detected cars
    # x, y is the top left corner, w, h is width and height of the rectangle
    

    for (x, y, w, h) in cars:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Green rectangle, thickness 2
        print(f"Center X of car: {find_center_x(x, w)}")
        center_x_list.append(int(find_center_x(x, w)))
        print(f"Center X list: {center_x_list}")
    

    # Display the result
    cv2.imshow('Car Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()