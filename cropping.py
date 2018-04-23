import cv2

class cropperObj():
    def __init__(self, filename):
        self.filename = filename

    def cropImageBorders(self):
        # read  image
        img = cv2.imread(self.filename)

        # threshold image
        ret, threshed_img = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),15, 255, cv2.THRESH_BINARY)
        # find contours and get the external one
        image, contours, hier = cv2.findContours(threshed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # with each contour, draw boundingRect in green a minAreaRect in red and a minEnclosingCircle in blue
        aux_area = 0
        for c in contours:
            # get the bounding rect
            contour_area = cv2.contourArea(c)
            if contour_area > aux_area:
                aux_area = contour_area
                x, y, w, h = cv2.boundingRect(c)

        # draw a green rectangle to visualize the bounding rect
        crop = img[y:y + h, x:x + w]
        cv2.imwrite(self.filename, crop)
