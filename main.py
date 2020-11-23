import sensor, image, time, math
from pyb import UART
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()
#阈值
#THRESHOLD = (54, 100, 30, 127, -128, 127)
THRESHOLD  = (0, 100, 15, 127, -128, 127)
#数据传输
uart = UART(3,115200)
uart1 = UART(1,115200)
xDistence = 0
zDistence = 0
rotate = 0
lineRotate = 0
XCenter = 0
blobPixel = 0

#任务标志
taskStatus = 1
targetGet = 0

#tag参数
f_x = (2.8 / 3.984) * 160 # 默认值
f_y = (2.8 / 2.952) * 120 # 默认值
c_x = 160 * 0.5 # 默认值(image.w * 0.5)
c_y = 120 * 0.5 # 默认值(image.h * 0.5)


def receiveData():
    global taskStatus,lineRotate
    received = uart1.readchar()
    lineRotate = received


def degrees(radians):
    return (180 * radians) / math.pi


def aprilTagCheck():
    img = sensor.snapshot()
    global xDistence, rotate, targetGet, zDistence
    aprilTags = img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y)
    for aprilTag in aprilTags:
        targetGet = 1
        img.draw_rectangle(aprilTag.rect())
#        print(aprilTag.family())
#        print(aprilTag.z_translation())
#        print(degrees(aprilTag.y_rotation()), aprilTag.x_rotation(), aprilTag.z_rotation())
        rotate = degrees(aprilTag.y_rotation())
        xDistence = aprilTag.x_translation()
        zDistence = aprilTag.z_translation()
#        print(rotate,xDistence)
        if rotate < 180 :
            rotate += 180
        else:
            rotate -= 180
        xDistence = abs(xDistence * 10)
        xDistence += 40
        zDistence = abs(zDistence * 10)
#        for rect in aprilTag.corners():
#            img.draw_cross(rect)

def findOrigin():
    global blobPixel, XCenter, targetGet
    img = sensor.snapshot()
    blobs = img.find_blobs([THRESHOLD],merge = True, x_stride = 50)
    maxPixel = 0
    for blob in blobs:
        img.draw_rectangle(blob.rect())
        maxPixel = max(blob.pixels(),maxPixel)
        XCenter = blob.cx() + 60
        targetGet = 1
    blobPixel = maxPixel/30


def work(taskStatus):
    if taskStatus  == 1:
        findOrigin()

def sendData():
    global targetGet, blobPixel
    pack_data = bytearray( [0xaa, 0xaf, 0x00,0x00,0x00,0x00])
    if taskStatus == 1:
        pack_data = bytearray( [0xaa, 0xaf, XCenter, int(blobPixel), targetGet])
        print(XCenter,blobPixel,targetGet)
        targetGet = 0
    uart.write(pack_data)

while(True):
    clock.tick()
#    receiveData()
    work(taskStatus)
    sendData()
#    print(clock.fps())
