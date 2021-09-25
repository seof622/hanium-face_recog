import face_recognition
import numpy as np
import os

class encoding_csv():
    def crop_face(image_path):
        from PIL import Image
        import face_recognition

        # Load the jpg file into a numpy array
        image = face_recognition.load_image_file(image_path)

        # Find all the faces in the image using the default HOG-based model.
        # This method is fairly accurate, but not as accurate as the CNN model and not GPU accelerated.
        # See also: find_faces_in_picture_cnn.py
        face_locations = face_recognition.face_locations(image)

        print("I found {} face(s) in this photograph.".format(len(face_locations)))

        for face_location in face_locations:
            # Print the location of each face in this image
            top, right, bottom, left = face_location
            print(
                "A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
                                                                                                      right))

            # You can access the actual face itself like this:
            face_image = image[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            pil_image.save(image_path, 'jpeg')

    face_names = []
    face_encodings = []
    face_locations = []
    print("sub : initialize")
    Image_dir = "./encoding_image"
    encoding_dir = "/home/pi/project_han/encoding_list/"
    files = os.listdir(Image_dir)
    csv_files = os.listdir(encoding_dir)
    print("sub : load path")
    for filename in files:
        name, ext = os.path.splitext(filename)
        csv_file = encoding_dir + name + ".csv"
        print("sub : cal " + name)
        if os.path.isfile(csv_file):
            print("sub : Exist " + csv_file)
        else:
            full_name = os.path.join(Image_dir, filename)
            crop_face(full_name)
            face_encoding_img = face_recognition.load_image_file(full_name)
            print("sub : load " + name )
            face_encoding = face_recognition.face_encodings(face_encoding_img,model= 'small')
            encoding_np = face_encoding
            np.savetxt("./encoding_list/" + name + ".csv",encoding_np,delimiter=',')
    """
    ###인코딩 값 csv에서 추출하기
    face_encoding = np.loadtxt("./set_danger/encoding/test.csv",delimiter = ",")
    print(face_encoding)
    """




if __name__ == '__main__':
    save_csv = encoding_csv()
    print("encoding Complete")
