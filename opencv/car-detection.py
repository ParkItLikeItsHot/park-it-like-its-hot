import cv2

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


def find_center_x(x, w):
    return (x + (w // 2))

center_x_list = [None, None, None]
previous_center_x = None


cars_detected = 0


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for cascade detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect cars in the grayscale image
    cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60))
    print(f"Detected {cars} cars")
    
    if len(cars) != 0:
        cars_detected += len(cars)
    
    print(f"Detected {len(cars)} cars")
    print(f"Car coordinates: {cars}")
    # Draw rectangles around the detected cars
    # x, y is the top left corner, w, h is width and height of the rectangle
    

    for (x, y, w, h) in cars:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Green rectangle, thickness 2
        current_center_x = int(find_center_x(x, w))
        print(f"Center X of car: {current_center_x}")

        # compute delta against previous center if available
        center_x_list.append(current_center_x)
        # keep last 3 values
        center_x_list = center_x_list[-3:]

        center_x_delta = None
        direction = 'unknown'
        if previous_center_x is not None:
            center_x_delta = current_center_x - previous_center_x
            if center_x_delta > 0:
                direction = 'right'
            elif center_x_delta < 0:
                direction = 'left'
            else:
                direction = 'stationary'

        # log delta and direction
        print(f"center_x_delta: {center_x_delta}, direction: {direction}")

        # update previous_center_x for next detection
        previous_center_x = current_center_x
    

    # Display the result
    cv2.imshow('Car Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
print(f"Total cars detected during session: {cars_detected}")