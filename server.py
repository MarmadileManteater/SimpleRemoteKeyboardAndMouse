
""" server entrypoint """

import platform
import logging
from os.path import exists
from os import remove
import socket
import sys
import pyautogui
from bottle import route, run, static_file, request, template
from simple_log_formatter import SimpleLogFormatter

# Disable the pyautogui failsafe to allow for moving the mouse to the
# corner of the screen
pyautogui.FAILSAFE = False
# Global state variable __is_dragging__ represents whether or not the mouse is
# currently dragging
__is_dragging__ = False
__logger__ = logging.getLogger('simple_remote_keyboard_and_mouse')


@route('/script.js')
def scripts():
    """ the script for the controls page """
    return static_file("script.js", root='./static/')


@route('/styles.css')
def styles():
    """ the styles for the controls page """
    return static_file("styles.css", root='./static/')


@route('/')
def index():
    """ tThe controls page """
    return template("controls", platform=platform.system())


@route('/typewrite')
def sendkeystroke():
    """ typewrites the given query from the client """
    pyautogui.typewrite(request.query.get("query"))


@route('/send/<key>')
def sendkey(key):
    """ receives keypresses from the client (also handles mouse clicks) """
    if key == 'leftclick':
        pyautogui.click()
    elif key == 'rightclick':
        pyautogui.rightClick()
    else:
        pyautogui.press(key)


@route('/send-hotkey/<keys>')
def send_hotkey(keys):
    """ receives hotkey combinations from the client """
    keys = keys.split(',')
    pyautogui.hotkey(*keys)


@route('/mousemove/<x_move>/<y_move>')
def mousemove(x_move, y_move):
    """ handles mouse move events sent from the client """
    current_x, current_y = pyautogui.position()
    pyautogui.moveTo(current_x + float(x_move), current_y + float(y_move))


@route('/mousescroll/<x_scroll>/<y_scroll>')
def mousescroll(x_scroll, y_scroll):
    """ handles mouse scroll events sent from the client """
    horizontal_scroll = int(float(x_scroll)) * 4
    vertical_scroll = int(float(y_scroll)) * 4
    pyautogui.hscroll(horizontal_scroll)
    pyautogui.vscroll(vertical_scroll)


@route('/disabledrag')
def disabledrag():
    """ disables drag (if currently dragging) """
    global __is_dragging__
    pyautogui.mouseUp()
    __is_dragging__ = False


@route('/mousedrag/<x>/<y>')
def mousedrag(x_drag, y_drag):
    """ handles drag events sent from the client """
    global __is_dragging__
    current_x, current_y = pyautogui.position()
    if __is_dragging__ is False:
        pyautogui.mouseDown(current_x + int(x_drag), current_y + int(y_drag))
        __is_dragging__ = True
    else:
        pyautogui.moveTo(current_x + int(x_drag), current_y + int(y_drag))


def main(check_argv=True):
    """ entrypoint """
    if exists('./last-used-host.txt'):
        with open('./last-used-host.txt', encoding='utf8') as last_used_host:
            ip_address = last_used_host.read()
    else:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
    # if there are two arguments, use the command line argument for the ip address
    # otherwise just use the given ip address above
    if check_argv and len(sys.argv) > 1:
        ip_address = sys.argv[1]
    try:
        with open('./last-used-host.txt', 'w', encoding='utf8') as about_to_use_host:
            about_to_use_host.write(ip_address)
        run(host=ip_address, port=8080)
    except socket.gaierror as error:
        __logger__.error(error)
        if exists('./last-used-host.txt'):
            __logger__.warning("Launching with given IP address failed")
            __logger__.warning("Trying an ip address given by the system ")
            remove('./last-used-host.txt')
            main(False)


if __name__ == '__main__':
    __logger__.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(SimpleLogFormatter())
    __logger__.addHandler(streamHandler)
    main()
