
from distance import calculate_distance
from js_api import query_selector, query_selector_all, add_event_listener, prevent_default, get_attribute, set_attribute, encode_uri, type_of, date, get_time
from backend_api import mouse, request
from state import State
from toast import toast

state = State(x=0, y=0, is_touching=False, is_scrolling=False, is_dragging=False, last_time_sent=0)

def map_button_event_to_route(button, event, route):
  route_type = typeof(route)
  # if the route is a function, evaluate it and fetch it, and if it is a string, just fetch it
  add_event_listener(button, event, lambda: request(route() if type_of(route) == 'function' else route))
  
keyboard = query_selector('.keyboard')
typewrite_button = query_selector('.send')
def typewrite():
  content = keyboard.value
  keyboard.value = ''
  return f"/typewrite?query={encode_uri(content)}"
map_button_event_to_route(typewrite_button, 'click', typewrite)

for element in query_selector_all('.ui'):
  send = get_attribute(element, 'data-send')
  if send:
    map_button_event_to_route(element, 'click', f"/send/{send}")
  hot_key = get_attribute(element, 'data-hotkey')
  if hot_key:
    map_button_event_to_route(element, 'click', f"/send-hotkey/{hot_key}")
  toggle = get_attribute(element, 'data-toggle')
  if toggle:
    if toggle == 'drag':
      def toggle_drag(element):
        def t():
          # switch the toggle
          state.is_dragging = state.is_dragging == False
          set_attribute(element, 'data-active', state.is_dragging)
          return '/disabledrag'
        return t
      map_button_event_to_route(element, 'click', toggle_drag(element))

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
    mouse(-dx * 2, -dy * 2, state.is_scrolling, state.is_dragging)
add_event_listener(touchpad, 'touchmove', on_touch_move)

def on_touch_end(e):
  """ called when the touchpad is no longer being ✋touched """
  state.update(0, 0, False, False)
add_event_listener(touchpad, 'touchend', on_touch_end)
