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
        self.qimage_scaled = QImage()                         # scaled image to fit to the size of qlabel_image
        self.qpixmap = QPixmap()                              # qpixmap to fill the qlabel_image
        self.qimage = None
        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = True        # to enable or disable pan
        self.pressed = None

        # 截图参数
        self.cutImgEnabled = False
        self.cutStartPoint = None
        self.cutEndPoint = None


        self.shape = 'point'
        self.penColor = Qt.black
        self.penWidth = 1
        self.pointArray = None
        self.point = None


        self.qlabel_image.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.__connectEvents()

    def __connectEvents(self):
        # Mouse events
        self.qlabel_image.mousePressEvent = self.mousePressAction
        self.qlabel_image.mouseMoveEvent = self.mouseMoveAction
        self.qlabel_image.mouseReleaseEvent = self.mouseReleaseAction
        self.qlabel_image.resizeEvent = self.onResize
        self.qlabel_image.paintEvent = self.paintEvent

    def onResize(self,QResizeEvent):
        if self.qimage is not None:
            ''' things to do when qlabel_image is resized '''
            self.qpixmap = QPixmap(self.qlabel_image.size())
            self.qpixmap.fill(QtCore.Qt.gray)
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def loadImage(self, imagePath):
        ''' To load and display new image.'''
        self.qimage = QImage(imagePath)
        self.adjustLabelSize()
        # print(self.qimage.size())
        self.qpixmap = QPixmap(self.qlabel_image.size())
        if not self.qimage.isNull():
            # reset Zoom factor and Pan position
            self.zoomX = 1
            self.position = [0, 0]
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width(), self.qlabel_image.height(), QtCore.Qt.KeepAspectRatio)
            self.update()
        else:
            self.statusbar.showMessage('Cannot open this image! Try another one.', 5000)

    #调整label高宽比为图片高宽比
    def adjustLabelSize(self):
        imageX = self.qimage.size().width()
        imageY = self.qimage.size().height()
        print(imageX,imageY)
        imageRatio = imageX / imageY

        labelGeometry = self.qlabel_image.geometry()
        self.qlabel_image.parentWidget().setGeometry(labelGeometry.x(),labelGeometry.y(),labelGeometry.width(),labelGeometry.width() / imageRatio+19)



    def update(self):
        ''' This function actually draws the scaled image to the qlabel_image.
            It will be repeatedly called when zooming or panning.
            So, I tried to include only the necessary operations required just for these tasks. 
        '''
        if not self.qimage_scaled.isNull():
            # check if position is within limits to prevent unbounded panning.
            px, py = self.position
            px = px if (px <= self.qimage_scaled.width() - self.qlabel_image.width()) else (self.qimage_scaled.width() - self.qlabel_image.width())
            py = py if (py <= self.qimage_scaled.height() - self.qlabel_image.height()) else (self.qimage_scaled.height() - self.qlabel_image.height())
            px = px if (px >= 0) else 0
            py = py if (py >= 0) else 0
            self.position = (px, py)

            if self.zoomX == 1:
                self.qpixmap.fill(QtCore.Qt.white)

            # the act of painting the qpixamp
            painter = QPainter()
            painter.begin(self.qpixmap)
            painter.drawImage(QtCore.QPoint(0, 0), self.qimage_scaled,
                    QtCore.QRect(self.position[0], self.position[1], self.qlabel_image.width(), self.qlabel_image.height()) )
            painter.end()

            self.qlabel_image.setPixmap(self.qpixmap)
        else:
            pass

    def mousePressAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        self.point = QMouseEvent.pos()
        self.pointArray = np.array([x,y])
        if self.cutImgEnabled:
            self.cutStartPoint = QMouseEvent.pos()
        if self.panFlag:
            self.pressed = QMouseEvent.pos()    # starting point of drag vector
            self.anchor = self.position         # save the pan position when panning starts

    def mouseMoveAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        self.point = QMouseEvent.pos()
        self.cutEndPoint = QMouseEvent.pos()
        self.pointArray = np.vstack((self.pointArray, [x,y]))
        if self.pressed:
            dx, dy = x - self.pressed.x(), y - self.pressed.y()         # calculate the drag vector
            self.position = self.anchor[0] - dx, self.anchor[1] - dy    # update pan position using drag vector
            self.update()                                               # show the image with udated pan position

    def mouseReleaseAction(self, QMouseEvent):
        x, y = QMouseEvent.pos().x(), QMouseEvent.pos().y()
        self.pointArray = np.vstack((self.pointArray, [x, y]))
        self.point = QMouseEvent.pos()
        if self.cutImgEnabled:
            self.cutEndPoint = QMouseEvent.pos()
            self.qimage = self.qimage_scaled.copy(self.cutStartPoint.x(), self.cutStartPoint.y(),self.cutEndPoint.x() - self.cutStartPoint.x(),self.cutEndPoint.y() - self.cutStartPoint.y())
            self.qimage_scaled = self.qimage_scaled.copy(self.cutStartPoint.x(), self.cutStartPoint.y(),self.cutEndPoint.x() - self.cutStartPoint.x(),self.cutEndPoint.y() - self.cutStartPoint.y())
            self.adjustLabelSize()
            self.update()
        self.pressed = None                                             # clear the starting point of drag vector

    def zoomPlus(self):
        self.zoomX += 1
        px, py = self.position
        px += self.qlabel_image.width()/2
        py += self.qlabel_image.height()/2
        self.position = (px, py)
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def zoomMinus(self):
        if self.zoomX > 1:
            self.zoomX -= 1
            px, py = self.position
            px -= self.qlabel_image.width()/2
            py -= self.qlabel_image.height()/2
            self.position = (px, py)
            self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
            self.update()

    def resetZoom(self):
        self.zoomX = 1
        self.position = [0, 0]
        self.qimage_scaled = self.qimage.scaled(self.qlabel_image.width() * self.zoomX, self.qlabel_image.height() * self.zoomX, QtCore.Qt.KeepAspectRatio)
        self.update()

    def enablePan(self, value):
        self.panFlag = value

    def setShape(self,shape):
        self.shape = shape

    def setPenColor(self,color):
        self.penColor = color

    def setPendWidth(self,width):
        self.penWidth = width


    def paintEvent(self, e):
        QtWidgets.QLabel.paintEvent(self.qlabel_image, e)  # 调用父类的painEvent方法
        # qp = QPainter()
        # qp.begin(self.qimage_scaled)
        # if self.point is not None:
        #     qp.setPen(QPen(QtCore.Qt.white, 5))  # 里面的5是你画的点大小，可以自己设置
        #     qp.drawPoint(self.point)
        #     qp.end()
        if self.cutImgEnabled:
            print("cut")
            qp = QPainter()
            qp.begin(self.qlabel_image)
            qp.setPen(QPen(QtCore.Qt.red, 1,Qt.DotLine))
            qp.drawRect(self.cutStartPoint.x(),self.cutStartPoint.y(),self.cutEndPoint.x()-self.cutStartPoint.x(),self.cutEndPoint.y()-self.cutStartPoint.y())

    def cutImage(self):
        self.cutImgEnabled = True