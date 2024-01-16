
from toast import toast

async def request(endpoint, method = 'GET', body = None):
  try:
    try:
      response = await fetch(endpoint, {
        "signal": JS('AbortSignal.timeout(5000)'),
        "method": method,
        "body": body
      })
      json = await response.json()
      if response.status != 200:
        raise Exception(f'Status code {response.status} does not indiciate success. <br/> Inner error: {json.message}')
      return json
    except Exception as error:
      if error.name == 'AbortError':
        raise Exception('Request timed out')
      else:
        raise error
  except Exception as error:
    toast(f"⛔", error)

async def input_api(command_type, parameters):
  return await request('/api/v2/input', 'POST', JSON.stringify({
    'commandType': command_type,
    'parameters': parameters
  }))

async def mouse(x_move, y_move, is_scrolling = False, is_dragging = False):
  endpoint = "drag" if is_dragging else "scroll" if is_scrolling else "move"
  return await request(f"/mouse{endpoint}/{x_move}/{y_move}")

__all__ = ['request', 'input_api', 'mouse']
