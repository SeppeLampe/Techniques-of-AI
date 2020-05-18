import Board
import datetime
import functools
import queue
import random
import time
import tkinter as tk

'''This function will generate a board and then call a function (showMatrix()) to visualize the field to the user.
It takes an optional parameter size as input which defines the size (n) of the (n x n)-matrix. Default value is
randomly chosen somewhere between 10 & 50 (including both 10 and 50).'''
def createBoard(size=random.randint(10, 51)):
    global board
    board = Board.Board(size)       #  Creates a global variable 'board'
    showMatrix()                    # Calls the showMatrix function for visualizing the board


'''This function visualizes the board as a matrix of buttons and places them in a separate frame.'''
def showMatrix():
    global buttonmatrix, matrixframe
    matrixcanvas.delete("all") # Clears the matrix shown on the GUI
    matrixframe = tk.Frame(matrixcanvas)  # This results in emptying the matrixframe more or less
    # This will generate a button for each cell on the field, see the 'generateMatrixButton' for more detailed info
    buttonmatrix = [[generateMatrixButton(row, column) for column in range(board.size)] for row in range(board.size)]
    # This places the matrixframe with all the buttons on the right place in the canvas
    matrixcanvas.create_window(matrixcanvas.winfo_width() // 2, 0,
                               anchor='n', window=matrixframe)
    # The next few lines are in order to generate and implement the scrollbar which can be used for large matrices
    matrixcanvas.update()
    matrixcanvas.pack(fill='both')
    matrixcanvas.bind("<MouseWheel>", lambda event: matrixcanvas.yview_scroll(int(-1*(event.delta/120)), "units"))

'''This function generates a button on the GUI, this button is of course related to the board.board matrix.'''
def generateMatrixButton(row, column):
    # Firstly, we will check which color we will need to set the background to, based on the board.board cell value
    bg = 'white'
    if board.board[row][column] == 'X':
        bg = 'black'
    elif (row, column) == board.start:
        bg = 'green'
    elif (row, column) == board.destination:
        bg = 'red'
    # This generates a button which displays the value of the board matrix on the button
    button = tk.Button(matrixframe, text=board.board[row][column], width=3, bg=bg,
                       command=lambda r=row, c=column: updateValue(r, c))
    # This makes it possible to scroll over the buttons to go down/up in large matrices
    button.bind("<MouseWheel>", lambda event: matrixcanvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    # This places the button on the right spot in the GUI
    button.grid(row=row, column=column)
    return button


'''This function updates the values of the matrix based on which option is active (increase or decrease the value of a 
cell, turn it into an obstacle/start/destination or turn it into 1.'''
def updateValue(row, column):
    current_action = actionvar.get()  # Get the current selected status of the button
    current_value = board.board[row][column]
    if current_action == "increment it by 1":
        if str(current_value).isdigit():  # Only when the pressed cell is a number we will increase it by 1
            board.setValue(row, column, current_value + 1)
    elif current_action == 'lower it by 1':
        if str(current_value).isdigit():  # Only when the pressed cell is a number we will decrease it by 1
            if current_value > 1:  # We cannot let the value go below 1, otherwise the heuristic (A*) will be admissible
                board.setValue(row, column, current_value - 1)
    elif current_action == 'turn it into an obstacle':
        if (row, column) != board.start and (row, column) != board.destination:
            board.setValue(row, column, 'X')
            buttonmatrix[row][column]["bg"] = 'black'
    elif current_action == 'turn the obstacle into a 1':
        if (row, column) != board.start and (row, column) != board.destination:
            board.setValue(row, column, 1)
            buttonmatrix[row][column]["bg"] = 'white'
    elif current_action == "set the start location there":
        resetColors()  # Remove the currently shown path since the previous path becomes irrelevant
        pointer = board.start
        board.setStart(row, column)
        if pointer == board.destination:
            buttonmatrix[pointer[0]][pointer[1]].config(bg='red', text=board.board[pointer[0]][pointer[1]])
        else:
            buttonmatrix[pointer[0]][pointer[1]].config(bg='white', text=board.board[pointer[0]][pointer[1]])
        buttonmatrix[row][column]["bg"] = 'green'
    elif current_action == "set the destination there":
        resetColors()  # Remove the currently shown path since the previous path becomes irrelevant
        pointer = board.destination
        board.setDestination(row, column)
        if pointer == board.start:
            buttonmatrix[pointer[0]][pointer[1]].config(bg='green', text=board.board[pointer[0]][pointer[1]])
        else:
            buttonmatrix[pointer[0]][pointer[1]].config(bg='white', text=board.board[pointer[0]][pointer[1]])
        buttonmatrix[row][column]["bg"] = 'red'
    buttonmatrix[row][column]["text"] = board.board[row][column]


'''This function resets the colors of the board before calculating the pathway. This is so that the user can keep
looking at the pathway once the calculation is finished and so that it disappears when the model is run again,
potentially with a different algorithm.'''
def resetColors():
    for row in range(board.size):
        for column in range(board.size):
            if buttonmatrix[row][column]['bg'] == 'green' and (row, column) != board.start:
                if (row, column) != board.destination:
                    buttonmatrix[row][column]['bg'] = 'white'
                else:
                    buttonmatrix[row][column]['bg'] = 'red'
    root.update()


'''This function configures the output for the label which is shown when an action (set start, increase by 1, ...)
is activated.'''
def actionsel():
    selection = "Press a cell in order to " + str(actionvar.get())
    sellabel.config(text=selection)


'''This function configures the output for the label which is shown when an algorithm is selected.'''
def algsel():
    selection = "You have selected " + str(algvar.get())
    alglabel.config(text=selection)


'''This function is called when the 'Calculate pathway' button is pressed. This function ensures that the correct
algorithm is called with the right parameters.'''
def calculatePathway():
    tracepath = tracevar.get()
    sleeptime = sleepscale.get()
    algorithm = algvar.get()
    if algorithm == "Algorithm A*":
        uniformCostOrAStar(sleeptime=sleeptime, tracepath=tracepath)
    elif algorithm == "Breadth First Search":
        depthOrBreadthFirstSearch(sleeptime=sleeptime, tracepath=tracepath)
    elif algorithm == "Depth First Search":
        depthOrBreadthFirstSearch(sleeptime=sleeptime, breadth=False, tracepath=tracepath)
    elif algorithm == "Uniform Cost Search":
        uniformCostOrAStar(sleeptime=sleeptime, astar=False, tracepath=tracepath)


'''This function colors every button in 'pathway' green, this will be called between every step of the calculation or
after a path has been found based on the selection of 'trace pathway' in the GUI'''
def showCalculation(pathway):
    for row, column in pathway:
        buttonmatrix[row][column]["bg"] = 'green'
    root.update()


'''This function colors every button in 'pathway' white, this will be called between every step of the calculation
if the 'trace path' in the GUI is active and right after pressing 'calculate pathway' on the GUI'''
def unshowCalculation(pathway):
    for row, column in pathway:
        buttonmatrix[row][column]["bg"] = 'white'
    root.update()


'''This function will be used to calculate the pathway for the Algorithm A* and Uniform Cost Search (UCS).'''
def uniformCostOrAStar(sleeptime=0, astar=True, tracepath=False):
    start = datetime.datetime.now() # Starts a timer
    resetColors()   # Recolors the previous shown pathway (if there is one) back to white
    board.resetVisitorFlags()   # Resets the visitor flags back to False
    # Both A* and UCS use a priorityqueue as agenda, that's also why I have combined both in one function
    agenda = queue.PriorityQueue()
    previous_pathway = []
    # If the algorithm is A* then we will incorporate a heuristic, we will subtract the board.start value since this
    # will be added later on. If the algorithm is UCS then we will not incorporate the heuristic. An item in the agenda
    # will look like this (value, [travelled_pathway]) where value is either heuristic + travelled distance (A*) or just
    # travelled distance in case of UCS.
    if astar:
        agenda.put((calculateHeuristic(board.start, board.destination)
                    - board.board[board.start[0]][board.start[1]], [board.start]))
        alg = "Algorithm A*"
    else:
        agenda.put([- board.board[board.start[0]][board.start[1]], [board.start]])
        alg = "Uniform Cost Search"
    while agenda.qsize() > 0:
        pointer = agenda.get() # Gets the first item from the priorityqueue
        pathway, current_point = pointer[1], pointer[1][-1]
        shortest_distance_to_current = board.visited[current_point[0]][current_point[1]]
        travelled_distance = pointer[0] + board.board[current_point[0]][current_point[1]]
        if astar:
            # In the A* algorithm the heuristic is incorporated in the first value of the agenda
            travelled_distance -= calculateHeuristic(current_point, board.destination)
        if str(shortest_distance_to_current).isdigit() and travelled_distance >= shortest_distance_to_current:
            # If this point has been visited yet and the current travelled distance is more than the previous
            # shortest distance to this point then we will not continue with this pathway
            continue
        # Else we will update the shortest distance to this point to the current travelled distance
        board.visited[current_point[0]][current_point[1]] = travelled_distance
        # If the tracepath is selected on the GUI then we will update the pathway each iteration
        if tracepath:
            time.sleep(sleeptime)
            # Delete the part of the previous pathway which isn't present in the current pathway
            unshowCalculation([coord for coord in previous_pathway if coord not in pathway])
            # Show the part of the current pathway which isn't active yet
            showCalculation([coord for coord in pathway if coord not in previous_pathway])
        if current_point == board.destination: # If we have reached the destination
            if not tracepath:   # Show the pathway if tracepath was disabled, otherwise it is already shown
                showCalculation(pathway)
            messagebox.config(state='normal')   # Allow us to make a change in the messagebox
            messagebox.insert('end', f'Algorithm: {alg}\nTotal Distance: {travelled_distance}\n'
                                        f'Elapsed time: {datetime.datetime.now() - start}\n')  # update messagebox
            messagebox.config(state='disabled') # Close access to messagebox again (prevents user input/disrupt)
            return
        # If we are not at the destination yet then we will add all possible and viable neighbors to the agenda
        # Viable neighbors are those which are on the board, which are not obstacles, which are not in the pathway
        # yet (prevents cycles) and which have not been visited yet or have only been visited by a longer path
        for point in filter(lambda point: not str(board.board[point[0]][point[1]]).isalpha()
                                and point not in pathway
                                and (not board.visited[point[0]][point[1]]
                                     or travelled_distance > board.visited[point[0]][point[1]])
                            , findNeighbors(current_point, board.size)):
            if astar:
                agenda.put((calculateHeuristic(point, board.destination) + travelled_distance, pathway + [point]))
            else:
                agenda.put((travelled_distance, pathway + [point]))
        previous_pathway = pathway
    # This will only execute when no pathway has been found
    unshowCalculation(previous_pathway[1:]) # Decolor the last pathway of the calculation
    messagebox.config(state='normal')  # Allow us to make a change in the messagebox
    messagebox.insert('end', f'Algorithm: {alg} \nNo pathway found!\n')
    messagebox.config(state='disabled')  # Close access to messagebox again (prevents user input/disrupt)
    return


'''This function is used to calculate the pathway for the Depth First Search (DFS) and Breadth First Search (BFS).'''
def depthOrBreadthFirstSearch(sleeptime=0, breadth=True, tracepath=False):
    start = datetime.datetime.now()
    resetColors()
    board.resetVisitorFlags()
    previous_pathway = []
    if breadth: # BFS will use a queue as agenda (FIFO)
        agenda = queue.Queue()
        alg = "Breadth First Search"
    else: # DFS will use a stack as agenda (LIFO), not that this could be implemented
        # with a simple list as well, yet the usage of queue.LifoQueue() allows me to combine both DFS and BFS in one
        # function due to the identical 'put' and 'get' commands as opposed to 'append' and 'pop' if a list were used.
        agenda = queue.LifoQueue()
        alg = "Depth First Search"
    agenda.put([board.start])
    while agenda.qsize() > 0:
        pathway = agenda.get() # One item in the agenda consists of a pathway (list of coordinates), nothing else.
        current_point = pathway[-1] # The current point is the last point in the pathway
        if board.visited[current_point[0]][current_point[1]]:
            continue  # If we already visited this point then we will not add it again
        if tracepath:   # If the tracepath is selected on the GUI then we will update the pathway each iteration
            time.sleep(sleeptime)
            # Delete the part of the previous pathway which isn't present in the current pathway
            unshowCalculation([coord for coord in previous_pathway if coord not in pathway])
            # Show the part of the current pathway which isn't active yet
            showCalculation([coord for coord in pathway if coord not in previous_pathway])
        board.visited[current_point[0]][current_point[1]] = True  # Set the visited flag for this node to True
        if current_point == board.destination:  # If we have reached the destination
            if not tracepath: # Show the pathway if tracepath was disabled, otherwise it is already shown
                showCalculation(pathway)
            # Calculate the distance by adding all values of the point in the pathway
            travelled_distance = functools.reduce(lambda x, y: x + y,
                            map(lambda x: board.board[x[0]][x[1]], pathway[1:]))
            messagebox.config(state='normal')   # Allow us to make a change in the messagebox
            messagebox.insert('end', f'Algorithm: {alg}\nTotal Distance: {travelled_distance}\n'
                                        f'Elapsed time: {datetime.datetime.now() - start}\n') # update messagebox
            messagebox.config(state='disabled') # Close access to messagebox again (prevents user input/disrupt)
            return
        # If we are not at the destination yet then we will add all possible and viable neighbors to the agenda
        # Viable neighbours are those which are on the board and have not been visited yet
        for point in filter(lambda point: not str(board.board[point[0]][point[1]]).isalpha()
                            and not board.visited[point[0]][point[1]], findNeighbors(current_point, board.size)):
            agenda.put(pathway + [point])
        previous_pathway = pathway
    # This will only execute when no pathway has been found
    unshowCalculation(previous_pathway[1:])  # Decolor the last pathway of the calculation
    messagebox.config(state='normal')  # Allow us to make a change in the messagebox
    messagebox.insert('end', f'Algorithm: {alg} \nNo pathway found!\n')
    messagebox.config(state='disabled')  # Close access to messagebox again (prevents user input/disrupt)
    return


'''Calculates the heuristic (Manhattan distance) from a certain point to the destination.'''
def calculateHeuristic(point1, point2):
    return abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])


'''This function will return a list of all neighbours of a certain point which are on the board.
In practise this will check whether the point lies on the edge of the board or not, it does not check for obstacles!'''
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


'''This will delete the current messages on display.'''
def clearMessages():
    messagebox.config(state='normal')   # First we must make the box active again
    messagebox.delete(1.0, 'end')   # Delete everything in the box
    messagebox.config(state='disabled') # Disable the box again (prevents suers from misusing/disorganizing it)


"""This is where the lay-out starts to be defined."""
if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")                            # This maximises the window

    mainframe = tk.Frame(root)
    mainframe.pack(fill='both', expand=True)

    topframe = tk.Frame(mainframe)
    topframe.pack(side='top')

    settingsframe = tk.Frame(topframe)
    settingsframe.pack(side='left')

    messageframe = tk.Frame(topframe)
    messageframe.pack(side='left')

    algorithmframe = tk.Frame(topframe)
    algorithmframe.pack(side='right')

    bottomframe = tk.Frame(mainframe)
    bottomframe.pack(side='bottom', expand=True, fill='both')

    matrixcanvas = tk.Canvas(bottomframe)
    matrixframe = tk.Frame(matrixcanvas)
    yscrollbar = tk.Scrollbar(bottomframe, orient="vertical", command=matrixcanvas.yview)   # Vertical scrollbar
    yscrollbar.pack(fill='y', side='right')  # Stretch scrollbar vertically and put it on the right side
    matrixcanvas.pack(fill='both', expand=True)


    matrixsizeslider = tk.Scale(settingsframe, from_=10, to=50, orient='horizontal', length=200, label='Matrix size')
    matrixsizeslider.pack(anchor='n')       # Matrix size slider

    actionvar = tk.StringVar()
    actionbuttons = [("Increment by 1", "increment it by 1"), ("Decrease by 1", 'lower it by 1'),
                     ("Make cell into an obstacle", 'turn it into an obstacle'),
                     ("Turn obstacle into the value 1", 'turn the obstacle into a 1'),
                     ("Choose start", "set the start location there"),
                     ("Choose destination", "set the destination there")]
    for text, value in actionbuttons:
        actionbutton = tk.Radiobutton(settingsframe, text=text, indicatoron=0, width=25, variable=actionvar,
                                      value=value, command=actionsel)
        actionbutton.pack()             # Matrix interactive adaptation buttons

    sellabel = tk.Label(settingsframe)  # Label for the Matrix interactive adaptation buttons
    sellabel.pack()

    sleepscale = tk.Scale(algorithmframe, from_=0, to=1, orient='horizontal', length=200,
                          label='Time between steps (s)',
                          resolution=0.05)
    sleepscale.pack(anchor='n')         # Slider for adjusting the sleeptime

    tracevar = tk.BooleanVar()          # Parameter which indicates the state of tracepath
    traceTrue = tk.Radiobutton(algorithmframe, text="Trace calculations", width=25, variable=tracevar,
                               value=True).pack()   # Enable tracepath
    traceFalse = tk.Radiobutton(algorithmframe, text="Do not trace calculations", width=25, variable=tracevar,
                                value=False).pack() # Disbale tracepath

    algvar = tk.StringVar()             # Parameter which indicates the selected algorithm
    algorithmbuttons = ["Algorithm A*", "Breadth First Search", "Depth First Search", "Uniform Cost Search"]

    for algorithm in algorithmbuttons:
        algorithmbutton = tk.Radiobutton(algorithmframe, text=algorithm, indicatoron=0, width=25, variable=algvar,
                                         value=algorithm, command=algsel)
        algorithmbutton.pack()          # Buttons for selecting the desired algorithm

    alglabel = tk.Label(algorithmframe)
    alglabel.pack()                     #  Label for the selected algorithm

    generatematrixbutton = tk.Button(settingsframe, text='Generate Matrix',
                                     command=lambda: createBoard(size=int(matrixsizeslider.get())))
    generatematrixbutton.pack(anchor='s')   # Button for generating a matrix

    calculatepathwaybutton = tk.Button(algorithmframe, text='Calculate Pathway',
                                       command=lambda: calculatePathway())
    calculatepathwaybutton.pack(anchor='s') # Button for calculating the pathway

    messagebox = tk.Text(messageframe, height=10, width=50, state='disabled')
    messagebox.pack()                       # The message window, used for showing the user results.
                                            # User input has been disabled

    clearmessages = tk.Button(messageframe, text='Clear Messages', command=lambda: clearMessages())
    clearmessages.pack()                    # Button for clearing everything is the messagebox

    root.mainloop()
