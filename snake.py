from collections import deque
import random


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Snake:
    def __init__(self, board_size):
        self.board_size = board_size
        self.possible_directions = ["u", "r", "d", "l"]
        self.initial_length = 3
        x = random.randint(2, board_size[0] - self.initial_length)
        y = random.randint(2, board_size[1] - self.initial_length)
        self.start_position = Point(x, y)

        start_direction = self.possible_directions[random.randint(0, 3)]
        self.initialize_snake_body(start_direction)
        self.current_direction = start_direction
        self.generate_apple()

    def initialize_snake_body(self, start_direction):
        head = self.start_position

        snake_body = []
        match(start_direction):
            case 'u':
                snake_body = [head, Point(head.x, head.y + 1), Point(head.x, head.y + 2)]
            case 'r':
                snake_body = [head, Point(head.x - 1, head.y), Point(head.x - 2, head.y)]
            case 'd':
                snake_body = [head, Point(head.x, head.y  - 1), Point(head.x, head.y - 2)]
            case 'l':
                snake_body = [head, Point(head.x + 1, head.y), Point(head.x + 2, head.y)]

        self.body = deque(
            snake_body
        )  # for easier adding and removing from both ends of the snake
        self.is_alive = True

    def generate_apple(self):
        width = self.board_size[0]
        height = self.board_size[1]
        apple_options = [Point(i // width,i % width) for i in range(width * height) if Point(i // width,i % width) not in self.body]
        if apple_options:
            self.apple = random.choice(apple_options)
        else:
            print("End game or error")
            return

    

    def is_valid(self, new_position):
        if (
            new_position.x < 0
            or new_position.x > self.board_size[0] - 1
            or new_position.y < 0
            or new_position.y > self.board_size[1] - 1
        ):
            return False
    
        if new_position == self.body[-1]: #Tail is valid new position cuz tail will move
            return True
        elif new_position in self.body:
            return False

        return True

    def move(self):
        if not self.is_alive:
            return
        
        new_direction = self.possible_directions[random.randint(0, 3)] # Later change this not to be random

        head = self.body[0]
        match(new_direction):
            case 'u':    
                if self.current_direction == 'd':                
                    new_position = Point(head.x, head.y + 1) 
                else:
                    new_position = Point(head.x, head.y - 1)
                    self.current_direction = new_direction
            case 'r':
                if self.current_direction == 'l':
                    new_position = Point(head.x - 1, head.y)  
                else:
                    new_position = Point(head.x + 1, head.y)
                    self.current_direction = new_direction
            case 'd':
                if self.current_direction == 'u':
                    new_position = Point(head.x, head.y - 1)  
                else:
                    new_position = Point(head.x, head.y + 1)
                    self.current_direction = new_direction
            case 'l':
                if self.current_direction == 'r':
                    new_position = Point(head.x + 1, head.y)  
                else:
                    new_position = Point(head.x - 1, head.y)
                    self.current_direction = new_direction
            case _ :
                new_position = Point(1,2)

        if self.is_valid(new_position):
            self.body.appendleft(new_position)  # new head
            self.body.pop()
            # remove tail
        else:
            self.is_alive = False
        
        return
    
    def __str__(self):
        return f"Body: {list(map(str, self.body))}"
