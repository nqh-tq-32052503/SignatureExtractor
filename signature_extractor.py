import cv2
import numpy
import time


class SignatureExtractor:
    def __init__(self, path: str) -> None:
        self.path = path
        self.image = cv2.imread(self.path)
        self.signature = None
        self.signaturePath = "./data/sign.jpg"

    def run(self):
        st = time.time()
        thresholdImage = self.threshold()
        self.filter(thresholdImage)
        cv2.imwrite(self.signaturePath, self.signature)
        en = time.time()
        with open("./runtime.txt", mode="a") as file:
            file.write(str(en - st) + "\n")

    def threshold(self):
        grayImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(
            grayImage, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        thresh0 = cv2.bitwise_not(thresh)
        return thresh0

    def filter(self, threshold):
        num, labels, stat, centroids = cv2.connectedComponentsWithStats(
            threshold, connectivity=8, ltype=cv2.CV_32S)
        lower_threshold_value = int(
            threshold.shape[0] * threshold.shape[1] / 1000)
        upper_threshold_value = threshold.shape[0] * threshold.shape[1]
        # stat = [x for x in stat if x[4] >=
        #         lower_threshold_value and x[2] * x[3] < upper_threshold_value]
        stat = [x for x in stat if (x[4] >= lower_threshold_value and x[2] * x[3] < upper_threshold_value) and (x[0] + x[2] >= threshold.shape[1] //
                                                                                                                2 or x[1] + x[3] >= threshold.shape[0] // 2) and (x[0] <= threshold.shape[1] // 2 and x[1] <= threshold.shape[0] // 2)]
        plate = self.image.copy()
        for s in stat:
            cv2.rectangle(plate, (s[0], s[1]), (s[0] + s[2],
                          s[1] + s[3]), color=(36, 255, 12), thickness=2)
        cv2.imwrite("./step/drawn_signature.jpg", plate)
        if len(stat) > 1:
            new_x, new_y, new_w, new_h = self.unionRect(stat)
        else:
            new_x = stat[0][0]
            new_y = stat[0][1]
            new_w = stat[0][2]
            new_h = stat[0][3]
        template = numpy.zeros_like(self.image)
        template[:, :, 0] = threshold
        template[:, :, 1] = threshold
        template[:, :, 2] = threshold
        self.signature = template[new_y: new_y + new_h, new_x: new_x + new_w]

    def unionRect(self, rect_coordinates):
        vertical_list = []
        horizontal_list = []
        for coordinates in rect_coordinates:
            x, y, w, h, _ = coordinates
            vertical_list.append(y)
            vertical_list.append(y + h)
            horizontal_list.append(x)
            horizontal_list.append(x + w)
        new_y = min(vertical_list)
        new_x = min(horizontal_list)
        new_h = max(vertical_list) - new_y
        new_w = max(horizontal_list) - new_x
        return new_x, new_y, new_w, new_h
