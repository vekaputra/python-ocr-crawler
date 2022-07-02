import pytesseract
import time
from pynput import keyboard
import pyautogui as pg
import telebot
import tkinter as tk
from tkinter import ttk

TESSERACT_CONFIG = '--psm 6 -l eng -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:'
BOT_TOKEN = ''
CHAT_ID = ''

stop = False
ignoreOrder = False
accounts = []
labels = {}
accountCaches = {}
bot = telebot.TeleBot(BOT_TOKEN)

def loadOrderList(userIds):
    coord = [
        [[145, 40], [1070, 40], [145, 580], [1070, 580]],
        [[920, 40], [1860, 40], [920, 580], [1860, 580]],
    ]

    for i, userId in enumerate(userIds):
        pg.click(coord[0][i][0], coord[0][i][1]) # (145 40) (1070 40) (145 580) (1070 580)
        pg.typewrite(userId)
        pg.click(coord[1][i][0], coord[1][i][1]) # (320 40) (1240 40) (320 580) (1240 580)
    
    time.sleep(0.8)
    return

def parseOCR(result):
    rows = result.split('\n')
    parsedResult = []
    for row in rows:
        if row == '\x0c':
            continue
        cols = row.upper().replace('DAY', '.').split(' ')

        if len(cols) != 7:
            continue

        parsedResult.append([
            cols[0], # time
            cols[1].replace('1', 'I'), # code
            cols[2], # order type
            cols[3], # order price
            cols[4], # order qty
            cols[5], # order done price
            cols[6] # order done qty
        ])
    
    return parsedResult

def broadcastNewOrder(userId, rows):
    global accountCaches

    i = 0
    j = 0
    newOrder = f'{labels[userId]}\n'
    for row in rows:
        if i >= 5:
            break
        i += 1
        if row[0] in accountCaches[userId]:
            continue
        else:
            j += 1
            row[3] = row[3].replace('O', '0')
            row[4] = row[4].replace('O', '0')
            row[5] = row[5].replace('O', '0')
            row[6] = row[6].replace('O', '0')
            signal = '🟢' # BUY
            if 'SELL' in row[2]:
                signal = '🔴' # SELL
            newOrder += f'\n{signal} {row[1]} {row[4]} @ {row[3]}; DONE {row[6]} @ {row[5]}'
            accountCaches[userId][row[0]] = 1
    
    if ignoreOrder:
        return
    if j != 0:
        bot.send_message(CHAT_ID, newOrder)

def getOCRValue(userIds):
    img = pg.screenshot()

    cropImgs = [
        img.crop((70, 150, 950, 465)).convert('RGB'),
        img.crop((1000, 150, 1880, 465)).convert('RGB'),
        img.crop((70, 690, 950, 1005)).convert('RGB'),
        img.crop((1000, 690, 1880, 1005)).convert('RGB'),
    ]

    for i, userId in enumerate(userIds):
        ocr = pytesseract.image_to_string(cropImgs[i], config=TESSERACT_CONFIG)
        result = parseOCR(ocr)
        broadcastNewOrder(userId, result)
    
    return

def runBot():
    global ignoreOrder
    global stop

    stop = False
    next = 0
    accLen = len(accounts)
        
    while stop == False:
        userIds = accounts[next:min(next+4, accLen)]
        loadOrderList(userIds)
        getOCRValue(userIds)

        next += 4
        if next > accLen:
            ignoreOrder = False
            next = 0

def runSecondSession():
    global ignoreOrder
    ignoreOrder = True
    runBot()

# Key Listener

def onPress(key):
    if key == keyboard.Key.esc:
        global stop
        stop = True

listener = keyboard.Listener(on_press = onPress)
listener.start()

# Init

#with open('account.conf') as f:
with open('research.conf') as f:
    lines = f.readlines()
    for line in lines:
        if '#' in line:
            continue
        rows = line.replace('\n','').split(':')
        accounts.append(rows[0])
        labels[rows[0]] = f'{rows[0]} - {rows[1]}'

for acc in accounts:
    accountCaches[acc] = {}

# GUI

options = {'padx': 5, 'pady':5}

root = tk.Tk()
root.title('Bot')
root.geometry('190x50')
root.resizable(False, False)

frame = ttk.Frame(root)

btnFirstSession = ttk.Button(frame, text='Sesi 1')
btnFirstSession.grid(column=0, row=0, **options)
btnFirstSession.configure(command=runBot)

btnSecondSession = ttk.Button(frame, text='Sesi 2')
btnSecondSession.grid(column=1, row=0, **options)
btnSecondSession.configure(command=runSecondSession)

frame.grid(padx=10, pady=10)

root.mainloop()