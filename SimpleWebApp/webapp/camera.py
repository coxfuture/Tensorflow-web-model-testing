import datetime
import os
import cv2
import numpy as np
import tensorflow as tf
import sys
from operator import itemgetter
from webapp import db

sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

class VideoCamera(object):
    def __init__(self,camarg):
    
        self.rtsplink = camarg
        #for debugging, make a note of the rtsp link seen here        
        print('starting video on',camarg)        
        self.video = cv2.VideoCapture(camarg)
        MODEL_NAME = 'inference_graph'
        CWD_PATH = os.getcwd()
        PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')
        PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')
        ##
        ## CHANGEME if using different trained model from default RCNN inception v2
        ##
        NUM_CLASSES = 90
        ##
        ##
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)
        

        # This is so deprecated it's not even funny. 
        # These 8 lines throw about 6 full pages of deprecation warnings.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)

        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')
        
            
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        
        ret, frame = self.video.read()
        #This is mega lazy error handling. If the camera link isn't stable enough,
        #the app will crash. Seems more common on CPU than GPU
        #This will at least tell you what camera caused the crash
        if ret == False:
            print('error: dropped frame on:',self.rtsplink) 
        frame_expanded = np.expand_dims(frame, axis=0)
        
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: frame_expanded})

        listb = boxes.tolist()[0]
        object_count = int(round(np.count_nonzero(listb) / 4))

        objlist = []
        for i in range(object_count):
            newobj = classes.tolist()[0][i]
            objlist.append(newobj)        
        
        detected = []
        for i in objlist:
            iden = self.category_index.get(int(round(i)))
            detected.append(iden.get('name'))
        
        #these generate lists of what's detected, it's not fully implemented because
        #generating alerts with them is going to be a lot of work, and for some reason 
        #the detected objects list defaults to an ndarray filled with 1s, so detecting 
        #whatever object is "1" is gonna require some thought
        #print(detected)
        #print(object_count,'objects')
        #print(num)
        #print(objlist)

        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=3,
            min_score_thresh=0.60)

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
