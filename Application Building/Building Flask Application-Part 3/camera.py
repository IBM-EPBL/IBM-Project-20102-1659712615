import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from os import getcwd

model=load_model('trained_model.h5')
cap=cv2.VideoCapture(0)
index=['A','B','C','D','E','F','G','H','I']
dir = getcwd()

def get_frames():
	while 1:
		ret, frame=cap.read()
		cv2.imwrite(dir + '\image.jpg',frame)
		img=image.load_img('image.jpg',target_size=(64,64))
		x=image.img_to_array(img)
		x=np.expand_dims(x,axis=0)
		prediction=np.argmax(model.predict(x),axis=1)
		y=prediction[0]
		copy = frame.copy()
		cv2.rectangle(copy, (320, 100), (620,400), (255,0,0), 5)
		cv2.putText(frame,'Prediction : '+str(index[y]),(100,100),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),4)
		cv2.imshow("Home", frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break
		

cap.release()
cv2.destroyAllWindows() 
