from collections import deque
from neural_network import NeuralNetwork
import random
import torch
import numpy as np
import copy


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __eq__(self, other):
        return isinstance(other, Point) and self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Vision:
    def __init__(self, distance_to_apple, distance_to_wall, distance_to_body):
        self.distance_to_apple = float(distance_to_apple)
        self.distance_to_wall = float(distance_to_wall)
        self.distance_to_body = float(distance_to_body)


class Snake:
    def __init__(self, board_size, model=None):
        self.board_size = board_size
        self.possible_directions = ["u", "r", "d", "l"]
        self.initial_length = 3
        self.score = 0
        self.fitness = 0
        self.steps = 0
        self.steps_since_last_apple = 0
        self.vision = [
            None for _ in range(8)
        ]  # snake can see in 8 directions (south, east , south-east ...)
        self.vision_steps = [
            Point(-1, 0),
            Point(-1, -1),
            Point(0, -1),
            Point(1, -1),
            Point(1, 0),
            Point(1, 1),
            Point(0, 1),
            Point(-1, 1),
        ]
        if model == None:
            self.model = NeuralNetwork()
        else:
            self.model = model
        x = random.randint(2, board_size[0] - self.initial_length)
        y = random.randint(2, board_size[1] - self.initial_length)
        self.start_position = Point(x, y)
        start_direction = self.possible_directions[random.randint(0, 3)]
        self.initialize_snake_body(start_direction)
        self.current_direction = start_direction
        self.current_tail_direction = start_direction
        self.generate_apple()

    def initialize_snake_body(self, start_direction):
        head = self.start_position

        snake_body = []
        match (start_direction):
            case "u":
                snake_body = [
                    head,
                    Point(head.x, head.y + 1),
                    Point(head.x, head.y + 2),
                ]
            case "r":
                snake_body = [
                    head,
                    Point(head.x - 1, head.y),
                    Point(head.x - 2, head.y),
                ]
            case "d":
                snake_body = [
                    head,
                    Point(head.x, head.y - 1),
                    Point(head.x, head.y - 2),
                ]
            case "l":
                snake_body = [
                    head,
                    Point(head.x + 1, head.y),
                    Point(head.x + 2, head.y),
                ]

        self.body = deque(
            snake_body
        )  # for easier adding and removing from both ends of the snake
        self.is_alive = True


    def calculate_fitness(self):
        self.fitness = self.steps + 2**self.score - 0.25*self.steps # encourage early exploration, more apple = better and we want it to be efficient with movement
        self.fitness = max(self.fitness, 0)

    def generate_apple(self):
        width = self.board_size[0]
        height = self.board_size[1]
        apple_options = [
            Point(x, y)
            for x in range(width)
            for y in range(height)
            if Point(x, y) not in self.body
        ]
        if apple_options:
            self.apple = random.choice(apple_options)
        else:
            print("End game or error")
            return

    def is_inside_grid(self, new_position):
        if (
            new_position.x < 0
            or new_position.x > self.board_size[0] - 1
            or new_position.y < 0
            or new_position.y > self.board_size[1] - 1
        ):
            return False

        return True

    def is_valid(self, new_position):
        if (
            new_position == self.body[-1]
        ):  # Tail is valid new position cuz tail will move
            return True
        elif new_position in self.body:
            return False

        return self.is_inside_grid(new_position)

    def look_in_direction(self, vision_step):
        distance_to_apple = -1
        distance_to_wall = -1
        distance_to_body = -1

        current_tile = copy.deepcopy(self.body[0])
        current_tile.x += vision_step.x
        current_tile.y += vision_step.y
        total_distance = 1  # first tile from our head in direction

        is_body_found = False
        is_apple_found = False
        while self.is_inside_grid(current_tile):
            if not is_body_found and current_tile in self.body:
                is_body_found = True
                distance_to_body = total_distance

            if not is_apple_found and current_tile == self.apple:
                is_apple_found = True
                distance_to_apple = total_distance

            total_distance += 1
            current_tile.x += vision_step.x
            current_tile.y += vision_step.y

        distance_to_wall = 1 / total_distance
        distance_to_apple = 1 if distance_to_apple != -1 else 0
        distance_to_body = 1 if distance_to_body != -1 else 0

        vision_in_direction = Vision(
            distance_to_apple, distance_to_wall, distance_to_body
        )
        return vision_in_direction

    def create_input_for_nn(self):
        input_array = np.array(
            list(
                map(
                    lambda x: [
                        x.distance_to_apple,
                        x.distance_to_wall,
                        x.distance_to_body,
                    ],
                    self.vision,
                )
            )
        )

        snake_direction_array = [0 for _ in range(len(self.possible_directions))]
        snake_direction_array[
            self.possible_directions.index(self.current_direction)
        ] = 1  # array of directions when only one of them have value 1
        input_array = np.append(input_array, snake_direction_array)

        tail_direction_array = [0 for _ in range(len(self.possible_directions))]
        tail_direction_array[
            self.possible_directions.index(self.current_tail_direction)
        ] = 1
        input_array = np.append(input_array, tail_direction_array)

        return input_array

    def look(self):
        for i, vision_step in enumerate(self.vision_steps):
            vision_in_direction = self.look_in_direction(vision_step)
            self.vision[i] = vision_in_direction

    def update(self):
        self.look()
        input_array = (
            self.create_input_for_nn()
        )  # this should be snake vision + encoded direction of a head + encoded direction of a tail
        output = self.model(torch.tensor(input_array).float())
        self.new_direction = self.possible_directions[torch.argmax(output).item()]

    def move(self):
        if not self.is_alive:
            return

        head = self.body[0]
        match (self.new_direction):
            case "u":
                if self.current_direction == "d":
                    new_position = Point(head.x, head.y + 1)
                else:
                    new_position = Point(head.x, head.y - 1)
                    self.current_direction = self.new_direction
            case "r":
                if self.current_direction == "l":
                    new_position = Point(head.x - 1, head.y)
                else:
                    new_position = Point(head.x + 1, head.y)
                    self.current_direction = self.new_direction
            case "d":
                if self.current_direction == "u":
                    new_position = Point(head.x, head.y - 1)
                else:
                    new_position = Point(head.x, head.y + 1)
                    self.current_direction = self.new_direction
            case "l":
                if self.current_direction == "r":
                    new_position = Point(head.x + 1, head.y)
                else:
                    new_position = Point(head.x - 1, head.y)
                    self.current_direction = self.new_direction
            case _:
                new_position = Point(1, 2)

        if self.is_valid(new_position):
            if new_position == self.apple:
                self.body.appendleft(new_position)  # new head
                self.score += 1
                self.steps_since_last_apple = 0
                self.generate_apple()
            else:
                self.steps_since_last_apple += 1
                self.body.pop()  # remove tail
                self.body.appendleft(new_position)

            self.steps += 1
            p1 = self.body[-1]
            p2 = self.body[-2]
            difference = p2 - p1
            if difference.x > 0:
                self.current_tail_direction = "r"
            elif difference.x < 0:
                self.current_tail_direction = "l"
            elif difference.y > 0:
                self.current_tail_direction = "d"
            elif difference.y < 0:
                self.current_tail_direction = "u"

        else:
            self.is_alive = False

        return

    def __str__(self):
        return f"Body: {list(map(str, self.body))}, Fitness: {self.fitness}"
