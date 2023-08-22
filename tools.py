import cv2

from repo.uptechStar.module.camra import Camera
from repo.uptechStar.module.tagdetector import TagDetector

c = Camera()
c.set_cam_resolution(resolution_multiplier=0.4)
width = c._camera.get(cv2.CAP_PROP_FRAME_WIDTH)
height = c._camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width)
print(height)
a = TagDetector(c, 'blue')

a.tag_monitor_switch = True
c.update_frame()
cv2.imwrite('test.jpg', c.latest_frame)
c.update_frame()
color = cv2.cvtColor(c.latest_frame, cv2.COLOR_BGR2GRAY)
cv2.imwrite('test1.jpg', color)

# from apriltag import Detector, DetectorOptions
#
# a = DetectorOptions()
# d = Detector()
# print(d.detect(color))
# print('saved')
while True:
    print(a.tag_id)

# cap = cv2.VideoCapture(0)
# _, img = cap.read()
# cv2.imwrite('test.jpg', img)
