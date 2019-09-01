# this module is used to create the game user interface
import pygame
# this module is used to make HTTP requests to your machine learning model
import requests
# this module is used to choose a random colour for the user interface and
#  make random choices about moves the computer should make
import random



# API KEY  - the unique private code for your Machine Learning project
global KEY
KEY = "put-your-project-API-key-here"




############################################################################
# Constants that match names you have used in your Machine Learning project
############################################################################
# You shouldn't need to change these, but if you spelled values differently
# in your project, then you can update these to match here.

# descriptions of the contents of a space on the game board
EMPTY = "EMPTY"
OPPONENT = "OPPONENT"   # for the human, the OPPONENT is the computer
                        # for the computer, the OPPONENT is the human
PLAYER = "PLAYER"       # for the human, the PLAYER is the human
                        # for the computer, the PLAYER is the computer

# descriptions of the locations on the game board
top_left = "top_left"
top_middle = "top_middle"
top_right = "top_right"
middle_left = "middle_left"
middle_middle = "middle_middle"
middle_right = "middle_right"
bottom_left = "bottom_left"
bottom_middle = "bottom_middle"
bottom_right = "bottom_right"

#
############################################################################




############################################################################
# Converting between labels and numeric values
############################################################################

# training examples refer to a location on the game board
deconvert = {}
deconvert[top_left] = 0
deconvert[top_middle] = 1
deconvert[top_right] = 2
deconvert[middle_left] = 3
deconvert[middle_middle] = 4
deconvert[middle_right] = 5
deconvert[bottom_left] = 6
deconvert[bottom_middle] = 7
deconvert[bottom_right] = 8




############################################################################
# Machine Learning functions
############################################################################

# who the two players are
HUMAN = "HUMAN"
COMPUTER = "COMPUTER"

# Storing a record of what has happened so the computer can learn from it!
#   contents of the board at each stage in the game
gamehistory = {
    HUMAN : [],
    COMPUTER : []
}
#   decisions made by each player
decisions = {
    HUMAN : [],
    COMPUTER : []
}



# Use your machine learning model to decide where the
#   computer should move next.
#
#  board :  list of board spaces with the current state of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
def classify(board):
    debug("Predicting the next best move for the computer")

    # where should the request be sent?
    url = "https://machinelearningforkids.co.uk/api/scratch/"+ KEY + "/classify"

    # send the state of the game board to your machine learning model
    response = requests.get(url, params={
        "data" : get_board_from_perspective(board, COMPUTER)
    })

    if response.ok:
        responseData = response.json()

        # responseData will contain the list of predictions made by the
        #  machine learning model, starting from the one with the most
        #  confidence, to the one with the least confidence
        for prediction in responseData:
            # we can't make a move unless the space is empty, so
            #  check that first
            if is_space_empty(board, prediction["class_name"]):
                return prediction

        # If we're here, it means that none of the predictions made by
        #  the machine learning model were actually empty!
        # (This should never happen, but to be safe...)

        # Pick a random space to move in
        for space in random.sample(deconvert.keys(), len(deconvert)):
            # we can't make a move unless the space is empty, so
            #  check that first
            if is_space_empty(board, space):
                return { "class_name" : space }
    else:
        # something went wrong - there was an error when trying to
        #  use your ML model
        print(response.json())
        response.raise_for_status()



# Add a move that resulted in a win to the training data for the
# machine learning model
#
#  board         :  list of board spaces with the current state of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
#  who           :  whose training data this is
#      e.g.    HUMAN
#  name_of_space :  name of the space that the move was in
#      e.g.    bottom_left
def add_to_train(board, who, name_of_space):
    print ("Adding the move in %s by %s to the training data" % (name_of_space, who))

    url = "https://machinelearningforkids.co.uk/api/scratch/"+ KEY + "/train"

    response = requests.post(url, json={
        # convert the contents of the board into a list of whose symbol
        #   is in that space, from the perspective of 'who'
        #  e.g. [ PLAYER, OPPONENT, PLAYER, EMPTY, EMPTY, PLAYER, OPPONENT, PLAYER, OPPONENT ]
        "data" : get_board_from_perspective(board, who),
        # the location that they chose to make a move in
        "label" : name_of_space
    })

    if response.ok:
        # training data stored okay
        pass
    else:
        # something went wrong
        print(response.json())
        response.raise_for_status()



# Train a new machine learning model using the training data
# that has been collected so far
def train_new_model():
    print ("Training a new machine learning model")

    url = "https://machinelearningforkids.co.uk/api/scratch/"+ KEY + "/models"
    response = requests.post(url)

    if response.ok:
        # machine learning model trained successfully
        pass
    else:
        # something went wrong
        print(response.json())
        response.raise_for_status()



# Someone won the game.
#  A machine learning model could learn from this...
#
#  winner          : who won - either HUMAN or COMPUTER
#  boardhistory    : the contents of the game board at each stage in the game
#  winnerdecisions : each of the decisions that the winner made
def learn_from_this(winner, boardhistory, winnerdecisions):
    print("%s won the game!" % (winner))
    print("Maybe the computer could learn from %s's experience?" % (winner))
    for idx in range(len(winnerdecisions)):
        print("\nAt the start of move %d the board looked like this:" % (idx + 1))
        print(boardhistory[idx])
        print("And %s decided to put their mark in %s" % (winner, winnerdecisions[idx]))




############################################################################
# Noughts and Crosses logic
############################################################################

# checks to see if a specific space on the board is currently empty
#
#  board         :  list of board spaces with the contents of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
#  name_of_space :  name of the space to check
#            e.g.    middle_right
def is_space_empty(board, name_of_space):
    index_of_space = deconvert[name_of_space]
    return board[index_of_space] == EMPTY



# Creates the initial state for the game
def create_empty_board():
    debug("Creating the initial empty game board state")
    return [ EMPTY, EMPTY, EMPTY,
             EMPTY, EMPTY, EMPTY,
             EMPTY, EMPTY, EMPTY ]



# Gets the contents of the board, from the perspective of either
#  the human or the computer.
#
#  board :  list of board spaces with the current state of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
#  who   :  either HUMAN or COMPUTER
#
# Returns the board described as PLAYER or OPPONENT
#      e.g.  [ PLAYER, OPPONENT, PLAYER, EMPTY, EMPTY, PLAYER, OPPONENT, PLAYER, OPPONENT ]
def get_board_from_perspective(board, who):
    convertedboard = []
    for move in board:
        if move == EMPTY:
            # an empty space is an empty space, from anyone's perspective
            convertedboard.append(EMPTY)
        else:
            convertedboard.append(PLAYER if move == who else OPPONENT)
    return convertedboard



############################################################################
# Noughts and Crosses user interface functions
############################################################################

# RGB colour codes
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


game_board_coordinates = {
    "top_left": {
        "bottom_left_corner": (120, 120),
        "top_right_corner": (180, 180),
        "top_left_corner": (180, 120),
        "bottom_right_corner": (120, 180),
        "centre": (150, 150)
    },
    "top_middle" : {
        "bottom_left_corner": (220, 120),
        "top_right_corner": (280, 180),
        "top_left_corner": (220, 180),
        "bottom_right_corner": (280, 120),
        "centre": (250, 150)
    },
    "top_right" : {
        "bottom_left_corner": (320, 120),
        "top_right_corner": (380, 180),
        "top_left_corner": (320, 180),
        "bottom_right_corner": (380, 120),
        "centre": (350, 150)
    },
    "middle_left" : {
        "bottom_left_corner": (120, 220),
        "top_right_corner": (180, 280),
        "top_left_corner": (120, 280),
        "bottom_right_corner": (180, 220),
        "centre": (150, 250)
    },
    "middle_middle" : {
        "bottom_left_corner": (220, 220),
        "top_right_corner": (280, 280),
        "top_left_corner": (220, 280),
        "bottom_right_corner": (280, 220),
        "centre": (250, 250)
    },
    "middle_right" : {
        "bottom_left_corner": (320, 220),
        "top_right_corner": (380, 280),
        "top_left_corner": (320, 280),
        "bottom_right_corner": (380, 220),
        "centre": (350, 250)
    },
    "bottom_left" : {
        "bottom_left_corner": (120, 320),
        "top_right_corner": (180, 380),
        "top_left_corner": (120, 380),
        "bottom_right_corner": (180, 320),
        "centre": (150, 350)
    },
    "bottom_middle" : {
        "bottom_left_corner": (220, 320),
        "top_right_corner": (280, 380),
        "top_left_corner": (220, 380),
        "bottom_right_corner": (280, 320),
        "centre": (250, 350)
    },
    "bottom_right" : {
        "bottom_left_corner": (320, 320),
        "top_right_corner": (380, 380),
        "top_left_corner": (320, 380),
        "bottom_right_corner": (380, 320),
        "centre": (350, 350)
    }
}


# Check if someone has won and draws a line to show the winner
#   if someone has won
#
#  who  : Who made the last move? (only need to check if they won
#          as a player who hasn't just made a move can't have won)
#         e.g.   HUMAN or COMPUTER
#
#  Returns true if someone won
#  Returns false if noone won
def display_winner(screen, board, who):
    debug("Checking if %s has won" % (who))

    gameover = False

    # we use a green line if the human wins, a red line if the computer does
    linecolour = GREEN if who == HUMAN else RED

    ######## Rows ########
    if board[deconvert["top_left"]] == who and board[deconvert["top_middle"]] == who and board[deconvert["top_right"]] == who:
        pygame.draw.line(screen, linecolour, (100, 150), (400, 150), 10)
        gameover = True
    if board[deconvert["middle_left"]] == who and board[deconvert["middle_middle"]] == who and board[deconvert["middle_right"]] == who:
        pygame.draw.line(screen, linecolour, (100, 250), (400, 250), 10)
        gameover = True
    if board[deconvert["bottom_left"]] == who and board[deconvert["bottom_middle"]] == who and board[deconvert["bottom_right"]] == who:
        pygame.draw.line(screen, linecolour, (100, 350), (400, 350), 10)
        gameover = True

    ######## Columns ########
    if board[deconvert["top_left"]] == who and board[deconvert["middle_left"]] == who and board[deconvert["bottom_left"]] == who:
        pygame.draw.line(screen, linecolour, (150, 100), (150, 400), 10)
        gameover = True
    if board[deconvert["top_middle"]] == who and board[deconvert["middle_middle"]] == who and board[deconvert["bottom_middle"]] == who:
        pygame.draw.line(screen, linecolour, (250, 100), (250, 400), 10)
        gameover = True
    if board[deconvert["top_right"]] == who and board[deconvert["middle_right"]] == who and board[deconvert["bottom_right"]] == who:
        pygame.draw.line(screen, linecolour, (350, 100), (350, 400), 10)
        gameover = True

    ######## Diagonals #########
    if board[deconvert["top_left"]] == who and board[deconvert["middle_middle"]] == who and board[deconvert["bottom_right"]] == who:
        pygame.draw.line(screen, linecolour, (100, 100), (400, 400), 15)
        gameover = True
    if board[deconvert["bottom_left"]] == who and board[deconvert["middle_middle"]] == who and board[deconvert["top_right"]] == who:
        pygame.draw.line(screen, linecolour, (400, 100), (100, 400), 15)
        gameover = True

    if gameover:
        # refresh the display if we've drawn any game-over lines
        pygame.display.update()

    return gameover



# Redraw the UI with a different background colour
#
#  board :  list of board spaces with the contents of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
def redraw_screen(screen, colour, board):
    debug("Changing the background colour")

    # fill everything in the new background colour
    screen.fill(colour)

    # now we've covered everything, we need to redraw
    #  the game board again
    draw_game_board(screen)

    # now we need to redraw all of the moves that
    #  have been made
    for spacename in deconvert.keys():
        space_code = deconvert[spacename]

        if board[space_code] == HUMAN:
            draw_move(screen, spacename, "cross")
        elif board[space_code] == COMPUTER:
            draw_move(screen, spacename, "nought")

    # refresh now we've made changes
    pygame.display.update()



# Draw the crossed lines that make up a noughts and crosses board
def draw_game_board(screen):
    pygame.draw.rect(screen, WHITE, (195, 100, 10, 300))
    pygame.draw.rect(screen, WHITE, (295, 100, 10, 300))
    pygame.draw.rect(screen, WHITE, (100, 195, 300, 10))
    pygame.draw.rect(screen, WHITE, (100, 295, 300, 10))



# Setup the window that will be used to display the game
def prepare_game_window():
    debug("Setting up the game user interface")
    # sets up the pygame library we'll use to create the game
    pygame.init()
    # create a window that is 500 pixels wide and 500 pixels high
    screen = pygame.display.set_mode((500, 500))
    # set the title of the window
    pygame.display.set_caption("Machine Learning Noughts and Crosses")
    return screen



# Create a random RGB code to be used for the background colour
def generate_random_colour():
    debug("Generating a random colour code")
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return [r, g, b]



# Draw a new move on the game board
#
#  screen        :  The PyGame screen to draw the move on
#  name_of_space :  Name of the space to draw the move on
#                    e.g.    middle_right
#  move          :  The move to draw.
#                   It will be either "nought" or "cross"
def draw_move(screen, name_of_space, move):
    debug("Drawing a move on the game board : %s in %s" % (move, name_of_space))

    if move == "nought":
        location = game_board_coordinates[name_of_space]["centre"]
        pygame.draw.circle(screen, WHITE, location, 35 , 8)
    elif move == "cross":
        pygame.draw.line(screen, WHITE,
                         game_board_coordinates[name_of_space]["bottom_left_corner"],
                         game_board_coordinates[name_of_space]["top_right_corner"],
                         10)
        pygame.draw.line(screen, WHITE,
                         game_board_coordinates[name_of_space]["top_left_corner"],
                         game_board_coordinates[name_of_space]["bottom_right_corner"],
                         10)
    pygame.display.update()



# The user has clicked on the game board.
# Which space did they click on?
#
#  mx : the x coordinate of their click
#  my : the y coordiante of their click
#
#  Returns the name of the space they clicked on (e.g. "middle_right")
def get_click_location(mx, my):
    debug("Getting location of click in %d,%d" % (mx, my))
    if 100 < mx < 400 and 100 < my < 400:
        if my < 200:
            if mx < 200:
                return "top_left"
            elif mx < 300:
                return "top_middle"
            else:
                return "top_right"
        elif my < 300:
            if mx < 200:
                return "middle_left"
            elif mx < 300:
                return "middle_middle"
            else:
                return "middle_right"
        else:
            if mx < 200:
                return "bottom_left"
            elif mx < 300:
                return "bottom_middle"
            else:
                return "bottom_right"
    return "none"



# Handle a new move, by either the player or the computer
#
#  board         :  list of board spaces with the contents of each space
#      e.g.  [ HUMAN, COMPUTER, HUMAN, EMPTY, EMPTY, HUMAN, COMPUTER, HUMAN, COMPUTER ]
#  name_of_space :  name of the space the move was in
#            e.g.    middle_right
#  identity      :  whose move this is
#            e.g.    HUMAN or COMPUTER
#
#  returns true if this move ended the game
#  returns false if the game should keep going
def game_move(screen, board, name_of_space, identity):
    debug("Processing a move for %s who chose %s" % (identity, name_of_space))

    # choose the symbol for which player this is
    symbol = "cross" if identity == HUMAN else "nought"

    # draw a symbol on the board to represent the move
    draw_move(screen, name_of_space, symbol)

    # update the history of what has happened in case
    #  we want to learn from it later
    gamehistory[identity].append(board.copy())
    decisions[identity].append(name_of_space)

    # update the board to include the move
    movelocation = deconvert[name_of_space]
    board[movelocation] = identity

    # have they won the game?
    gameover = display_winner(screen, board, identity)
    if gameover:
        # someone won! maybe an ML project could learn from this
        learn_from_this(identity, gamehistory[identity], decisions[identity])

    # the game is also over if the board is full (a draw!)
    #
    # and the board is full if both players together
    #  have made 9 moves in total
    if len(decisions[HUMAN]) + len(decisions[COMPUTER]) >= 9:
        gameover = True

    return gameover



# the machine learning model's turn
def let_computer_play(screen, board):
    computer_move = classify(board)
    print(computer_move)
    return game_move(screen, board, computer_move["class_name"], COMPUTER)




############################################################################
# Main game logic starts here
############################################################################

def debug(msg):
    # if something isn't working, uncomment the line below
    #  so you get detailed print-outs of everything that
    #  the program is doing
    # print(msg)
    pass



debug("Configuration")
debug("Using identities %s %s %s" % (EMPTY, PLAYER, OPPONENT))
debug(deconvert)

debug("Initial startup and setup")
screen = prepare_game_window()
board = create_empty_board()
redraw_screen(screen, generate_random_colour(), board)

debug("Initialising game state variables")
running = True
gameover = False

debug("Deciding who will play first")
computer_goes_first = random.choice([False, True])
if computer_goes_first:
    let_computer_play(screen, board)


while running:
    # wait for the user to do something...
    event = pygame.event.wait()

    if event.type == pygame.QUIT:
        running = False

    if event.type == pygame.MOUSEBUTTONDOWN and gameover == False:
        # what has the user clicked on?
        mx, my = pygame.mouse.get_pos()
        location_name = get_click_location(mx, my)

        if location_name == "none":
            # user clicked on none of the spaces so we'll
            #  change the colour for them instead!
            redraw_screen(screen, generate_random_colour(), board)

        elif is_space_empty(board, location_name):
            # the user clicked on an empty space
            gameover = game_move(screen, board, location_name, HUMAN)

            # if we're still going, it is the computer's turn next
            if gameover == False:
                # the computer chooses where to play
                gameover = let_computer_play(screen, board)

        # ignore anything else the user clicked on while we
        #  were processing their click, so they don't try to
        #  sneakily have lots of moves at once
        pygame.event.clear()
