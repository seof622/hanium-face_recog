import dlib
import cv2
import numpy as np

# create list for landmarks
ALL = list(range(0, 68))
RIGHT_EYEBROW = list(range(17, 20))
LEFT_EYEBROW = list(range(20, 23))
RIGHT_EYE = list(range(32, 40))
LEFT_EYE = list(range(40, 48))
NOSE = list(range(23, 32))
MOUTH_OUTLINE = list(range(48, 61))
MOUTH_INNER = list(range(61, 68))
JAWLINE = list(range(0, 17))


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

count = 0

vid_in = cv2.VideoCapture(0,cv2.CAP_DSHOW)

face_id = input('\n enter user Name end press <return> ==>  ')
print("\n [INFO] Initializing face capture. Look the camera and wait ...")

while True:
    # Get frame from video
    # get success : ret = True / fail : ret= False
    ret, image_o = vid_in.read()

   # resize the video
    image = cv2.resize(image_o, dsize=(640, 480), interpolation=cv2.INTER_AREA)
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_detector = detector(img_gray, 1)

    print("The number of faces detected : {}".format(len(face_detector)))

    for face in face_detector:
        count += 1
        # face wrapped with rectangle
        cv2.rectangle(image, (face.left(), face.top()), (face.right(), face.bottom()),
                      (0, 0, 255), 3)
        cv2.imwrite("Gathering_Data/User." + str(face_id) + '.' + str(count) + ".jpg",
                    img_gray[face.top():face.bottom(), face.left():face.right()])

        # make prediction and transform to numpy array
        landmarks = predictor(image, face)  # 얼굴에서 68개 점 찾기

        #create list to contain landmarks
        landmark_list = []

        # append (x, y) in landmark_list
        for p in landmarks.parts():
            landmark_list.append([p.x, p.y])
            cv2.circle(image, (p.x, p.y), 2, (0, 255, 0), -1)


    cv2.imshow('result', image)

    # wait for keyboard input
    key = cv2.waitKey(1)

    # if esc,
    if key == 27:
        break
    elif count >= 1:  # Take 30 face sample and stop video
        break
vid_in.release()