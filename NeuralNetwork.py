import ChessMain, ChessEngine, Preprocessor 
import numpy as np
from matplotlib import pyplot as plt

DEBUG = True
COLUMNS = {'a': 7, 'b': 6, 'c': 5, 'd': 4, 'e': 3, 'f': 2, 'g': 1, 'h': 0}
PROMOTIONS = {'Q': 5, 'R': 4, 'B': 3, 'N': 2}

def testEngine():
    pgn_file = "./games/ficsgamesdb_202101_standard2000_nomovetimes_196479.pgn"
    all_games = Preprocessor.getGames(pgn_file=pgn_file)
    j = 0
    scores = []
    for game in all_games:
        found_moves = 0
        j += 1
        print("")
        print("Game No. " + str(j))
        gs = ChessEngine.GameState()
        game_moves = game.Moves
        total_moves = len(game_moves)
        for move in game_moves:
            if gs.whiteToMove:
                print('White Move: ' + str(move), end=" ")
            else:
                print('Black Move: ' + str(move), end=" ")
            if '+' in move:
                move = move.strip('+') 
                print(" -(+)", end=" ")
            elif '#' in move:
                move = move.strip('#')
                print(" -(#)", end=" ")
            possible_moves = gs.getValidMoves()
            selected_move = None
            for i in range(len(possible_moves)):
                if move == possible_moves[i].moveString:
                    selected_move = possible_moves[i]
                    print("[x]")
                    found_moves += 1
                    break
            if selected_move == None and move != '':
                if move[0] in ['N', 'B', 'R']:
                    new_move = move[0] + move[2:]
                    if move[1].isnumeric():
                        row = int(move[1]) - 1
                        for i in range(len(possible_moves)):
                            if new_move == possible_moves[i].moveString and possible_moves[i].startRow == row:
                                selected_move = possible_moves[i]
                                print("[x]")
                                found_moves += 1
                                break
                    elif move[1] in ['a', 'b', 'c', 'd', 'e', 'g', 'f', 'h']:
                        col = COLUMNS[move[1]]
                        for i in range(len(possible_moves)):
                            if new_move == possible_moves[i].moveString and possible_moves[i].startCol == col:
                                selected_move = possible_moves[i]
                                print("[x]")
                                found_moves += 1
                                break
            if '=' in move:
                choice = move[-1]
                move = move[0:-2]
                for i in range(len(possible_moves)):
                    if move == possible_moves[i].moveString and possible_moves[i].isPawnPromotion:
                        f = 1 if gs.whiteToMove else (-1)
                        possible_moves[i].promotionChoice = PROMOTIONS[choice] * f 
                        selected_move = possible_moves[i]
            if selected_move == None:
                print("[ ]")
                temp = [possible_moves[i].moveString for i in range(len(possible_moves))]                
                break
            else:
                obj = one_hot_board(gs.board)
                gs.makeMove(selected_move)
        new_score = (found_moves / total_moves) * 100
        scores.append(new_score)
        print("(" + str(new_score) + "%)")
    print("Hello World!")
    return scores

def findGameStates():
    pgn_file = "./games/ficsgamesdb_202101_standard2000_nomovetimes_196479.pgn"
    all_games = Preprocessor.getGames(pgn_file=pgn_file)
    boards = []
    score = []
    score.append(len(boards))
    g = 0
    for game in all_games:
        g += 1
        print("")
        print("Game: " + str(g), end=" ")
        score.append(len(boards))
        gs = ChessEngine.GameState()
        game_moves = game.Moves
        num = 0
        for move in game_moves:
            possible_moves = gs.getValidMoves()
            selected_move = None
            for i in range(len(possible_moves)):
                if move == possible_moves[i].moveString:
                    selected_move = possible_moves[i]
                    break
            if selected_move != None:
                gs.makeMove(selected_move)
                if len(boards) > 0:
                    found = False
                    for i in range(len(boards)):
                        if (boards[i] == gs.board).all():
                            found = True
                            break
                    if not found:
                        #print("+", end=" ")
                        num += 1
                        boards.append(np.array(gs.board))
                else:
                    boards.append(np.array(gs.board))
            else:
                break
        print("(" + str(num) + ")", end=" ")
    return (boards, score)

def one_hot_board(board, white_perspective=True):
    # space = np.zeros(15, dytpe=int)
    # data = np.zeros(960, dtype=int)
    f = 1 if white_perspective else (-1)
    LUT = np.diag(np.ones(13, dtype=int))
    data = np.array([], dtype=int)
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            data = np.append(data, LUT[piece])
    return data
    

if __name__ == "__main__":
    '''x = findGameStates()
    plt.plot(x[1])
    plt.show()'''
    score = testEngine()
    score.sort()
    plt.plot(score)
    plt.show()


    print("Hello World")
