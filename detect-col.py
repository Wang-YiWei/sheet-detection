import cv2
import numpy as np

img = cv2.imread('./images/demo2.png',0)

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

all_circles_x = []
for item in circles[0,:]:
    x = item[0] # x pos
    all_circles_x.append(x)

# get the mode of pos_x
value_count = np.bincount(np.array(all_circles_x))
most_frequent_x = np.argmax(value_count)

# filter the question circle
ques_and_opt_circle_dist = 10
ques_circle_y = []
for item in circles[0,:]:
    x = item[0] # x pos
    y = item[1] # y pos    
    if(abs(x - most_frequent_x) > ques_and_opt_circle_dist):
        ques_circle_y.append(y)

# categorize circles among questions
ques_circle_y.sort()
all_circle_info = []
for item in circles[0,:]:
    x = item[0] # x pos
    y = item[1] # y pos
    r = item[2] # radius    
    for index,ques_y in enumerate(ques_circle_y):
        if(y > ques_y):
            if(index != (len(ques_circle_y)-1) ):
                continue
            else:
                info = {'x' : x , 'y' : y , 'r' : r, 'ques' : index+1, 'option' : 0}            
                all_circle_info.append(info)
        elif(y not in ques_circle_y):
            info = {'x' : x , 'y' : y , 'r' : r, 'ques' : index, 'option' : 0}            
            all_circle_info.append(info)
            break

# categorize option in each question
all_circle_info.sort(key=lambda d:d['y'])
total_ques_num = all_circle_info[-1]['ques']
for current_ques in range(total_ques_num):
    count = 1
    for item in all_circle_info:
        if(item['ques'] == current_ques+1):
            item['option'] = count
            count += 1

# set boundaries of users' stroke-color
boundaries = [([0, 0, 0], [70, 70, 70])]

# set a threshold of center rect's pixel value
base_pixel = 200 

# store selected circle 
found = []
for item in all_circle_info:
    x = item['x'] # x pos
    y = item['y'] # y pos
    r = item['r'] # radius

    # draw the outer circle
    # cv2.circle(original_img,(x,y),r,(0,255,0),2) # check if circles are correct (removable)

    # crop circle
    rectX = (x - r)
    rectY = (y - r)
    crop_img = original_img[rectY:(rectY+2*r), rectX:(rectX+2*r)]

    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        mask = cv2.inRange(crop_img, lower, upper)

        # check if the center rect of the circle is filled using mask
        center_rect = mask[int(0.5*r):int(1.5*r), int(0.5*r):int(1.5*r)]
        if(np.average(center_rect) >= base_pixel):
            found.append(item)

# sort in the order of question
found.sort(key=lambda d:d['y'])
# print(found)

for item in found:
    cv2.circle(original_img,(item['x'],item['y']),r,(0,0,255),2) # check if circles are correct (removable)
    print("question",item['ques'],":",item['option'])
    
# show img
cv2.imshow('detected circles',original_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
