import argparse
import datetime
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=400, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.15)
else:
    camera = cv2.VideoCapture(args["video"])

firstFrame = None
curr_time = None

while True:
    (grabbed, frame) = camera.read()
    text = "Unoccupied"

    if not grabbed:
        break
    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (19, 21), 0)
    if firstFrame is None:
        firstFrame = gray
        continue
    if curr_time is None:
        curr_time = time.time()

    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 250, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=1)
    cnts, val, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)

    if len(val) > 0:
        for c in val:
            if cv2.contourArea(contour=c) < args["min_area"]:
                continue
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF
    if int(curr_time - time.time()) <= -59:
        curr_time = None
        firstFrame = None
    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
