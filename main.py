from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils

# import RPi.GPIO as gpio
import argparse
import imutils
import time
import dlib
import cv2

cnt = 0
total = 0
font = cv2.FONT_HERSHEY_SIMPLEX

def eye_aspect_ratio(eye):
	return (dist.euclidean(eye[1], eye[5]) + dist.euclidean(eye[2], eye[4]))/(dist.euclidean(eye[0], eye[3])*2)

def arg_parse():
	parse = argparse.ArgumentParser()
	parse.add_argument("-p", dest = 'predict', default="shape_predictor_68_face_landmarks.dat", help="shape predictor file")
	parse.add_argument("-t", dest = 'threshold', default=0.2, type=float)
	parse.add_argument("-f", dest = 'frames',default=2, type=int)
	return parse.parse_args()

def grayscale(image):
	 return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def eyes(srt, end):
	EYE = shape[srt:end]
	EAR = eye_aspect_ratio(EYE)
	return EYE, EAR

args = arg_parse()
eye_thresh = args.threshold
eye_frames = args.frames
eye_predict = args.predict

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(eye_predict)

(l_srt, l_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(r_srt, r_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

cap = cv2.VideoCapture(0)

while cap.isOpened():
	_, frame = cap.read()
	gray = grayscale(frame)

	width, height = frame.shape[:2]
	whalf, hhalf = int(width/2), int(height/2)

	for rect in detector(gray, 0):
		shape = face_utils.shape_to_np(predictor(gray, rect))

		l_eye, l_ear = eyes(l_srt, l_end)
		r_eye, r_ear = eyes(r_srt, r_end)
		m_ear = (l_ear + r_ear) / 2.0
		print(m_ear, end = "\b\b\b\b\b")

		cv2.drawContours(frame, [cv2.convexHull(l_eye)], -1, (0, 255, 0), 1, maxLevel=1)
		cv2.drawContours(frame, [cv2.convexHull(r_eye)], -1, (0, 255, 0), 1, maxLevel=1)

		if ear < eye_thresh:
			cnt += 1
			if cnt > 60:
				cv2.putText(frame, "Dont Sleep", (whalf, hhalf), font, 1, (0, 0, 255), 2)
				print("\nDont Sleep")
		else:
			if cnt >= eye_frames:
				total += 1
			cnt = 0
		# cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), font, 0.7, (0, 0, 255), 2)

	cv2.imshow("Frame", frame)
	if cv2.waitKey(1) & 0xFF == ord("q"):
		break

cap.release()
cv2.destroyAllWindows()