import face_recognition
import numpy as np
import os

class encoding_csv():

    face_names = []
    face_encodings = []

    Image_dir = "./encoding_image"

    files = os.listdir(Image_dir)
    for filename in files:
        name, ext = os.path.splitext(filename)
        if ext == '.jpg':
            full_name = os.path.join(Image_dir, filename)
            face_encoding_img = face_recognition.load_image_file(full_name)
            face_encoding = face_recognition.face_encodings(face_encoding_img,model= 'small')
            encoding_np = face_encoding
            ###인코딩 값 csv에 쓰기
            np.savetxt("./encoding_list/" + name + ".csv",encoding_np,delimiter=',')
    """
    ###인코딩 값 csv에서 추출하기
    face_encoding = np.loadtxt("./set_danger/encoding/test.csv",delimiter = ",")
    print(face_encoding)
    """
if __name__ == '__main__':
    save_csv = encoding_csv()
    print("Complete")