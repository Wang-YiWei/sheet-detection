import cv2
import numpy as np
import json

img = cv2.imread('./images/demo.jpg',0)

# resize img
height, width = img.shape[:2]
aspect_ratio = height/width
new_height = 800
new_width = new_height/aspect_ratio
size = (int(new_width), int(new_height))
img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

# preprocess img
img = cv2.medianBlur(img,5)
original_img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

# find circles in the sheet
circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=60,param2=30,minRadius=8,maxRadius=30)
circles = np.uint16(np.around(circles))

# set boundaries of users' stroke-color
boundaries = [([0, 0, 0], [70, 70, 70])]

# store selected circle position 
found = []

# store possible circle's pos_x in the sheet
circle_pos_x = []

# set a threshold of center rect's pixel value
base_pixel = 200

for item in circles[0,:]:
    # draw the outer circle
    x = item[0] # x pos
    y = item[1] # y pos
    r = item[2] # radius
    # cv2.circle(original_img,(x,y),r,(0,255,0),2) # check if circles are correct (removable)
    
    # record possible circle's pos_x in the sheet
    pushed = 0    
    for j in range(len(circle_pos_x)):
        if (x <= circle_pos_x[j] + 30 and x >= circle_pos_x[j] - 30):
            pushed = 1
    if(not(pushed)):
        circle_pos_x.append(x)

    # crop circle
    rectX = (x - r)
    rectY = (y - r)
    crop_img = original_img[rectY:(rectY+2*r), rectX:(rectX+2*r)]

    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        mask = cv2.inRange(crop_img, lower, upper)

        # check if the center rect of the circle is filled
        center_rect = mask[int(0.5*r):int(1.5*r), int(0.5*r):int(1.5*r)]
        if(np.average(center_rect) >= base_pixel):
            pos = {"x" : x, "y" : y, "ques" : 0, "option" : 0}
            found.append(dict(pos))

# sort in the order of question
found.sort(key=lambda d:d["y"])

# sort in the order of option
circle_pos_x.sort()

for index,item in enumerate(found):
    item["ques"] = index + 1
    cv2.circle(original_img,(item["x"],item["y"]),r,(0,0,255),2) # check if circles are correct (removable)
    for index2,value in enumerate(circle_pos_x):
        if(item["x"] <= value + 30 and item["x"] >= value - 30):
            item["option"] = index2+1
# print(found)

# print(circle_pos_x)
for item in found:
    print("question",item["ques"],":",item["option"])

# cv2.imwrite('demo.png',original_img)
cv2.imshow('detected circles',original_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
