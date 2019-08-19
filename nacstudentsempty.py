import pygame, random, time, sys, requests

convert = {1:"EMPTY", 2:"OPPONENT", 3:"PLAYER"}
deconvert = {"top_left":0, "top_middle":1, "top_right":2, "middle_left":3, "middle_middle":4, "middle_right":5, "bottom_left":6, "bottom_middle":7, "bottom_right":8, 0:"top_left", 1:"top_middle", 2:"top_right", 3:"middle_left", 4:"middle_middle", 5:"middle_right", 6:"bottom_left", 7:"bottom_middle", 8:"bottom_right"}

global key
key = ""

def classify(board):
    url = "https://machinelearningforkids.co.uk/api/scratch/"+ key + "/classify"
    convertedboard = []
    for i in range(9):
        convertedboard.append(convert[board[i]])
    response = requests.get(url, params={ "data" : convertedboard })
    if response.ok:
        responseData = response.json()
        topMatch = responseData[0]
        count = 0
        while board[deconvert[topMatch["class_name"]]] != 1:
            count += 1
            topMatch = responseData[count]
            if count == 8:
                break
        if topMatch["confidence"] == 0:
            rv = random.randint(0, 8)
            while board[rv] != 1:
                rv = random.randint(0, 8)
            topMatch["class_name"] = deconvert[rv]
        return topMatch
    else:
        response.raise_for_status()

def add_to_train(board, label):
    numbers = []
    data = []
    for i in range(9):
        numbers.append(convert[board[i]])
        data.append("data" + str(i+1))
    url = "https://machinelearningforkids.co.uk/api/scratch/"+ key + "/train" 

    response = requests.post(url, json={ "data" : numbers, "label" : label })

    if response.ok:
        return
    else:
        response.raise_for_status()

def train_new_model():
    url = "https://machinelearningforkids.co.uk/api/scratch/"+ key + "/models" 
    response = requests.post(url)

    if response.ok:
        return
    else:
        response.raise_for_status()
    
def winner(board, savedmoves, movelocation, movelocations):
    whohaswon = 0
    a = ()
    for i in range(2, 4):
        if i == 2:
            a = (255, 0, 0)
        else:
            a = (0, 255, 0)
            
        ######## Rows ########
        if board[deconvert["top_left"]] == i and board[deconvert["top_middle"]] == i and board[deconvert["top_right"]] == i:
            pygame.draw.line(screen, a, (100, 150), (400, 150), 10)
            whohaswon = i-1
        if board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i:
            pygame.draw.line(screen, a, (100, 250), (400, 250), 10)
            whohaswon = i-1
        if board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i:
            pygame.draw.line(screen, a, (100, 350), (400, 350), 10)
            whohaswon = i-1
            
        ######## Columns ########
        if board[deconvert["top_left"]] == i and board[deconvert["middle_left"]] == i and board[deconvert["bottom_left"]] == i:
            pygame.draw.line(screen, a, (150, 100), (150, 400), 10)
            whohaswon = i-1
        if board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] ==i:
            pygame.draw.line(screen, a, (250, 100), (250, 400), 10)
            whohaswon = i-1
        if board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i:
            pygame.draw.line(screen, a, (350, 100), (350, 400), 10)
            whohaswon = i-1
        
        ######## Diagonals #########
        if board[deconvert["top_left"]] == i and board[deconvert["middle_middle"]] == i and board[deconvert["bottom_right"]] == i:
              pygame.draw.line(screen, a, (100, 100), (400, 400), 15)
              whohaswon = i-1
        if board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i and board[deconvert["edit_here"]] == i:
              pygame.draw.line(screen, a, (400, 100), (100, 400), 15)
              whohaswon = i-1

    pygame.display.update()
    savedmoves.append(board)
    movelocations.append(movelocation)
    if whohaswon != 0:
        if firstmove == True:
            if whohaswon == 1:
                for i in range(0, len(savedmoves), 2):
                    add_to_train(savedmoves[i], deconvert[movelocations[i]])
            if whohaswon == 2:
                for i in range(1, len(savedmoves), 2):
                    add_to_train(savedmoves[i], deconvert[movelocations[i]])
        else:
            if whohaswon == 1:
                for i in range(1, len(savedmoves), 2):
                    add_to_train(savedmoves[i], deconvert[movelocations[i]])
            if whohaswon == 2:
                for i in range(0, len(savedmoves), 2):
                    add_to_train(savedmoves[i], deconvert[movelocations[i]])
    return whohaswon

def colourchange(colour, board):
    screen.fill(colour)
    pygame.draw.rect(screen, (255, 255, 255), (195, 100, 10, 300)); pygame.draw.rect(screen, (255, 255, 255), (295, 100, 10, 300)); pygame.draw.rect(screen, (255, 255, 255), (100, 195, 300, 10)); pygame.draw.rect(screen, (255, 255, 255), (100, 295, 300, 10))
    for i in range(9):
        if board[i] == 2:
            pygame.draw.circle(screen, (255, 255, 255), posscompmoves[i], 35 , 8)
        if board[i] == 3:
            a = (i % 3) * 100
            if i < 3:
                pygame.draw.line(screen, (255, 255, 255), (a+120, 120), (a+180, 180), 10); pygame.draw.line(screen, (255, 255, 255), (a+120, 180), (a+180, 120), 10)
            elif i < 6:
                pygame.draw.line(screen, (255, 255, 255), (a+120, 220), (a+180, 280), 10); pygame.draw.line(screen, (255, 255, 255), (a+120, 280), (a+180, 220), 10)
            else:
                pygame.draw.line(screen, (255, 255, 255), (a+120, 320), (a+180, 380), 10); pygame.draw.line(screen, (255, 255, 255), (a+120, 380), (a+180, 320), 10)
                
pygame.init()
screen = pygame.display.set_mode((500, 500))
caption = pygame.display.set_caption("Noughts and Crosses")
run = True
posscompmoves = [(150,150), (250,150), (350,150), (150,250), (250,250), (350,250), (150,350), (250,350), (350,350)]
board = [1,1,1,1,1,1,1,1,1]
savedmoves = []
movelocations = []
movecount = 0
pygame.draw.rect(screen, (255, 255, 255), (195, 100, 10, 300)); pygame.draw.rect(screen, (255, 255, 255), (295, 100, 10, 300)); pygame.draw.rect(screen, (255, 255, 255), (100, 195, 300, 10)); pygame.draw.rect(screen, (255, 255, 255), (100, 295, 300, 10))
r = random.randint(0, 255); g = random.randint(0,255); b = random.randint(0, 255); colour = [r, g, b]
colourchange(colour, board)
pygame.display.update()
hasusermoved = random.choice([False, True])
firstmove = hasusermoved
win = 0
movelocation = 0
while run:
    time.sleep(0.05)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if 100 < mx < 400 and 100 < my < 400:
                if my < 200:
                    if mx < 200 and board[0] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (120, 120), (180, 180), 10); pygame.draw.line(screen, (255, 255, 255), (120, 180), (180, 120), 10)
                        board[0] = 3
                        hasusermoved = True
                        movelocation = 0
                    elif mx < 300 and board[1] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (220, 120), (280, 180), 10); pygame.draw.line(screen, (255, 255, 255), (220, 180), (280, 120), 10)
                        board[1] = 3
                        movelocation = 1
                        hasusermoved = True
                    elif board[2] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (320, 120), (380, 180), 10); pygame.draw.line(screen, (255, 255, 255), (320, 180), (380, 120), 10)
                        board[2] = 3
                        hasusermoved = True
                        movelocation = 2
                elif my < 300:
                    if mx < 200 and board[3] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (120, 220), (180, 280), 10); pygame.draw.line(screen, (255, 255, 255), (120, 280), (180, 220), 10)
                        board[3] = 3
                        hasusermoved = True
                        movelocation = 3
                    elif mx < 300 and board[4] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (220, 220), (280, 280), 10); pygame.draw.line(screen, (255, 255, 255), (220, 280), (280, 220), 10)
                        board[4] = 3
                        hasusermoved = True
                        movelocation = 4
                    elif board[5] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (320, 220), (380, 280), 10); pygame.draw.line(screen, (255, 255, 255), (320, 280), (380, 220), 10)
                        board[5] = 3
                        hasusermoved = True
                        movelocation = 5
                else:
                    if mx < 200 and board[6] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (120, 320), (180, 380), 10); pygame.draw.line(screen, (255, 255, 255), (120, 380), (180, 320), 10)
                        board[6] = 3
                        hasusermoved = True
                        movelocation = 6
                    elif mx < 300 and board[7] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (220, 320), (280, 380), 10); pygame.draw.line(screen, (255, 255, 255), (220, 380), (280, 320), 10)
                        board[7] = 3
                        hasusermoved = True
                        movelocation = 7
                    elif board[8] == 1:
                        pygame.draw.line(screen, (255, 255, 255), (320, 320), (380, 380), 10); pygame.draw.line(screen, (255, 255, 255), (320, 380), (380, 320), 10)
                        board[8] = 3
                        hasusermoved = True
                        movelocation = 8
            else:
                r = random.randint(0, 255); g = random.randint(0, 255); b = random.randint(0, 255)
                colour = [r, g, b]
                colourchange(colour, board)
        pygame.display.update()
   
        if win == 0:
            if hasusermoved == True:
                movecount += 1
                win = winner(board, savedmoves, movelocation, movelocations)
                if win == 0:
                    compmove = deconvert[classify(board)["class_name"]]
                    movelocation = compmove
                    board[compmove] = 2
                    pygame.draw.circle(screen, (255, 255, 255), posscompmoves[compmove], 35 , 8)
                    hasusermoved = False
                    movecount += 1
                    win = winner(board, savedmoves, movelocation, movelocations)
        pygame.display.flip()
        if random.randint(1, 500) == 123:
            train_new_model()
        
pygame.quit()
sys.exit(0)
exit()
