import cv2
import numpy as np
import json

# todo: 判斷找到的圓x、y與其他圓是否有偏差
    # note: 應該不能把特立獨行的y刪掉，不然如果每題都只有一個選項，每個圓的y都會是特立獨行的
        # 每題不會只有一個選項...，還是要刪掉特立獨行的y
    
# todo: 把判斷黑圓的方法修改成同一列最黑的
    # ok

# todo？: 把圓從內接正方形變成外接正方形
    # 原本就是外接

# tofix : 去噪(media blur) 參數
# tofix : adaptiveThreshold 參數
# tofix : HoughCircles 參數
# tofix : boundaries
# tofix : border
# tofix : 模糊把點拿掉
# tofix : x y deviation


# tofix : 
filename = './images/t8.jpg'
total_ques_num = 8
total_opt_num = 5


def recognize(p1,p2):
    ans_list = []
    img = cv2.imread(filename,0)

    # resize img
    try:
        height, width = img.shape[:2]
        aspect_ratio = height/width
        new_height = 3*297
        new_width = new_height/aspect_ratio
        size = (int(new_width), int(new_height))
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    except:
        # print('exit1')
        # exit()
        return ans_list



    # preprocess img
    ## remove shadow and strengthen black circle
    strengthen_img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv2.THRESH_BINARY,21,2)
    img = cv2.medianBlur(img,5)
    original_img = cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)

    # p1 = 60 , p2 = 30 
    # find circles in the sheet
    circles = cv2.HoughCircles(img,cv2.HOUGH_GRADIENT,1,20,param1=p1,param2=p2,minRadius=8,maxRadius=30)
    
    try:
        circles = np.uint16(np.ceil(circles))
    except:
        # print('exit2')
        return ans_list
    # store all circle's posX , posY and radius
    circle_info = []

    # # store all circle's posX、posY and its showup-count

    posY_counter = []
    posY_offset = 30 # posY's deviation

    # store circle info and collect possible options' x
    for item in circles[0,:]:
        x = item[0] # x pos
        y = item[1] # y pos
        r = item[2] # radius

        info = {'x' : x, 'y' : y, 'radius' : r ,\
             'ques' : 0 , 'option' : 0 , 'value' : 0}
        circle_info.append(info)

        # record possible circle's posY in the sheet
        pushed_y = 0 
        for pos_record in posY_counter:
            if (y <= pos_record['y'] + posY_offset and \
                y >= pos_record['y'] - posY_offset):
                pushed_y = 1
        if(not(pushed_y)):
            new_pos = {'y' : y , 'count' : 0}
            posY_counter.append(new_pos)

        # print(r)

    # collect possible y's showup-count
    for item in circle_info:
        for pos_record in posY_counter:
            if (item['y'] <= pos_record['y'] + posY_offset and \
                item['y'] >= pos_record['y'] - posY_offset):
                pos_record['count'] += 1

    # print(posY_counter)

    # pop out outstanding option
    for pos_record in posY_counter:
        if (pos_record['count'] == 1):
            for item in circle_info:
                if (item['y'] == pos_record['y']):
                    circle_info.remove(item)
            posY_counter.remove(pos_record)


    ## sort in the order of question
    circle_info.sort(key=lambda d:d['y'])

    posY_counter.sort(key=lambda d:d['y'])

    # categorize ques num
    for index,item in enumerate(circle_info):
        for y_index,y_item in enumerate(posY_counter):
            if(item["y"] <= y_item["y"] + posY_offset and \
                item["y"] >= y_item["y"] - posY_offset):
                item["ques"] = y_index+1
                break

    circle_info.sort(key=lambda d:d['ques'])
    ## sort in the order of option
    circle_info.sort(key=lambda d:d['x'])

    # categorize option num
    for ques in range(1,total_ques_num+1):
        opt = 1
        for index,item in enumerate(circle_info):
            if(item['ques'] == ques):
                item['option'] = opt
                opt += 1

    circle_info.sort(key=lambda d:d['ques'])
    circle_info.sort(key=lambda d:d['option'])
    

    # print(circle_info) # check if circle info is correct

    # start recognition
    # set boundaries of users' stroke-color
    boundaries = [([0], [50])]
    border = 8

    kernel = np.ones((3,3),np.uint8)

    for item in circle_info:
        x = item['x']
        y = item['y']
        r = item['radius']

        # cv2.circle(original_img,(x,y),r,(0,255,0),2) # check if circles are correct (removable)

        try:    
            # crop circle to external square
            rectX = (x - r)
            rectY = (y - r)

            crop_img = strengthen_img[rectY+border:(rectY+2*r)-border,\
                        rectX+border:(rectX+2*r)-border]    
            erosion = cv2.erode(crop_img,kernel,iterations = 1)    
        except:
            # print('exit3')
            # exit()
            return ans_list

        for (lower, upper) in boundaries:
            lower = np.array(lower, dtype = "uint8")
            upper = np.array(upper, dtype = "uint8")
            mask = cv2.inRange(erosion, lower, upper)
            # the more pixel , the more 255 value in mask(2-d array)

            for row in mask:
                for col in row:
                    if( col == 255):
                        item['value'] += 1

        # cv2.imshow   ('detected circles {},{}'.format(item['ques'],item['option']),erosion) # removable
 
    # judge answer
    for ques_index in range(1,total_ques_num+1):
        blackest = 0
        found = {} #
        for item in circle_info:
            if(item['ques'] == ques_index):
                # print(item['value'])
                if(item['value'] > blackest):
                    blackest = item['value']
                    found = item
        try:
            ans_list.append(found['option'])
            # print('- - - %d - - - %d - - - %d - - - %d - - -' % (found['x'],found['y'],found['ques'],found['option'])) #
            # cv2.circle(original_img,found['x'],found['y'],found['radius'],(0,0,255),2) # check if circles are correct (removable)
            # print("question",ques_index+1,":",ans)
        except:
            # print('exit4')
            ans_list = []
            return ans_list
        

    # print('----------------------------------------------------------------------')
    # for item in circle_info:
    #     print("%d %d %d %d" % (item['ques'], item['option'], item['x'], item['y']))

    # print(ans_list)

    # check question num and option num is correct
    fail = False
    if(len(ans_list) != total_ques_num):
        fail = True
    for ans in ans_list:
        if(ans < 1 or ans > total_opt_num):
            fail = True
    if(fail):
        ans_list = []

    # print(ans_list)


    # cv2.imshow('detected circles of {}-{}'.format(p1,p2),original_img)
    

    return ans_list


res = []
arr = [[0 for i in range(1)] for j in range(4)]
for p1 in range(40,80,10):
    # for p2 in range(25, 40, 5):
        p2 = 25
        curr_ans = recognize(p1,p2)
        res.append(curr_ans)
        if(curr_ans == [2,3,1,4,5,2,5,1]):
            # print('p1 = %d, p2 = %d' %(p1,p2))
            arr[ (p1//10) -4 ][ (p2//5) -5] = 1

# print(arr)

# cv2.waitKey(0)
# cv2.destroyAllWindows()
container = []
for index,elem in enumerate(res):
    collected = 0
    for index2,item in enumerate(container):
        if(elem == item['ans']):
            item['count'] += 1
            collected = 1
            break
    if(not collected):
        new_item = {'ans': elem,'count':1}
        container.append(new_item)

# print(res)

# print(container)
output = []
max_count = 0
for item in container:
    if(item['count'] > max_count):
        max_count = item['count']
        output = item['ans']

#返回众数
return output
