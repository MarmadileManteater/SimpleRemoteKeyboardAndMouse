
import logging
import pyautogui
import socket
import sys
from os.path import exists
from os import remove
from bottle import route, run, template, static_file, request
from SimpleLogFormatter import SimpleLogFormatter


logger = logging.getLogger('simple_remote_keyboard_and_mouse')
# Disable the pyautogui failsafe to allow for moving the mouse to the corner of the screen
pyautogui.FAILSAFE = False
# Global state variable isDragging represents whether or not the mouse is currently dragging
isDragging = False

@route('/script.js')
def styles():
    return static_file("script.js", root='./')

@route('/styles.css')
def styles():
    return static_file("styles.css", root='./')

# at the route, serve up the controls page
@route('/')
def index():
    return static_file("controls.html", root='./')

@route('/fonts/Rubik-VariableFont_wght.ttf')
def foundationFont():
    return static_file("fonts/Rubik-VariableFont_wght.ttf", root="./", mimetype="application/x-font-ttf")

# type whatever is sent through the pyautogui typewrite method
@route('/typewrite')
def sendkeystroke():
    pyautogui.typewrite(request.query.get("query"))

@route('/send/<key>')
def sendkey(key):
    if key == 'leftclick':
        pyautogui.click()
    elif key == 'rightclick':
        pyautogui.rightClick()
    else:
        pyautogui.press(key)

@route('/send-hotkey/<keys>')
def sendHotkey(keys):
    keys = keys.split(',')
    pyautogui.hotkey(*keys)

@route('/mousemove/<x>/<y>')
def mousemove(x, y):
    currentX, currentY = pyautogui.position()
    pyautogui.moveTo(currentX + float(x), currentY + float(y))

@route('/mousescroll/<x>/<y>')
def mousescroll(x, y):
    h = int(float(x)) * 4
    v = int(float(y)) * 4
    pyautogui.hscroll(h)
    pyautogui.vscroll(v)

@route('/disabledrag')
def disabledrag():
    global isDragging
    pyautogui.mouseUp()
    isDragging = False

@route('/mousedrag/<x>/<y>')
def mousedrag(x, y):
    global isDragging
    currentX, currentY = pyautogui.position()
    if isDragging is False:
        pyautogui.mouseDown(currentX + int(x), currentY + int(y))
        isDragging = True
    else:
        pyautogui.moveTo(currentX + int(x), currentY + int(y))

def main(checkArgv = True):
    global logger
    if exists('./last-used-host.txt'):
        with open('./last-used-host.txt') as lastUsedHost:
            IP_addres = lastUsedHost.read()
    else:
        hostname = socket.gethostname()
        IP_addres = socket.gethostbyname(hostname)
    # if there are two arguments, use the command line argument for the ip address
    # otherwise just use the given ip address above
    if checkArgv and len(sys.argv) > 1:
        IP_addres = sys.argv[1]
    try:
        with open('./last-used-host.txt', 'w') as aboutToUseHost:
            aboutToUseHost.write(IP_addres)
        run(host=IP_addres, port=8080)
    except Exception as e:
        logger.error(e)
        if exists('./last-used-host.txt'):
            logger.warning('Launching with given IP address failed\nTrying an ip address given by the system . . . ')
            remove('./last-used-host.txt')
            main(False)

if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(SimpleLogFormatter())
    logger.addHandler(streamHandler)
    main()
