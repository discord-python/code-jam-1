from random import randint


class SnakeGame:
    """
    Simple Snake game
    """

    def __init__(self, board_dimensions):
        self.board_dimensions = board_dimensions
        self.restart()

    def restart(self):
        """
        Restores game to default state
        """

        self.snake = Snake(positions=[[2, 2], [2, 1]])
        self.putFood()
        self.score = 0

    def __str__(self):
        """
        Draw the board
        """
        # create empty board
        # board_string = "+" + "-" * (self.board_dimensions[1]) + "+" + "\n"
        board_string = ""
        for i in range(self.board_dimensions[0]):
            # row_string = "|"
            row_string = ""
            # draw snake
            for j in range(self.board_dimensions[1]):
                if [i, j] == self.snake.positions[0]:
                    row_string += ":python:"  # head
                elif [i, j] in self.snake.positions:
                    row_string += "🐍"
                elif [i, j] == self.food:
                    row_string += "🍕"
                else:
                    row_string += "◻️"
            # row_string += "|\n"
            board_string += row_string + "\n"
        # board_string += "+" + "-" * (self.board_dimensions[1]) + "+\n"

        return board_string

    def move(self, direction):
        """
        Executes one movement.
        Returns information about the movement:
        "ok", "forbidden", "lost", "food".
        """

        direction_dict = {
            "right": (0, 1),
            "left": (0, -1),
            "up": (-1, 0),
            "down": (1, 0)
        }
        move_status = self.snake.move(direction_dict[direction])

        if self.isLost():
            move_status = "lost"
            self.restart()

        if self.isEating():
            self.snake.grow()
            move_status = "grow"
            self.putFood()
            self.score += 1

        return move_status

    def isLost(self):
        head = self.snake.head

        if (head[0] == -1 or
                head[1] == -1 or
                head[0] == self.board_dimensions[0] or
                head[1] == self.board_dimensions[1] or
                head in self.snake.positions[1:]):
            return True
        
        return False

    def putFood(self):
        valid = False
        while not valid:
            i = randint(0, self.board_dimensions[0] - 1)
            j = randint(0, self.board_dimensions[1] - 1)

            if [i, j] not in self.snake.positions:
                valid = True

        self.food = [i, j]

    def isEating(self):
        if self.snake.head == self.food:
            return True
        return False


class Snake:
    """
    Actual snake in the game.
    """

    def __init__(self, positions):
        self.positions = positions
        self.head = positions[0]

    def move(self, velocity):
        """
        Executes one movement.

        Returns information about the movement:
        "ok", "forbidden"
        """
        if not self.isPossible(velocity):
            print("Movement not allowed")
            return "forbidden"

        # delete tail but store it, as we might want the snake to grow
        self.deletedTail = self.positions[-1]
        self.positions = self.positions[:-1]

        # move head
        self.head = [self.head[0] + velocity[0],
                     self.head[1] + velocity[1]]
        self.positions.insert(0, self.head)

        return "ok"

    def isPossible(self, velocity):
        """
        Check Snake is trying to do an 180º turn.
        """
        newHead = [self.head[0] + velocity[0],
                   self.head[1] + velocity[1]]
        if newHead == self.positions[1]:
            return False
        return True

    def grow(self):
        """
        Makes the snake grow one square.
        """
        self.positions.append(self.deletedTail)
