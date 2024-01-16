
from distance import calculate_distance
from js_api import query_selector, query_selector_all, add_event_listener, prevent_default, get_attribute, set_attribute, encode_uri, type_of, date, get_time
from backend_api import mouse, request, input_api
from state import State
from toast import toast

api_version = query_selector('meta[name="api-version"]')
__api__ = get_attribute(api_version, 'content')

state = State(x=0, y=0, is_touching=False, is_scrolling=False, is_dragging=False, last_time_sent=0)

def map_button_event_to_route(button, event, get_route_info):
  if __api__ == 'v1':
    route_type = typeof(route)
    # if the route is a function, evaluate it and fetch it, and if it is a string, just fetch it
    add_event_listener(button, event, lambda: request(get_route_info().route if typeof(get_route_info) == 'function' else get_route_info))
  elif __api__ == 'v2':
    def on_event():
      info = get_route_info()
      input_api(info.commandType, info.parameters)
    add_event_listener(button, event, on_event)


keyboard = query_selector('.keyboard')
typewrite_button = query_selector('.send')
def typewrite_info():
  content = keyboard.value
  keyboard.value = ''
  if __api__ == 'v1':
    return {
      'route': f"/typewrite?query={encode_uri(content)}",
      'method': 'GET',
      'body': None
    }
  elif __api__ == 'v2':
    return {
      'commandType': 'typewrite',
      'parameters': [content]
    }
map_button_event_to_route(typewrite_button, 'click', typewrite_info)

for element in query_selector_all('.ui'):
  send = get_attribute(element, 'data-send')
  if send:
    def send_key_info(send):
      def callback():
        if __api__ == 'v1':
          return {
            'route': f"/send/{send}"
          }
        elif __api__ == 'v2':
          return {
            'commandType': 'send-key',
            'parameters': [send]
          }
      return callback
    map_button_event_to_route(element, 'click', send_key_info(send))
  hot_key = get_attribute(element, 'data-hotkey')
  if hot_key:
    def hot_key_info(hot_key):
      def callback():
        if __api__ == 'v1':
          return {
            'route': f"/send-hotkey/{hot_key}"
          }
        elif __api__ == 'v2':
          return {
            'commandType': 'send-hotkey',
            'parameters': hot_key.split(',')
          }
      return callback
    map_button_event_to_route(element, 'click', hot_key_info(hot_key))
  toggle = get_attribute(element, 'data-toggle')
  if toggle:
    if toggle == 'drag':
      def freeze_element_with_callback(element):
        """ 🧊 freeze specific `element` for a callback """
        def callback():
          # switch the toggle
          state.is_dragging = state.is_dragging == False
          set_attribute(element, 'data-active', state.is_dragging)
          if __api__ == 'v1':
            return {
              'route': '/disabledrag'
            }
          elif __api__ == 'v2':
            return {
              'commandType': 'disabledrag',
              'parameters': []
            }
        return callback
      map_button_event_to_route(element, 'click', freeze_element_with_callback(element))

touchpad = query_selector('.touch')

def on_touch_start(e):
  """ called when the touchpad is first 👆touched """
  prevent_default(e)
  state.update(e.touches[0].clientX, e.touches[0].clientY, True, len(e.touches) > 0)
add_event_listener(touchpad, 'touchstart', on_touch_start)

def on_touch_move(e):
  """ called when the touchpad is being 👆touched and the touch is changing position """
  if state.last_time_sent < get_time(date()) - 150:
    touches = [(touch.clientX, touch.clientY) for touch in e.touches]
    x, y = touches[0]
    dx = int(state.x - x)
    dy = int(state.y - y)

    state.update(x, y, None, calculate_distance(touches[0], touches[1]) < 100 if len(touches) == 2 else False, None, get_time(date()))
    if __api__ == 'v1':
      mouse(-dx * 2, -dy * 2, state.is_scrolling, state.is_dragging)
    elif __api__ == 'v2':
      mouse_type = 'drag' if state.is_dragging else 'scroll' if state.is_scrolling else 'move'
      input_api(f'mouse{mouse_type}', (-dx * 2, -dy * 2))

add_event_listener(touchpad, 'touchmove', on_touch_move)

def on_touch_end(e):
  """ called when the touchpad is no longer being ✋touched """
  state.update(0, 0, False, False)
add_event_listener(touchpad, 'touchend', on_touch_end)
