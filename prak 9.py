import tkinter as tk

class GameEntity:
    def _init_(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def remove(self):
        self.canvas.delete(self.item)

class Ball(GameEntity):
    def _init_(self, canvas, x, y):
        self.radius = 12
        self.direction = [1, -1]
        self.velocity = 6  # Adjust speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#FFFFFF')  # Ball color: white
        super()._init_(canvas, item)

    def update_position(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        self.move(self.direction[0] * self.velocity, self.direction[1] * self.velocity)

    def handle_collision(self, entities):
        coords = self.get_position()
        center_x = (coords[0] + coords[2]) / 2
        if len(entities) > 1:
            self.direction[1] *= -1
        elif len(entities) == 1:
            entity = entities[0]
            entity_coords = entity.get_position()
            if center_x > entity_coords[2]:
                self.direction[0] = 1
            elif center_x < entity_coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for entity in entities:
            if isinstance(entity, Block):
                entity.reduce_hits()

class Paddle(GameEntity):
    def _init_(self, canvas, x, y):
        self.width = 100
        self.height = 15
        self.attached_ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill='#C0C0C0')  # Paddle color: gray
        super()._init_(canvas, item)

    def attach_ball(self, ball):
        self.attached_ball = ball

    def shift(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super().move(offset, 0)
            if self.attached_ball:
                self.attached_ball.move(offset, 0)

class Block(GameEntity):
    COLORS = {1: '#FFFFFF', 2: '#AAAAAA', 3: '#555555'}  # Block durability colors: white to dark gray

    def _init_(self, canvas, x, y, durability):
        self.width = 70
        self.height = 25
        self.durability = durability
        color = Block.COLORS[durability]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2,
                                       x + self.width / 2, y + self.height / 2,
                                       fill=color, tags='block')
        super()._init_(canvas, item)

    def reduce_hits(self):
        self.durability -= 1
        if self.durability == 0:
            self.remove()
        else:
            self.canvas.itemconfig(self.item, fill=Block.COLORS[self.durability])

class BrickBreaker(tk.Frame):
    def _init_(self, master):
        super()._init_(master)
        self.lives = 3
        self.width = 620
        self.height = 420
        self.canvas = tk.Canvas(self, bg='#000000', width=self.width, height=self.height)  # Background color: black
        self.canvas.pack()
        self.pack()

        self.objects = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 350)
        self.objects[self.paddle.item] = self.paddle

        for x in range(10, self.width - 10, 80):
            self.add_block(x + 40, 60, 3)
            self.add_block(x + 40, 90, 2)
            self.add_block(x + 40, 120, 1)

        self.display = None
        self.initialize_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.shift(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.shift(20))

    def initialize_game(self):
        self.spawn_ball()
        self.update_lives_display()
        self.message = self.create_text(310, 200, 'Press Space to Start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def spawn_ball(self):
        if self.ball:
            self.ball.remove()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) / 2
        self.ball = Ball(self.canvas, x, 330)
        self.paddle.attach_ball(self.ball)

    def add_block(self, x, y, durability):
        block = Block(self.canvas, x, y, durability)
        self.objects[block.item] = block

    def create_text(self, x, y, text, size=35):
        font = ('Arial', size)
        return self.canvas.create_text(x, y, text=text, font=font, fill='#FFFFFF')  # Text color: white

    def update_lives_display(self):
        text = f'Lives: {self.lives}'
        if self.display is None:
            self.display = self.create_text(60, 30, text, 15)
        else:
            self.canvas.itemconfig(self.display, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.message)
        self.paddle.attached_ball = None
        self.run_game_loop()

    def run_game_loop(self):
        self.check_collisions()
        if not self.canvas.find_withtag('block'):
            self.ball.velocity = 0
            self.create_text(310, 200, 'You Win!')
        elif self.ball.get_position()[3] >= self.height:
            self.ball.velocity = 0
            self.lives -= 1
            if self.lives < 0:
                self.create_text(310, 200, 'Game Over')
            else:
                self.after(1000, self.initialize_game)
        else:
            self.ball.update_position()
            self.after(50, self.run_game_loop())

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        hits = self.canvas.find_overlapping(*ball_coords)
        hit_objects = [self.objects[h] for h in hits if h in self.objects]
        self.ball.handle_collision(hit_objects)

if __name__ == '_main_':
    root = tk.Tk()
    root.title('Brick Breaker Game')
    game = BrickBreaker(root)
    game.mainloop()
