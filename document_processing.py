import fitz
import cv2
import numpy
import time


class DocumentProcessing:
    def __init__(self, path: str) -> None:
        self.path = path
        self.location = None

    def convert2Img(self, location="./data/document.jpg"):
        self.location = location
        if self.path.endswith(".pdf"):
            mat = fitz.Matrix(2, 2)
            doc = fitz.open(self.path)
            image = doc[-1].get_pixmap(matrix=mat)
            image.save(location)
        else:
            img = cv2.imread(self.path)
            cv2.imwrite(location, img)

    def preprocessSignature(self, signaturePath: str):
        signature = cv2.imread(signaturePath)
        gray = cv2.cvtColor(signature, cv2.COLOR_BGR2GRAY)
        _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        th = cv2.bitwise_not(th)
        newSignature = numpy.zeros_like(signature)
        newSignature[:, :, 0] = th
        newSignature[:, :, 1] = th
        newSignature[:, :, 2] = th
        return newSignature

    def putSignature(self, signaturePath, x, y):
        try:
            st = time.time()
            signature = self.preprocessSignature(signaturePath)
            rawDocument = cv2.imread(self.location)
            r = rawDocument.copy()
            pointed = rawDocument.copy()
            cv2.circle(pointed, (x, y), 1, (0, 255, 0), 2)
            cv2.imwrite("./step/raw.jpg", rawDocument)
            cv2.imwrite("./step/pointed_raw.jpg", pointed)
            document = cv2.cvtColor(rawDocument, cv2.COLOR_BGR2GRAY)
            cv2.imwrite("./step/gray.jpg", document)
            _, binaryDoc = cv2.threshold(
                document, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            binaryDoc = cv2.bitwise_not(binaryDoc)
            cv2.imwrite("./step/bin.jpg", binaryDoc)
            template = binaryDoc.copy()
            line = numpy.full(
                (1, binaryDoc.shape[1] // 2), fill_value=255, dtype=numpy.uint8)
            template = template[binaryDoc.shape[0] //
                                2:, binaryDoc.shape[1] // 2:]
            cv2.imwrite("./step/part.jpg", template)
            for i in range(template.shape[0]):
                if numpy.sum(template[i]) > 0:
                    template[i] = line
            cv2.imwrite("./step/black.jpg", template)
            startPoint = 0
            newY = y - binaryDoc.shape[0] // 2
            newX = x - binaryDoc.shape[1] // 2
            while template[newY - startPoint][newX] == 0 and newY + startPoint < template.shape[0]:
                startPoint += 1
            if startPoint - 10 < signature.shape[0] // 2:
                newHeight = 2 * (startPoint - 10) + 1
                newWidth = int(
                    signature.shape[1] / signature.shape[0] * newHeight)
                if newWidth % 2 == 0:
                    newWidth += 1
                newSignature = cv2.resize(signature, (newWidth, newHeight))
                rawDocument[y - newHeight // 2: y + newHeight // 2 + 1,
                            x - newWidth // 2: x + newWidth // 2 + 1] = newSignature
                region = r.copy()
                cv2.rectangle(region, (x - newWidth // 2, y - newHeight // 2),
                              (x + newWidth // 2 + 1, y + newHeight // 2 + 1), (0, 255, 0), 2)
                cv2.imwrite("./step/region.jpg", region)
            else:
                rawDocument[y - signature.shape[0] // 2: y + signature.shape[0] // 2 + 1,
                            x - signature.shape[1] // 2: x + signature.shape[1] // 2 + 1] = signature
                newHeight = signature.shape[0]
                newWidth = signature.shape[1]
                region = r.copy()
                cv2.rectangle(region, (x - newWidth // 2, y - newHeight // 2),
                              (x + newWidth // 2 + 1, y + newHeight // 2 + 1), (0, 255, 0), 2)
                cv2.imwrite("./step/region.jpg", region)
            cv2.imwrite("./step/result.jpg", rawDocument)
            cv2.imshow("Result: ", rawDocument)
            en = time.time()
            with open("./runtime.txt", mode="a") as file:
                file.write(str(en - st) + "\n")
            cv2.waitKey(1000)
            return True, rawDocument
        except:
            return False, None
