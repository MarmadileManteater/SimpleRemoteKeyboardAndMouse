
""" server entrypoint """

import platform
import logging
from os.path import exists
from os import remove
import subprocess
import socket
import sys
import pyautogui
import re
from bottle import route, default_app, static_file, request, template, response, TEMPLATE_PATH
from paste import httpserver
from .simple_log_formatter import SimpleLogFormatter
from .helpers.javascripthon import compileJsthon

VOLUME_BUMP_AMOUNT = 10# volume only changes by 10% intervals

# Disable the pyautogui failsafe to allow for moving the mouse to the
# corner of the screen
pyautogui.FAILSAFE = False
# Global state variable __is_dragging__ represents whether or not the mouse is
# currently dragging
__is_dragging__ = False
__logger__ = logging.getLogger('simple_remote_keyboard_and_mouse')
__client_side_script__ = None

TEMPLATE_PATH.insert(0, './backend/views')

def get_audio_system_linux():
    """ 
        determines if `pactl` or `amixer` are available in linux
        returns the name of whichever it finds first or None 
    """
    if platform.system().lower() == 'linux':
        if "/pactl" in subprocess.run(("type pactl"), capture_output=True, shell=True).stdout.decode():
            return 'pactl'
        if "/amixer" in subprocess.run(("type amixer"), capture_output=True, shell=True).stdout.decode():
            return 'amixer'
    return None


def is_volume_control_possible():
    """ determines if volume control is currently possible / implemented for the current platform """
    # if this is windows, this will always be possible
    if platform.system().lower() == 'windows':
        return True
    # check to see if there is an audio system we can interface with in linux
    if get_audio_system_linux() != None:
        return True
    return False


def volume_control(control):
    """ takes in a windows volume control key input and handles it in linux as well """
    if platform.system().lower() == 'linux':
        # need to handle this with some cli tool
        audio_controls_system = get_audio_system_linux()
        if audio_controls_system == 'pactl':
            # obtain default sink name from `pactl info`
            default_sink_name = subprocess.run(("pactl info | grep 'Default Sink'"), capture_output=True, shell=True).stdout.decode().replace("Default Sink: ", "").replace("\n", "")
            # perform the operation on the sink
            set_value = None
            if control == "volumeup":
                set_value = "+%i" % VOLUME_BUMP_AMOUNT
            elif control == "volumedown":
                set_value = "-%i" % VOLUME_BUMP_AMOUNT
            elif control == "volumemute":
                set_value = 0
            if set_value != None:
                subprocess.run(("pactl", "set-sink-volume", "{sink_name}".format(sink_name=default_sink_name), "{set_value}%".format(set_value=set_value)))
            else:
                print("Command \"%\" not supported" % control)
        elif audio_controls_system == 'amixer':
            # amixer doesn't support relative volume inputs, so we have to check what the volume is first
            volume_info = subprocess.run(("amixer sget 'Master'"), capture_output=True, shell=True).stdout.decode().replace("\n", "")
            re_volume_level = re.compile(r"\[([0-9]*?)%\]")
            volume_level = int(re_volume_level.search(volume_info).group(1))
            set_value = None
            if control == "volumeup":
                set_value = "%i" % (volume_level + VOLUME_BUMP_AMOUNT)
            elif control == "volumedown":
                set_value = "%i" % (volume_level - VOLUME_BUMP_AMOUNT)
            elif control == "volumemute":
                set_value = "0"
            if set_value != None:
                subprocess.run(("amixer", "sset", "'Master'", "{set_value}%".format(set_value=set_value)))
            else:
                print("Command \"%\" not supported" % control)
    elif platform.system().lower() == 'windows':
        pyautogui.press(control)

@route('/<script_name>.js')
def dynamic_python_script_loader(script_name):
    """ loads a javascripthon script from the `client` folder """
    py_script_name = f"./frontend/{script_name}.py"
    if exists(py_script_name):
        jsthon = compileJsthon(py_script_name)
        response.content_type = 'application/javascript; charset=utf-8'
        response.status = 200
        
        return jsthon['js']
    else:
        response.status = 404
        response.content_type = 'application/javascript; charset=utf-8'
        return 'console.log("404 - Not found.")'

#@route('/<script_name>.js.map')
def dynamic_python_source_map_loader(script_name):
    py_script_name = f"./frontend/{script_name}.py"
    if exists(py_script_name):
        jsthon = compileJsthon(py_script_name)
        response.content_type = 'application/json; encoding=utf-8'
        response.status = 200
        return jsthon['map']
    else:
        response.status = 404
        response.content_type = 'application/json; encoding=utf-8'
        return '{ "status": 404, "content": "Not found" }'


@route('/styles.css')
def styles():
    """ the styles for the controls page """
    return static_file("styles.css", root='./backend/static/')

@route('/')
def index():
    """ The controls page """
    return template("controls", volume_controls=is_volume_control_possible())


@route('/typewrite')
def sendkeystroke():
    """ typewrites the given query from the client """
    pyautogui.typewrite(request.query.get("query"))


@route('/send/<key>')
def sendkey(key):
    """ receives keypresses from the client (also handles mouse clicks) """
    try:
        if key == 'leftclick':
            pyautogui.click()
        elif key == 'rightclick':
            pyautogui.rightClick()
        elif key == 'volumeup':
            volume_control(key)
        elif key == 'volumedown':
            volume_control(key)
        elif key == 'volumemute':
            volume_control(key)
        else:
            pyautogui.press(key)
        response.content_type = 'application/json; encoding=utf-8'
        response.status = 200
        return '{ \"type\": \"success\" }'
    except Exception as e:
        response.content_type = 'application/json; encoding=utf-8'
        response.status = 500
        return f'{{ \"type\": \"error\", "message": "{e}" }}'


@route('/send-hotkey/<keys>')
def send_hotkey(keys):
    """ receives hotkey combinations from the client """
    keys = keys.split(',')
    pyautogui.hotkey(*keys)
    response.content_type = 'application/json'
    return f"{{ \"type\": \"success\", \"message\": \"hotkey {'+'.join(keys)} was pressed\"}}"

@route('/mouse<movement_type>/<x_move>/<y_move>')
def mouse(x_move, y_move, movement_type):
    """ handles mouse move events sent from the client """
    global __is_dragging__
    is_scrolling = movement_type == 'scroll'
    is_dragging = movement_type == 'drag'
    is_moving = movement_type == 'move'
    try:
        current_x, current_y = pyautogui.position()
        if is_scrolling:
            horizontal_scroll = int(float(x_move)) * 4
            vertical_scroll = int(float(y_move)) * 4
            pyautogui.hscroll(horizontal_scroll)
            pyautogui.vscroll(vertical_scroll)
        elif is_dragging:
            if __is_dragging__ is False:
                pyautogui.mouseDown(current_x + int(x_move), current_y + int(y_move))
                __is_dragging__ = True
            else:
                pyautogui.moveTo(current_x + float(x_move), current_y + float(y_move))
        elif is_moving:
            pyautogui.moveTo(current_x + float(x_move), current_y + float(y_move))
        else:
            response.content_type = 'application/json'
            response.status = 406
            return f"{{ \"type\": \"error\", \"message\": \"'{movement_type}' is not an acceptable movement type\", \"options\": [ \"move\", \"scroll\", \"drag\"] }}"
        response.content_type = 'application/json'
        response.status = 200
        return '{ \"type\": \"success\" }'
    except Exception as e:
        response.content_type = 'application/json'
        response.status = 500
        return f'{{ "type": "error", "message": "{e}" }}'

@route('/disabledrag')
def disabledrag():
    """ disables drag (if currently dragging) """
    global __is_dragging__
    pyautogui.mouseUp()
    was_dragging = __is_dragging__
    __is_dragging__ = False
    response.content_type = 'application/json'
    response.status = 200
    if was_dragging:
      return '{ "type": "success", "message": "Disabled existing drag" }'
    else:
      return '{ "type": "info", "message": "Nothing to do" }'


def main(check_argv=True):
    """ entrypoint """
    __logger__.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(SimpleLogFormatter())
    __logger__.addHandler(streamHandler)
    
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
        app = default_app()
        httpserver.serve(app, host=ip_address.rstrip(), port=8080)
    except socket.gaierror as error:
        __logger__.error(error)
        if exists('./last-used-host.txt'):
            __logger__.warning("Launching with given IP address failed")
            __logger__.warning("Trying an ip address given by the system ")
            remove('./last-used-host.txt')
            main(False)


if __name__ == '__main__':
    main()
