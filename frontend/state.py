
class State:
  x: float
  y: float
  is_touching: bool
  is_scrolling: bool
  is_dragging: bool
  last_time_sent: int
  def __init__(self, **kwards):
    self.x = kwards["x"]
    self.y = kwards["y"]
    self.is_touching = kwards["is_touching"]
    self.is_scrolling = kwards["is_scrolling"]
    self.is_dragging = kwards["is_dragging"]
    self.last_time_sent = kwards["last_time_sent"]
    
  def update(self, x, y, is_touching=None, is_scrolling=None, is_dragging=None, last_time_sent=None):
    """ 📦 updates the data fields for this class"""
    self.x = x
    self.y = y
    if is_touching != None:
      self.is_touching = is_touching
    if is_scrolling != None:
      self.is_scrolling = is_scrolling
    if last_time_sent != None:
      self.last_time_sent = last_time_sent

__all__ = ["State"]
