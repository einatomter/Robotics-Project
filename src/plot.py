from telloFunctions import *
import cv2
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QWidget, QSlider, QFrame, QLabel, QStyleFactory
from pyqtgraph.Qt import QtCore, QtGui
from random import randint


def update_plot_data():

    global cycle
    global plotInfo
    global plotKalman

    global line1
    global line2
    global line3

    global line1K
    global line2K
    global line3K

    global X
    global P
    global Q
    global R
    global XInit

    global whichMethod

    print(f'Q values: {Q[0][0]} , {Q[1][1]} , {Q[2][2]}')

    ret, frame = cap.read()
    if whichMethod == 0:
        outputs = progYOLO(frame, net, whT)
        info = findObjectYOLO(outputs, frame, classNames, 0) # YOLO
    elif whichMethod == 1:
        info = findObjectHSV(frame, minHSV=(21,113,129), maxHSV=(81,206,255)) # HSV
    else:
        info = findObjectHaar(frame)


    X, P = kalman(info, X, P, Q, R)



    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
    
    pix = QtGui.QPixmap.fromImage(img)
    camFrame.setPixmap(pix)

    for i in range(3):
        plotInfo[i].append(info[i])
        plotKalman[i].append(X[i])

    cycle.append(cycle[-1] + 1)  # Add a new value 1 higher than the last.

    if len(cycle) >= 100:
        line1.getViewBox().enableAutoRange(axis='y', enable=True)
        line2.getViewBox().enableAutoRange(axis='x', enable=True)
        line3.getViewBox().enableAutoRange(axis='x', enable=True)

    if len(cycle) > 100:
        for i in range(3):
            plotInfo[i].pop(0) 
            plotKalman[i].pop(0)

        cycle.pop(0)

    line1.setData(plotInfo[0], cycle)  # Update the data
    line2.setData(cycle, plotInfo[1])
    line3.setData(cycle, plotInfo[2])

    line1K.setData(plotKalman[0], cycle)
    line2K.setData(cycle, plotKalman[1])
    line3K.setData(cycle, plotKalman[2])



def readQVal(value):
    global Q
    global boolQ
    if boolQ:
        newQ = value/100
        Q = [[newQ, 0, 0],[0, newQ, 0],[0, 0, newQ]]
    boolQ = True


def changeMethod(button):
    global whichMethod
    if button.text() == 'YOLO':
        whichMethod = 0
    elif button.text() == 'HSV':
        whichMethod = 1
    else:
        whichMethod = 2


boolQ = False
whichMethod = 0

classNames, net, whT = initYOLO()
cap = cv2.VideoCapture(0)

app = QApplication([])
win = QMainWindow()

Q = np.array([[5, 0, 0], [0, 2.5, 0], [0, 0, 1.4]]) # Process noise
R = np.array([[20, 0, 0], [0, 25, 0],[0, 0, 30]]) # Measurement noise
X = np.array([320, 240, 200])
XInit = np.array([320, 240, 200])
P = np.array([[10, 0, 0],[0, 20, 0], [0, 0, 10]])

# Data

cycle = [0]

plotInfo = [[],[],[]] # [x,y,h,loopCount] Do not change value
plotKalman = [[],[],[]] # Do not change value

plotInfo[0].append(320)
plotInfo[1].append(240)
plotInfo[2].append(200)

plotKalman[0].append(320)
plotKalman[1].append(240)
plotKalman[2].append(200)


# Creating Plot

penInfo = pg.mkPen(color=(255, 0, 0), style=QtCore.Qt.DashLine)
penKalman = pg.mkPen(color=(0, 0, 255))


# Left/Right
plot1Widget = pg.PlotWidget()
plot1Widget.setTitle("Left - Right", color=(0,0,0), size='20pt')
plot1Widget.setLabel('left', "<span style=\"color:black;font-size:14px\">Pixels</span>")
plot1Widget.setLabel('bottom', "<span style=\"color:black;font-size:14px\">Cycle</span>")
plot1Widget.addLegend()
plot1Widget.setXRange(0, 640)
plot1Widget.setYRange(max(0, cycle[0]-100), (cycle[0]+100))
plot1Widget.setLimits(xMin=0, xMax=640, minXRange=0, maxXRange=640) # Limit zoom and pan
plot1Widget.setFixedHeight(480)
plot1Widget.setFixedWidth(640)

line1 = plot1Widget.plot(cycle, plotInfo[0], name='measured', pen=penInfo)
line1K = plot1Widget.plot(cycle, plotKalman[0], name='kalman', pen=penKalman)



# Up/Down
plot2Widget = pg.PlotWidget()
plot2Widget.setTitle("Up - Down", color=(0,0,0), size='20pt')
plot2Widget.setLabel('left', "<span style=\"color:black;font-size:14px\">Pixels</span>")
plot2Widget.setLabel('bottom', "<span style=\"color:black;font-size:14px\">Cycle</span>")
plot2Widget.addLegend()
plot2Widget.setXRange(max(0, cycle[0]-100), (cycle[0]+100))
plot2Widget.setYRange(0, 480)
plot2Widget.setLimits(yMin=0, yMax=480, minYRange=0, maxYRange=480)
plot2Widget.setFixedHeight(480)
plot2Widget.setFixedWidth(640)

line2 = plot2Widget.plot(plotInfo[1], cycle, name='measured', pen=penInfo)
line2K = plot2Widget.plot(plotKalman[1], cycle, name='kalman', pen=penKalman)
line2.getViewBox().invertY(True)
line2K.getViewBox().invertY(True)


# Forward/Back
plot3Widget = pg.PlotWidget()
plot3Widget.setTitle("Forward - Backward", color=(0,0,0), size='20pt')
plot3Widget.setLabel('left', "<span style=\"color:black;font-size:14px\">Pixels</span>")
plot3Widget.setLabel('bottom', "<span style=\"color:black;font-size:14px\">Cycle</span>")
plot3Widget.addLegend()
plot3Widget.setXRange(max(0, cycle[0]-100), (cycle[0]+100))
plot3Widget.setYRange(0, 400)
plot3Widget.setLimits(yMin=0, yMax=400, minYRange=0, maxYRange=400)
plot3Widget.setFixedHeight(480)
plot3Widget.setFixedWidth(640)

line3 = plot3Widget.plot(cycle, plotInfo[2], name='measured', pen=penInfo)
line3K = plot3Widget.plot(cycle, plotKalman[2], name='kalman', pen=penKalman)

plot1Widget.setBackground('w')
plot2Widget.setBackground('w')
plot3Widget.setBackground('w')

# webcam

camFrame = QtGui.QLabel()

# update 

# graphs
timer = QtCore.QTimer()
timer.setInterval(50)
timer.timeout.connect(update_plot_data)
timer.start()







# Creating window layout
central_widget = QWidget()

layout = QVBoxLayout(central_widget)






hBoxButtons = QHBoxLayout()
buttonHAAR = QPushButton('HAAR')
buttonYOLO = QPushButton('YOLO')
buttonHSV = QPushButton('HSV')
buttonHAAR.clicked.connect(lambda: changeMethod(buttonHAAR))
buttonYOLO.clicked.connect(lambda: changeMethod(buttonYOLO))
buttonHSV.clicked.connect(lambda: changeMethod(buttonHSV))
hBoxButtons.addWidget(buttonHAAR)
hBoxButtons.addWidget(buttonYOLO)
hBoxButtons.addWidget(buttonHSV)


groupBox1 = QGroupBox()
hBoxTop = QHBoxLayout()
hBoxTop.addWidget(camFrame)
hBoxTop.addWidget(plot1Widget)
groupBox1.setLayout(hBoxTop)



groupBox2 = QGroupBox()
hBoxBot = QHBoxLayout()
hBoxBot.addWidget(plot2Widget)
hBoxBot.addWidget(plot3Widget)
groupBox2.setLayout(hBoxBot)



qtext = QLabel()
qtext.setText("Q - variance slider")
qSlider = QSlider(QtCore.Qt.Horizontal)
qSlider.valueChanged[int].connect(readQVal)
qSlider.setMaximum(200)
qSlider.setSliderPosition(100)

sliderBox = QHBoxLayout()
sliderBox.addWidget(qtext)
sliderBox.addWidget(qSlider)


layout.addLayout(sliderBox)
layout.addLayout(hBoxButtons)
layout.addWidget(groupBox1)
layout.addWidget(groupBox2)



# Run program


# print(QStyleFactory.keys())
# app.setStyle('windowsvista')
win.setWindowTitle('Kalman vs Measure - (Frame width: 640, height: 480)')
win.setCentralWidget(central_widget)
#win.move(2400,50)
win.setFixedSize(1324, 1080)

win.show()
print(win.size())


app.exit(app.exec_())
cap.release()