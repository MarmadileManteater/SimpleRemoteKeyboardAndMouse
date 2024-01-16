
from js_api import query_selector, clone_template, append_child, remove_child, inner_html, set_attribute, set_timeout, style

toast_template = query_selector("#toast")
toast_center = query_selector("#toast-center")

def toast(icon, message):
  new_toast = clone_template(toast_template)
  icon_element = query_selector(".icon", new_toast)
  inner_html(icon_element, icon)
  message_element = query_selector(".message", new_toast)
  inner_html(message_element, message)
  set_attribute(new_toast, 'class', 'toast')
  append_child(toast_center, new_toast)
  set_timeout(lambda : set_attribute(new_toast, 'data-visibility', 'fade-out'), 3000)
  set_timeout(lambda : remove_child(toast_center, new_toast), 5000)

status_light = query_selector('#status-light')

def indicate_status(status_color='#04ff89', time=100):
  if status_light:
    style(status_light, {
      'background-color': status_color
    })
    set_timeout(lambda : style(status_light, { 'background-color': 'grey'}), time)


__all__ = ['toast', 'indicate_status', 'toast_center']
