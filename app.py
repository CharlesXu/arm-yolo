import os
import cv2                                       
import numpy as np                               
from flask import Flask, render_template, request
                                            
app = Flask(__name__)                       
                                            
INPUT_MODEL_WEIGHTS = "/conf/yolov3.weights"
INPUT_MODEL_CONFIG = "/conf/yolov3.cfg" 
INPUT_MODEL_CLASSES = "/conf/yolov3.txt"      
                                                                
scale = 0.00392
classes = None 
ROOT_DIR = os.path.abspath("/")                                 
MODEL_WEIGHTS_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_WEIGHTS)
MODEL_CONFIG_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_CONFIG)  
MODEL_CLASSES_PATH = os.path.join(ROOT_DIR, INPUT_MODEL_CLASSES)
                                                                
with open(MODEL_CLASSES_PATH, 'r') as f:                  
	classes = [line.strip() for line in f.readlines()]    
                                                          
COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet(MODEL_WEIGHTS_PATH, MODEL_CONFIG_PATH)

def get_output_layers(net):                                                       
	layer_names = net.getLayerNames()                                             
	output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
	return output_layers                      
                                        
@app.route('/process', methods=['POST','PUT'])      
def upload_file():                            
	file = request.files['image_file']             

	image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
	Width = image.shape[1]
	Height = image.shape[0]  

	blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
	net.setInput(blob)
	outs = net.forward(get_output_layers(net))

	class_ids = []
	confidences = []
	boxes = []
	conf_threshold = 0.5
	nms_threshold = 0.4                

	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > 0.5:
				center_x = int(detection[0] * Width)
				center_y = int(detection[1] * Height)
				w = int(detection[2] * Width)
				h = int(detection[3] * Height)
				x = center_x - w / 2
				y = center_y - h / 2
				class_ids.append(class_id)
				confidences.append(float(confidence))
				boxes.append([x, y, w, h])

	output = ""
	for i in range(0,len(class_ids)):
		output = output + "Class: " + classes[class_ids[i]] + " with confidence: " + str(confidences[i]) + "\n"

	return output
                          
if __name__ == '__main__':
	app.run()

