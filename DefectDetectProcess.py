import sys,os

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5 import QtCore
from qtmodern.styles import dark
from actions import ImageViewer
from qtmodern.windows import ModernWindow
import cv2

# 主窗口
class DefectDetect(QMainWindow):
    def __init__(self):
        super(DefectDetect,self).__init__()
        loadUi("mainWindow.ui",self)
        self.image = None
        #图片显示区域为ImageViewer
        self.image_viewer = ImageViewer(self.imageLabel)
        #打开图片按钮绑定事件
        self.openButton.clicked.connect(self.loadClicked)

        #实现图片显示区域label可拉伸大小
        layout = self.verticalLayout_3
        sizegrip = QSizeGrip(self.imageLabel)
        layout.addWidget(sizegrip, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        layout.setStretchFactor(self.imageLabel, 40)
        layout.setStretchFactor(sizegrip, 0.5)
        self.frame_4.setLayout(layout)
        self.frame_4.setWindowFlag(QtCore.Qt.SubWindow)
        self.frame_4.show()

        self.penColorFrame = QFrame()
        self.intInfoFrame(self.toolFrame)

        #截图
        self.cutImgButtom.clicked.connect(self.cutImgClicked)
        #放大
        self.enlargeBtn.clicked.connect(self.enlarge)
        #缩小
        self.narrowBtn.clicked.connect(self.narrow)
        #还原大小
        self.reductionBtn.clicked.connect(self.reduction)

    #打开图片
    @pyqtSlot()
    def loadClicked(self):
        fname, fliter = QFileDialog.getOpenFileName(self,'Open File','C:\\',"Image Files (*.*)")
        if fname:
            self.image = fname
            self.image_viewer.loadImage(fname)
        else:
            print('Invalid Image')

    def intInfoFrame(self,frame):
        labelShape = QLabel("形状:")
        labelPenW = QLabel("画笔宽度:")
        labelPenColor = QLabel("画笔颜色:")

        shapeComboBox = QComboBox()
        shapeComboBox.addItem('点','Point')
        shapeComboBox.addItem('线','Line')
        shapeComboBox.addItem('矩形','Rectangle')
        shapeComboBox.addItem('圆','Rounded Rectangle')

        widthSpinBox = QSpinBox()
        widthSpinBox.setRange(0, 20)


        self.penColorFrame.setAutoFillBackground(True)
        self.penColorFrame.setPalette(QPalette(Qt.blue))
        penColorPushButton = QPushButton("更改")

        layout = QGridLayout(self.tab_2)
        layout.addWidget(labelShape,1,0)
        layout.addWidget(shapeComboBox,2,0)
        layout.addWidget(labelPenW,3,0)
        layout.addWidget(widthSpinBox, 4, 0)
        layout.addWidget(labelPenColor,5,0)
        layout.addWidget(self.penColorFrame, 6, 0)
        layout.addWidget(penColorPushButton, 6, 1)
        self.tab_2.setLayout(layout)

        shapeComboBox.activated.connect(self.slotShape)
        widthSpinBox.valueChanged.connect(self.slotPenWidth)
        penColorPushButton.clicked.connect(self.slotPenColor)

    def slotShape(self, value):
        self.image_viewer.setShape(value)
        print(value)

    def slotPenWidth(self, value):
        self.image_viewer.setPendWidth(value)
        print(value)

    def slotPenColor(self):
        color = QColorDialog.getColor(Qt.black)
        self.penColorFrame.setPalette(QPalette(color))
        self.image_viewer.setPenColor(color)
        print(color)

    def cutImgClicked(self):
        self.image_viewer.cutImage()


    def enlarge(self):
         self.image_viewer.enlarge()

    def narrow(self):
        self.image_viewer.narrow()

    def reduction(self):
        self.image_viewer.reduction()

app=QApplication(sys.argv)
dark(app)
window = DefectDetect()
window.setWindowTitle("缺陷检测")
window.show()
sys.exit(app.exec_())