import ChessMain, ChessEngine, Preprocessor 
import numpy as np
from matplotlib import pyplot as plt

DEBUG = True
COLUMNS = {'a': 7, 'b': 6, 'c': 5, 'd': 4, 'e': 3, 'f': 2, 'g': 1, 'h': 0}
PROMOTIONS = {'Q': 5, 'R': 4, 'B': 3, 'N': 2}

def testEngine():
    pgn_file = "./games/ficsgamesdb_202101_standard2000_nomovetimes_196479.pgn"
    games = Preprocessor.getGames(pgn_file=pgn_file)
    total_fail = 0
    for num, game in enumerate(games):
        gs = ChessEngine.GameState()
        moves = game.Moves
        score = 0
        for i, move in enumerate(moves):
            next_move = gs.getMoveFromString(move)
            try:
                gs.makeMove(next_move)
                score += 1
            except:
                if move == '':
                    break
                else:
                    total_fail += 1
                    break
        score = (score * 100) / (i+1)
        print("Game: " + str(num+1) + " -- ( " + str(score) + "% )")
    print("Number of Fails: " + str(total_fail) + " / " + str(num+1))
    return total_fail


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
    #score.sort()
    #plt.plot(score)
    #plt.show()

    
    print("Hello World")
