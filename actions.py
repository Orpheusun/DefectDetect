from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import cv2
import numpy as np
from PyQt5 import QtWidgets

__author__ = "Atinderpal Singh"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "atinderpalap@gmail.com"

class ImageViewer:
    ''' Basic image viewer class to show an image with zoom and pan functionaities.
        Requirement: Qt's Qlabel widget name where the image will be drawn/displayed.
    '''
    def __init__(self, qlabel):
        self.qlabel_image = qlabel                            # widget/window name where image is displayed (I'm usiing qlabel)
        self.img = None
        self.qimage = None
        self.qimage_scaled = QImage()
        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.enableCut = False
        self.cutStartPoint = None
        self.cutEndPoint = None
        self.qlabel_image.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.__connectEvents()

    def __connectEvents(self):
        # Mouse events
        self.qlabel_image.resizeEvent = self.onResize
        self.qlabel_image.mousePressEvent = self.mousePressAction
        self.qlabel_image.mouseMoveEvent = self.mouseMoveAction
        self.qlabel_image.mouseReleaseEvent = self.mouseReleaseAction
        self.qlabel_image.paintEvent = self.paintEvent



    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        self.img = cv2.imdecode(np.fromfile(imagePath,dtype=np.uint8),0)
        # self.img = cv2.imread(imagePath,0)
        cv2.imshow('1',self.img)
        self.loadQImage()
        self.resizeLable()
        self.displayImage()

    def loadQImage(self):
        if self.img is not None:
            qformat = QImage.Format_Indexed8

            if len(self.img.shape) == 3:  # rows[0], cols[1], channels[2]
                if (self.imgimg.shape[2]) == 4:
                    qformat = QImage.Format_RGBA8888
                else:
                    qformat = QImage.Format_RGB888
            qimg = QImage(self.img, self.img.shape[1], self.img.shape[0],
                         self.img.strides[0], qformat)
            # BGR > RGB
            qimg = qimg.rgbSwapped()
            self.qimage = qimg
        else:
            pass

    #调整label高宽比适应图片高宽比
    def resizeLable(self):
        # Resize Qlabel
        imageX = self.qimage.size().width()
        imageY = self.qimage.size().height()
        imageRatio = imageX / imageY
        labelGeometry = self.qlabel_image.geometry()
        if imageX > labelGeometry.width():
            self.qlabel_image.parentWidget().setGeometry(labelGeometry.x(), labelGeometry.y(), labelGeometry.width() * self.zoomX, labelGeometry.width() * self.zoomX / imageRatio + 19)
        else:
            self.qlabel_image.parentWidget().setGeometry(labelGeometry.x(), labelGeometry.y(),
                                                         imageX,
                                                         imageY + 19)

    def displayImage(self):
        if not self.qimage.isNull():
            pixmap = QPixmap.fromImage(self.qimage)
            # 调整图片大小
            pixmap = pixmap.scaled(self.qlabel_image.width(),self.qlabel_image.height(),Qt.KeepAspectRatio)
            self.qlabel_image.setPixmap(pixmap)
        else:
            self.statusbar.showMessage('Cannot open this image! Try another one.', 5000)

    def onResize(self, QResizeEvent):
        if self.qimage is not None:
            pixmap = QPixmap.fromImage(self.qimage)
            pixmap = pixmap.scaled(self.qlabel_image.width(), self.qlabel_image.height(), Qt.KeepAspectRatio)
            self.qlabel_image.setPixmap(pixmap)

    def enlarge(self):
        self.zoomX = 1.5
        print(self.zoomX)
        self.resizeLable()

    def narrow(self):
        self.zoomX = 0.5
        print(self.zoomX)
        self.resizeLable()

    def reduction(self):
        self.zoomX = 1
        self.resizeLable()

    def cutImage(self):
        self.enableCut = True

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        print(self.qlabel_image.pixmap().rect())
        if self.enableCut:
            print("press")
            self.cutStartPoint = QMouseEvent.pos()

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        if self.enableCut:
            print("move")
            self.cutEndPoint = QMouseEvent.pos()
            self.qlabel_image.update()



    def mouseReleaseAction(self,QMouseEvent):
        if self.enableCut:
            print("release")
            self.cutEndPoint = QMouseEvent.pos()
            self.qlabel_image.update()
            self.enableCut = False
            self.showCutImage()

    def paintEvent(self, QPaintEvent):
        QtWidgets.QLabel.paintEvent(self.qlabel_image, QPaintEvent)  # 调用父类的painEvent方法
        print("painting")
        print(self.enableCut)
        if self.enableCut:
            print("cut")
            qp = QPainter()
            qp.begin(self.qlabel_image)
            qp.setPen(QPen(QtCore.Qt.red, 1, Qt.DotLine))
            qp.drawRect(self.cutStartPoint.x(), self.cutStartPoint.y(), self.cutEndPoint.x() - self.cutStartPoint.x(),
                        self.cutEndPoint.y() - self.cutStartPoint.y())


    def showCutImage(self):
        rect = QRect(self.cutStartPoint,self.cutEndPoint)
        self.qimage = self.qimage.copy(rect)
        self.cutStartPoint = None
        self.cutEndPoint = None
        self.resizeLable()
        self.displayImage()

