import random

class Board:
    '''
    This class represents a 2-dimensional field where each tile has a value of 1 to 5, this represents the cost
    to move to this tile from an adjacent (N, E, S, W) tile.
    The field also contains a certain amount (25%) of obstacles which cannot be crossed.
    The representation of the field is an (n x n)-matrix where normal tiles are represented via an int (1-5)
    and obstacles by an 'X'. To create an instance of this class an integer n must be provided along which indicates
    the size of the (n x n)-field/matrix. Furthermore does this class contain two special 'points' denoted by 'start'
    and 'destination', these will be start and end positions of our path. Lastly, some algorithms will make use of a
    second matrix 'visited' which has the same size as the field matrix and is initially completely filled with 'False'
    values.
    '''
    def __init__(self, size):
        self.size = size
        self.generateBoard()  # Generates a size x size matrix with values of 1-5
        self.start = (0, 0)  # Sets start to (0, 0), this is the left upper corner
        self.destination = (size - 1, size - 1)  # Sets destination to the right lower corner
        self.generateObstacles()  # Changes a quarter of the cells to obstacles

    def __str__(self):  # Gives a string representation of the board
        return '\n'.join('  '.join(str(x) for x in row) for row in self.board)

    '''This function generates the board which is an n x n matrix with n equal to the size.
    The size must be given as parameter to the instance call'''
    def generateBoard(self):
        self.board = [[random.randint(1, 5) for column in range(self.size)] for row in range(self.size)]

    '''This function generates the obstacles on the board.
    Currently, 25% of the board is being covered in obstacles, obstacles are marked as an X instead of a integer'''
    def generateObstacles(self):
        for x in range(self.size ** 2 // 4):
            check = False
            # This loop prevents self.start and self.destination to be turned into obstacles
            while not check:
                row, column = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if (row, column) != self.start and (row, column) != self.destination and self.board[row][column] != 'X':
                    check = True
            self.board[row][column] = 'X'  # Set the value on the board to X

    '''This function will reset all the visitor flags back to False.'''
    def resetVisitorFlags(self):
        self.visited = [[False for x in range(self.size)] for y in range(self.size)]

    '''This function will set the start position to (row, column)'''
    def setStart(self, row, column):  # Sets the start position to board[row][column]
        if row >= self.size or column >= self.size or row < 0 or column < 0:
            raise ValueError('The row or column does not fit on the board!')
        if self.board[row][column] == 'X':
            self.board[row][column] = random.randint(1, 5)
        self.start = (row, column)

    '''This function will set the destination to (row, column)'''
    def setDestination(self, row, column):  # Sets the destination to board[row][column]
        if row >= self.size or column >= self.size or row < 0 or column < 0:
            raise ValueError('The row or column does not fit on the board!')
        if self.board[row][column] == 'X':
            self.board[row][column] = random.randint(1, 5)
        self.destination = (row, column)

    '''This function will change (row, column) into an obstacle'''
    def setObstacle(self, row, column):  # Turns board[row][column] into and obstacle!
        self.board[row][column] = 'X'

    '''Sets board[row][column] to a certain value, ca be used to turn an obstacle into a 'normal' value'''
    def setValue(self, row, column, value):
        self.board[row][column] = value
