from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsScene, QMessageBox
from PyQt5.QtGui import QPixmap
from document_processing import DocumentProcessing
from signature_extractor import SignatureExtractor
import cv2
import os
import time


class App(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.extractor = None
        self.processor = None
        self.uploadedDocument = False
        self.uploadedSignature = False
        self.chosenLocation = False
        self.documentSize = (636, 900)
        self.signatureSize = (270, 180)
        self.buttonSize = (150, 40)

        self.setWindowTitle("Signature Extractor Program")
        windowWidth = self.documentSize[0] + self.signatureSize[0] + 30
        windowHeight = max(
            self.documentSize[1] + self.buttonSize[1], self.signatureSize[1] + self.buttonSize[1]) + 30
        self.resize(windowWidth, windowHeight)
        self.setGeometry(0, 0, windowWidth, windowHeight)
        self.setObjectName("Main")
        self.uploadDocButton = QtWidgets.QPushButton(self)
        self.uploadDocButton.setGeometry(
            0, 0, self.buttonSize[0], self.buttonSize[1])
        self.uploadDocButton.setText("Upload document")
        self.uploadSignButton = QtWidgets.QPushButton(self)
        self.uploadSignButton.setGeometry(
            self.documentSize[0] + 10, 0, self.buttonSize[0], self.buttonSize[1])
        self.uploadSignButton.setText("Upload signature")
        self.documentView = QtWidgets.QGraphicsView(self)
        self.documentView.setGeometry(
            0, self.buttonSize[1] + 1, self.documentSize[0], self.documentSize[1])
        self.signatureView = QtWidgets.QGraphicsView(self)
        self.signatureView.setGeometry(
            self.documentSize[0] + 10, self.buttonSize[1] + 1, self.signatureSize[0], self.signatureSize[1])
        self.runButton = QtWidgets.QPushButton(self)
        self.runButton.setGeometry(
            windowWidth - self.buttonSize[0] - 30, windowHeight - 3 * self.buttonSize[1] - 120, self.buttonSize[0], self.buttonSize[1] + 30)
        self.mergeButton = QtWidgets.QPushButton(self)
        self.mergeButton.setGeometry(
            windowWidth - self.buttonSize[0] - 30, windowHeight - 2 * self.buttonSize[1] - 90, self.buttonSize[0], self.buttonSize[1] + 30)
        self.quitButton = QtWidgets.QPushButton(self)
        self.quitButton.setStyleSheet('background-color: red')
        self.quitButton.setGeometry(
            windowWidth - self.buttonSize[0] - 30, windowHeight - self.buttonSize[1] - 60, self.buttonSize[0], self.buttonSize[1] + 30)
        self.quitButton.setText("Quit")
        self.runButton.setText("Extract")
        self.mergeButton.setText("Merge")
        self.mergeButton.setEnabled(False)
        self.locationX = -1
        self.locationY = -1
        self.elapsedTime = 0.0
        self.setupUploadAction()
        self.show()
        print("Time: ", self.elapsedTime)

    def setupUploadAction(self):
        self.quitButton.clicked.connect(self.close)
        self.uploadDocButton.clicked.connect(self.uploadDocument)
        self.uploadSignButton.clicked.connect(self.uploadSignature)
        self.runButton.clicked.connect(self.run)
        self.mergeButton.clicked.connect(self.merge)

    def merge(self):
        if self.chosenLocation:
            result, image = self.processor.putSignature(
                "./data/sign.jpg", self.locationX, self.locationY)
            if result:
                dialog = QMessageBox(self)
                dialog.setWindowTitle("MESSAGE")
                dialog.setText("Save result ?")
                button = dialog.exec()
                if button == QMessageBox.Ok:
                    cv2.imwrite("./data/result.jpg", image)
                    self.close()

    def run(self):
        if self.uploadedSignature and self.uploadedDocument:
            self.extractor = SignatureExtractor(path="./data/signature.jpg")
            self.extractor.run()
            self.showMessage(
                "MESSAGE", "Signature has been extracted sucessfully!\nClick a point on document view where you want to put signature in")
            self.documentView.mousePressEvent = self.getPos
            self.mergeButton.setEnabled(True)
        else:
            self.showMessage(
                "ERROR", "Signature and document must be uploaded!")

    def showMessage(self, title: str, content: str):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(content)
        dialog.exec()

    def uploadDocument(self):
        fileName = QFileDialog.getOpenFileName(
            self, caption="Open a file", directory="", filter="All Files (*.*)")
        documentPath = fileName[0]
        self.processor = DocumentProcessing(path=str(documentPath))
        self.processor.convert2Img()
        self.displayDocument()

    def uploadSignature(self):
        fileName = QFileDialog.getOpenFileName(
            self, caption="Open a file", directory="", filter="All Files (*.*)")
        signaturePath = fileName[0]
        image = cv2.imread(str(signaturePath))
        cv2.imwrite("./data/signature.jpg", image)
        self.displaySignature()

    def displayDocument(self):
        assert "document.jpg" in os.listdir("./data"), "Document not found!"
        path = "./data/document.jpg"
        image = cv2.imread(path)
        image = cv2.resize(image, (self.documentSize[0], self.documentSize[1]))
        cv2.imwrite(path, image)
        document = QPixmap(path)
        item = QGraphicsPixmapItem(document)
        scene = QGraphicsScene(self)
        scene.addItem(item)
        self.documentView.setScene(scene)
        self.uploadedDocument = True

    def displaySignature(self):
        assert "signature.jpg" in os.listdir("./data"), "Signature not found!"
        path = "./data/signature.jpg"
        save_path = "./data/view_signature.jpg"
        image = cv2.imread(path)
        image = cv2.resize(
            image, (self.signatureSize[0], self.signatureSize[1]))
        cv2.imwrite(save_path, image)
        document = QPixmap(save_path)
        item = QGraphicsPixmapItem(document)
        scene = QGraphicsScene(self)
        scene.addItem(item)
        self.signatureView.setScene(scene)
        self.uploadedSignature = True

    def getPos(self, event):
        while self.chosenLocation == False:
            self.locationX = event.pos().x()
            self.locationY = event.pos().y()
            self.chosenLocation = True


if __name__ == "__main__":
    import math
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    app.exec_()
