# -*- coding: utf-8 -*-

"""
This is a simple script that only takes care of taking a picture
"""

def takeASnap():
        import cv2 

        camera_port = 0 
        ramp_frames = 30 

        try:
            camera = cv2.VideoCapture(camera_port)
        except Exception:
            print("Camera error")

        def get_image():
            retval, im = camera.read()
            return im 
        for i in range(ramp_frames):
            camera.read()

        camera_capture = get_image()
        filename = "newSnap.jpg"
        cv2.imwrite(filename,camera_capture)


        camera.release()
        cv2.destroyAllWindows()
        return 1
 
if __name__ == '__main__':
     
     takeASnap()
