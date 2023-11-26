class MovingEntity:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.is_moving = False
        self.movement_generator = None

    @property
    def position(self):
        return (self.x, self.y)
    
    def tween_to(self, dest_x: int, dest_y: int, time: int):
        dx = (dest_x - self.x) / time
        dy = (dest_y - self.y) / time
        for _ in range(time - 1):
            self.x += dx
            self.y += dy
            yield
        self.x = dest_x
        self.y = dest_y

    def start(self, dest_x: int, dest_y: int, time: int):
        self.is_moving = True
        self.movement_generator = self.tween_to(dest_x, dest_y, time)
    
    def update(self):
        try:
            if self.is_moving:
                next(self.movement_generator)
        except StopIteration:
            self.is_moving = False
            self.movement_generator = None
