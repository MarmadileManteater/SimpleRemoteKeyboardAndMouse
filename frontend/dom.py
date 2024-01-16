
# snakecase versions of common dom functions

def query_selector(query, target=document):
  return target.querySelector(query)

def query_selector_all(query, target=document):
  return target.querySelectorAll(query)

def add_event_listener(element, typeOf, listener):
  return element.addEventListener(typeOf, listener)

def prevent_default(event):
  event.preventDefault()

def clone_template(template_element):
  tagName = template_element.getAttribute('tag-name')
  root = document.createElement(tagName)
  root.innerHTML = template_element.innerHTML
  return root

def append_child(parent, child):
  parent.appendChild(child)
  
def prepend_child(parent, child):
  parent.insertBefore(child, parent.firstChild)

def remove_child(parent, child):
  parent.removeChild(child)

def inner_html(element, html):
  element.innerHTML = html

def set_attribute(element, key, value):
  element.setAttribute(key, value)

def get_attribute(element, key):
  return element.getAttribute(key)

__all__ = ['query_selector', 'query_selector_all', 'add_event_listener', 'prevent_default', 'clone_template', 'append_child', 'prepend_child', 'remove_child', 'inner_html', 'set_attribute', 'get_attribute']
