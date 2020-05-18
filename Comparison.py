import Board
import time
import queue
import random

def AStar(board):
    board.resetVisitorFlags()
    agenda = queue.PriorityQueue()
    agenda.put((calculateHeuristic(board.start, board.destination)
                - board.board[board.start[0]][board.start[1]], [board.start]))
    while agenda.qsize() > 0:
        pointer = agenda.get()
        pathway, current_point = pointer[1], pointer[1][-1]
        shortest_distance_to_current = board.visited[current_point[0]][current_point[1]]
        travelled_distance = pointer[0] + board.board[current_point[0]][current_point[1]] - calculateHeuristic(current_point, board.destination)
        if str(shortest_distance_to_current).isdigit() and travelled_distance >= shortest_distance_to_current:
            continue
        board.visited[current_point[0]][current_point[1]] = travelled_distance
        if current_point == board.destination:
            return travelled_distance, pathway
        for point in filter(lambda point: not str(board.board[point[0]][point[1]]).isalpha()
                                          and point not in pathway
                                          and (not board.visited[point[0]][point[1]]
                                               or travelled_distance > board.visited[point[0]][point[1]])
                , findNeighbors(current_point, board.size)):
            agenda.put((calculateHeuristic(point, board.destination) + travelled_distance, pathway + [point]))
    return False

def calculateHeuristic(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])

def findNeighbors(point, size):
    nextPoints = []
    if point[0] != 0:
        nextPoints.append((point[0] - 1, point[1]))  # Add point above current
    if point[1] != 0:
        nextPoints.append((point[0], point[1] - 1))  # Add point left of current
    if point[0] != size - 1:
        nextPoints.append((point[0] + 1, point[1]))  # Add point below current
    if point[1] != size - 1:
        nextPoints.append((point[0], point[1] + 1))  # Add point right of current
    return nextPoints

# ---------------------------------------------------------------------------------------------------------------------
'''
This code was retrieved from https://www.redblobgames.com/pathfinding/a-star/implementation.html.
This implements the A* algorithm for path finding. However, it does not assign different weights to various cells
automatically. They can be added manually however in the "GridWithWeights subclass".
'''
class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        return id not in self.walls


    def neighbors(self, id):
        (x, y) = id
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0: results.reverse()  # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results


class GridWithWeights(SquareGrid):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.weights = {}

    def cost(self, from_node, to_node):
        return self.weights.get(to_node)


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


def a_star_search(graph, start, goal):
    frontier = queue.PriorityQueue()
    frontier.put((0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current_tuple = frontier.get()
        current = current_tuple[1]

        if current == goal:
            path, cost = [], cost_so_far[current]
            while current:
                path.append(current)
                current = came_from[current]
            return cost, path[::-1]

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put((priority, next))
                came_from[next] = current

    return False

# ---------------------------------------------------------------------------------------------------------------------
'''
https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
'''

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            travelled_distance = -maze[start[0]][start[1]]                              # Modification 1
            while current is not None:
                path.append(current.position)
                travelled_distance += maze[current.position[0]][current.position[1]]    # Modification 1
                current = current.parent
            return travelled_distance, path[::-1]                                       # Modification 1

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:     # Modification 2

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze)-1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] == 'X':     # Modification 3
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            closed = False                                  # Modification 4
            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    closed = True
                    break                               # Modification 4

            if closed:                                      # Modification 4
                continue                                    # Modification 4

            # Create the f, g, and h values
            child.g = current_node.g + maze[child.position[0]][child.position[1]]       # Modification 5
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1]) # Modification 6
            child.f = child.g + child.h

            # Child is already in the open list
            already_better = False                          # Modification 7
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    already_better = True                   # Modification 7
                    break

            if not already_better:                          # Modification 7
            # Add the child to the open list
                open_list.append(child)

    return False

# ---------------------------------------------------------------------------------------------------------------------
'''
From here on, the tests are set-up and executed.
'''

# This functions transforms the grid into the same field as the board
def copyObstaclesAndWeights(board, grid):
    for row in range(board.size):
        for column in range(board.size):
            if board.board[row][column] == 'X':
                grid.walls.append((row, column))
            else:
                grid.weights.update({(row, column): board.board[row][column]})

# This function will perform the tests
def test(size, amount, algorithms):
    timer1, timer2, timer3 = 0, 0, 0

    for i in range(amount):
        board = Board.Board(size)
        board.setStart(random.randint(0, board.size - 1), random.randint(0, board.size - 1))
        board.setDestination(random.randint(0, board.size - 1), random.randint(0, board.size - 1))

        if 'personal' in algorithms:
            start = time.time()
            personal = AStar(board)
            timer1 += (time.time() - start)

        if 'redblob' in algorithms:
            grid = GridWithWeights(size, size)
            copyObstaclesAndWeights(board, grid)
            start = time.time()
            redblob = a_star_search(grid, board.start, board.destination)
            timer2 += (time.time() - start)

        if 'swift' in algorithms:
            board.resetVisitorFlags()
            start = time.time()
            swift = astar(board.board, board.start, board.destination)
            timer3 += (time.time() - start)
        '''
        # This code can be activated to show the cases where the output of the three algorithms isn't the same.
        # Note that this will only work in test 1-4 
        if 'swift' in algorithms:
            if personal != redblob != swift:
                print(personal)
                print(redblob)
                print(swift)
                print("")
        '''

    result = []
    if 'personal' in algorithms:
        result.append(round(timer1, 3))
    if 'redblob' in algorithms:
        result.append(round(timer2, 3))
    if 'swift' in algorithms:
        result.append(round(timer3, 3))
    print(result)


# These are the tests, which are currently executed 10 times each.
print('Test 1:')
[test(5, 2000, ['personal', 'redblob', 'swift']) for x in range(10)]

print('\nTest 2:')
[test(10, 1000, ['personal', 'redblob', 'swift']) for x in range(10)]

print('\nTest 3:')
[test(20, 500, ['personal', 'redblob', 'swift']) for x in range(10)]

print('\nTest 4:')
[test(50, 100, ['personal', 'redblob', 'swift']) for x in range(10)]

print('\nTest 5:')
[test(100, 50, ['personal', 'redblob']) for x in range(10)]

print('\nTest 6:')
[test(200, 20, ['personal']) for x in range(10)]
