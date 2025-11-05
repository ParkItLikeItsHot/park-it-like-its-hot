import cv2 as cv

img = cv.VideoCapture(0)

if not img.isOpened():
    print("Error: Could not open webcam.")
    exit()

face_classifier = cv.CascadeClassifier(
    cv.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_bounding_box(vid):
    gray_image = cv.cvtColor(vid, cv.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    for (x, y, w, h) in faces:
        cv.rectangle(vid, (x, y), (x + w, y + h), (0, 255, 0), 4)
    return faces

while True:
    ret, frame = img.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    detect_bounding_box(frame)
    cv.imshow('Webcam', frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

img.release()
cv.destroyAllWindows()
