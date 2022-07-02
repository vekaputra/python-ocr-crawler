from pynput import keyboard
import pyautogui as pg
import time

stop = False

def saveGoodRBPValue(userId): # Red Blue Purple
    img = pg.screenshot()

    # 723 140 945 425
    # 1652 140 1875 425
    # 723 680 945 965
    # 1652 680 1875 965

    cropImgs = [
        img.crop((723, 140, 945, 425)),
        img.crop((1652, 140, 1875, 425)),
        img.crop((723, 680, 945, 965)),
        img.crop((1652, 680, 1875, 965)),
    ]

    i = 0
    for cropImg in cropImgs:
        pixels = list(cropImg.getdata())

        red = 0
        blue = 0
        purple = 0

        for pixel in pixels:
            if pixel[2] > 192 and pixel[0] < 64 and pixel[1] < 64:
                blue = blue + 1
            if pixel[0] > 192 and pixel[1] < 64 and pixel[2] < 64:
                red = red + 1
            if pixel[0] > 192 and pixel[2] > 192 and pixel[1] < 64:
                purple = purple + 1
        
        if blue > 0 and red < blue / 5:
            id = str(userId+i).zfill(6)
            cropImg.save("port-return/"+id+".jpg")
        
        i += 1

def loadReturn(userId, pin):
    coord = [
        [[145, 40], [1070, 40], [145, 580], [1070, 580]],
        [[320, 40], [1240, 40], [320, 580], [1240, 580]],
        [[370, 100], [1300, 100], [370, 640], [1300, 640]],
        [[525, 100], [1450, 100], [525, 640], [1450, 640]],
        [[920, 40], [1860, 40], [920, 580], [1860, 580]],
    ]
    for i in range(0, 4):
        pg.click(coord[0][i][0], coord[0][i][1]) # (145 40) (1070 40) (145 580) (1070 580)
        pg.typewrite(str(userId+i).zfill(6))
        time.sleep(0.05)
    
    for i in range(0, 4):
        pg.click(coord[1][i][0], coord[1][i][1]) # (320 40) (1240 40) (320 580) (1240 580)
        pg.typewrite(pin)
        time.sleep(0.05)
        pg.click(coord[2][i][0], coord[2][i][1]) # (370 100) (1300 100) (370 640) (1300 640)
        pg.typewrite("202104")
        time.sleep(0.05)
        pg.click(coord[3][i][0], coord[3][i][1]) # (920 40) (1860 40) (920 580) (1860 580)
        pg.typewrite("202202")
    
    time.sleep(0.5)
    return userId+4

def onPress(key):
    if key == keyboard.Key.esc:
        global stop
        stop = True

listener = keyboard.Listener(on_press = onPress)
listener.start()

next = 256242
while next < 264610 and stop == False:
    next = loadReturn(next, "0401")
    results = saveGoodRBPValue(next-4)
