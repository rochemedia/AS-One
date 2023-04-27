import cv2
import numpy as np
import os
from .utils import draw_kpts, plot_skeleton_kpts
import cv2
import time

from asone.pose_estimators.yolov7_pose import Yolov7PoseEstimator
from asone.pose_estimators.yolov8_pose import Yolov8PoseEstimator
from asone.utils import get_weight_path, download_weights

class PoseEstimator:
    def __init__(self, estimator_flag, weights: str=None, use_cuda=True):
        self.model_flag = 'yolov8'
        
        if weights:
            weights = weights
        else:
            weights = get_weight_path(estimator_flag)
            if not os.path.exists(weights):
                download_weights(weights)
        self.estimator = self.get_estimator(estimator_flag, weights, use_cuda)

    def get_estimator(self, estimator_flag: int, weights: str, use_cuda: bool):
        
        if estimator_flag in range(149, 155):
            estimator = Yolov7PoseEstimator(weights=weights)
            self.model_flag = 'yolov7'
        elif estimator_flag in range(144, 149):
            estimator = Yolov8PoseEstimator(weights=weights,
                                       use_cuda=use_cuda)
            self.model_flag = 'yolov8'
        return estimator
    
    def estimate_image(self, frame, conf_thresh):
        keypoints = self.estimator.estimate(frame)
        return keypoints
    
    def estimate_video(self, video_path, save=True, conf_thresh=0.5, display=True):
       
        if video_path == 0:
            cap = cv2.VideoCapture(0)
            video_path = 'webcam.mp4'
        else:
            cap = cv2.VideoCapture(video_path)
        
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        FPS = cap.get(cv2.CAP_PROP_FPS)

        if save:
            video_writer = cv2.VideoWriter(
                os.path.basename(video_path),
                cv2.VideoWriter_fourcc(*"mp4v"),
                FPS,
                (int(width), int(height)),
            )
        
        frame_no = 1
        tic = time.time()

        prevTime = 0
        fframe_num = 0
        while True:
            start_time = time.time()

            ret, img = cap.read()
            if not ret:
                break
            frame = img.copy()
            kpts = self.estimator.estimate(img)
            currTime = time.time()
            fps = 1 / (currTime - prevTime)
            prevTime = currTime

            if kpts is not None:
                img = draw_kpts(img, kpts) 
                # for i in kpts:
                #     img = plot_skeleton_kpts(im=img, kpts=i, steps=1)
            cv2.line(img, (20, 25), (127, 25), [85, 45, 255], 30)
            cv2.putText(img, f'FPS: {int(fps)}', (11, 35), 0, 1, [
                        225, 255, 255], thickness=2, lineType=cv2.LINE_AA)

            frame_no+=1
            if display:
                cv2.imshow('Window', img)

            if save:
                video_writer.write(img)
    
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
