import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
from core_engine.plate_detector import PlateDetector
os.environ['KMP_DUPLICATE_LIB_OK']='TRUE'


ModelPath = 'C:/Users/Win11/PycharmProjects/Plate/plate2/best.pt'
img_path = 'C:/Users/Win11/PycharmProjects/Plate/plate2/data/20.jpg'

img = cv2.imread(img_path)
img = cv2.resize(img, (640, 640))

detector = PlateDetector(ModelPath)
plate_coords=detector.detect(img)
x1, y1, x2, y2 = plate_coords[0]

plaka_img = img[y1:y2, x1:x2]
buyuk_plaka = cv2.resize(plaka_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)



buyuk_plaka = cv2.cvtColor(buyuk_plaka, cv2.COLOR_RGB2GRAY)

th_img = buyuk_plaka = cv2.adaptiveThreshold(buyuk_plaka , 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11,2)

kernel = np.ones((5,5),np.uint8)
th_img = cv2.morphologyEx(th_img,cv2.MORPH_OPEN,kernel ,iterations=1)


cnt = cv2.findContours(th_img ,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cnt = cnt[0]
cnt= sorted(cnt, key=cv2.contourArea, reverse=True)[:15]




plt.imshow(th_img, cmap='gray')
plt.show()

