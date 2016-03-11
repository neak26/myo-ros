#!/usr/bin/env python

'''Simple Myo ROS Node to Train Gestures

This script uses the emg data from Myo to train Gestures. Maximum 10 Gestures can be 
learned. These Gestures are saved each in its own file. The files then are used from
the classify_myo_ros.py script.
To train Gestures, start the script, make the Gesture which should be trained and
then press a number from 0-9, which then is the lable for this Gesture. 
This script is based on the myo-raw project - especially on the classify_myo.py 
and the myo.py files. (see https://github.com/dzhu/myo-raw/ which is available under 
the MIT LICENSE)

Following changes where made:
  - ros code added
  - split up classifying and gesture learning

usage: python train_myo.py (but myo_ros.py must be running) 

provides:
  - generates files vals0.dat - vals9.dat which are used from classify_myo_ros.py
  - subscribes to: /myo/data/emg
'''

from __future__ import print_function

# import used collections
from collections import Counter, deque

# import pygame
try:
    import pygame
    from pygame.locals import *
    HAVE_PYGAME = True
except ImportError:
    HAVE_PYGAME = False

# Ros libraries
import roslib
import rospy

# emg, gesture
from std_msgs.msg import Int32, Int32MultiArray

# import nn_classifier class
import nn_classifier

# define class to train myo
class TrainMyoROS:
    HIST_LEN = 25
    
    def __init__(self):
        self.nnclassifier = nn_classifier.NNClassifier()
        self.recording = -1
        self.emg = (0,) * 8
        self.gesture = None
        self.history = deque([0] * TrainMyoROS.HIST_LEN, TrainMyoROS.HIST_LEN)
        self.history_cnt = Counter(self.history)
        
        '''Initialize ros publisher, ros subscriber'''
        rospy.init_node('myo_train', anonymous=True)
#         self.pub_gesture = rospy.Publisher("/myo/classifier/gesture", Int32)
        self.sub_emg = rospy.Subscriber("/myo/data/emg", Int32MultiArray, self.callback_emg, queue_size=1)
#         self.sub_gesture = rospy.Subscriber("/myo/classifier/gesture", Int32, self.callback_gesture, queue_size=1)

        self.nnclassifier.read_data()
        
    def callback_emg(self, ros_data):
        self.emg = ros_data.data
        if self.recording >= 0:
            self.nnclassifier.store_data(self.recording, self.emg)
        
        self.gesture = self.nnclassifier.classify(self.emg)
        self.history_cnt[self.history[0]] -= 1
        self.history_cnt[self.gesture] += 1
        self.history.append(self.gesture)

if __name__ == '__main__':
    
    ros_node = TrainMyoROS()
    
    if HAVE_PYGAME:
        pygame.init()
        w, h = 800, 320
        scr = pygame.display.set_mode((w, h))
        font = pygame.font.Font(None, 30)
    
    try:
        while not rospy.is_shutdown():
            
            r = ros_node.history_cnt.most_common(1)[0][0]
            
            if HAVE_PYGAME:
                for ev in pygame.event.get():
                    if ev.type == QUIT or (ev.type == KEYDOWN and ev.unicode == 'q'):
                        raise KeyboardInterrupt()
                    elif ev.type == KEYDOWN:
                        if K_0 <= ev.key <= K_9:
                            ros_node.recording = ev.key - K_0
                        elif K_KP0 <= ev.key <= K_KP9:
                            ros_node.recording = ev.key - K_Kp0
                        elif ev.unicode == 'r':
                            ros_node.nnclassifier.read_data()
                        elif ev.unicode == 'd':
                            ros_node.nnclassifier.clearGestureFiles()
                    elif ev.type == KEYUP:
                        if K_0 <= ev.key <= K_9 or K_KP0 <= ev.key <= K_KP9:
                            ros_node.recording = -1

                scr.fill((0, 0, 0), (0, 0, w, h))

                for i in range(10):
                    x = 0
                    y = 0 + 30 * i

                    clr = (0,200,0) if i == r else (255,255,255)

                    txt = font.render('%5d' % (ros_node.nnclassifier.Y == i).sum(), True, (255,255,255))
                    scr.blit(txt, (x + 20, y))

                    txt = font.render('%d' % i, True, clr)
                    scr.blit(txt, (x + 110, y))


                    scr.fill((0,0,0), (x+130, y + txt.get_height() / 2 - 10, len(ros_node.history) * 20, 20))
                    scr.fill(clr, (x+130, y + txt.get_height() / 2 - 10, ros_node.history_cnt[i] * 20, 20))

                pygame.display.flip()
            else:
                for i in range(10):
                    if i == r: sys.stdout.write('\x1b[32m')
                    print(i, '-' * ros_node.history_cnt[i], '\x1b[K')
                    if i == r: sys.stdout.write('\x1b[m')
                sys.stdout.write('\x1b[11A')
                print()

    except KeyboardInterrupt:
        pass
    finally:
        print()

    if HAVE_PYGAME:
        pygame.quit()
