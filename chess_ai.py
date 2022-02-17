import engine as eng
import main as cm
import random
import copy
import numpy as np

CHECKMATE = 10000
DEPTH = 3
MAX_THREADS = 4

PAWN_POSITION = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, -1, -3, -3, -1, 0, 0],
                 [1, 1, 1, 1, 1, 1, 1, 1],
                 [0, 1, 1, 4, 4, 2, 1, 1],
                 [1, 1, 2, 5, 5, 3, 1, 1],
                 [2, 2, 2, 6, 6, 4, 2, 2],
                 [5, 5, 8, 8, 8, 8, 5, 5],
                 [0, 0, 0, 0, 0, 0, 0, 0]])

KNIGHT_POSITION = np.array([[-5, -3, -1, -1, -1, -1, -3, 5],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 1, 1, 2, 2, 1, 1, 0], 
                   [0, 1, 2, 6, 6, 2, 1, 0], 
                   [0, 1, 2, 6, 6, 2, 1, 0], 
                   [0, 1, 1, 2, 2, 1, 1, 0], 
                   [0, 0, 1, 1, 1, 1, 0, 0], 
                   [0, 0, 0, 0, 0, 0, 0, 0]])

ROOK_POSITION = np.array([[-5, 1, 2, 3, 3, 0, 2, -5],
                 [0, 0, 0, 2, 2, 0, 0, 0],
                 [0, 0, 0, 1, 1, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]])

BISHOP_POSITION = np.array([[1, -2, -3, 0, 0, -3, 0, 1],
                   [2, 3, 2, 1, 1, 2, 3, 2],
                   [4, 6, 1, 1, 1, 1, 6, 4],
                   [1, 0, 1, 0, 0, 0, 1, 1],
                   [0, 1, 0, -1, -1, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0]])

QUEEN_POSITION = np.array([[-5, -2, -1, -1, 0, -2, -3, -5],
                  [0, 0, 0, 2, 1, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0],
                  [0, 0, 0, 1, 1, 0, 0, 0],
                  [0, 0, 0, 2, 2, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0]])

KING_POSITION = np.array([[3, 8, -1, -5, -1, 5, 7, 2],
                 [-2, -1, -8, -8, -8, -1, -1, -1],
                 [-3, -3, -3, -3, -3, -3, -3, -3],
                 [-5, -5, -2, -2, -2, -2, -5, -5],
                 [-4, -4, -3, -3, -3, -3, -4, -4],
                 [-4, -4, -3, -3, -3, -3, -4, -4],
                 [-4, -4, -3, -3, -3, -3, -4, -4],
                 [-4, -4, -3, -3, -3, -3, -4, -4]])

class ComputerPlayer:
    def __init__(self, gs, isWhite):
        self.pieceValues = [0, 10, 30, 30, 50, 90, 10000, -10000, -90, -50, -30, -30, -10]
        self.gs = gs
        self.isWhite = isWhite
        self.setBoardSquareValues()

    def setBoardSquareValues(self):
        if self.isWhite:
           self.SQUARE_VALUES = [np.zeros((8, 8)), PAWN_POSITION, KNIGHT_POSITION, BISHOP_POSITION, ROOK_POSITION, QUEEN_POSITION, KING_POSITION,
                            (-1)*np.rot90(np.rot90(KING_POSITION)), (-1)*np.rot90(np.rot90(QUEEN_POSITION)), (-1)*np.rot90(np.rot90(ROOK_POSITION)), (-1)*np.rot90(np.rot90(BISHOP_POSITION)), (-1)*np.rot90(np.rot90(KNIGHT_POSITION)), (-1)*np.rot90(np.rot90(PAWN_POSITION))]
        else:
            self.SQUARE_VALUES = [np.zeros((8, 8)), (-1)*PAWN_POSITION, (-1)*KNIGHT_POSITION, (-1)*BISHOP_POSITION, (-1)*ROOK_POSITION, (-1)*QUEEN_POSITION, (-1)*KING_POSITION,
                             np.rot90(np.rot90(KING_POSITION)), np.rot90(np.rot90(QUEEN_POSITION)), np.rot90(np.rot90(ROOK_POSITION)), np.rot90(np.rot90(BISHOP_POSITION)), np.rot90(np.rot90(KNIGHT_POSITION)), np.rot90(np.rot90(PAWN_POSITION))]


    def makeMove(self, gs):
        self.gs = gs
        self.moves = self.gs.getValidMoves()
        if len(self.moves) == 0:
            return None
        move = self.findBestMoveMinMax()
        if move == None:
            return None
        if move.isPawnPromotion:
            self.pawnPromotionChoice = 5 if self.isWhite else (-5)
        return move

    def findBestMoveMinMax(self, maxDepth=DEPTH, depth=0):
        f = 1 if depth % 2 == 0 else (-1)
        if depth == maxDepth:
            return self.scoreMaterial()
        else:
            possibleMoves = self.gs.getValidMoves()
            random.shuffle(possibleMoves)
            bestMinMaxScore = -100000 * f
            bestMove = None
            for move in possibleMoves:
                self.gs.makeMove(move)
                score = self.findBestMoveMinMax(depth=depth+1, maxDepth=maxDepth)
                if f == -1:
                    if bestMinMaxScore > score:
                        bestMinMaxScore = score
                        bestMove = move
                else:
                    if bestMinMaxScore < score:
                        bestMinMaxScore = score
                        bestMove = move
                self.gs.undoMove()
        if depth == 0:
            # print("Best Move: " + bestMove.moveString + ", Score: " + str(bestMinMaxScore))
            return bestMove
        else:
            return bestMinMaxScore

    def findBestMoveNegaMax():
        pass

    def scoreMaterial(self):
        score = 0
        f = 1 if self.isWhite else (-1)
        for row in range(8):
            for col in range(8):
                piece = self.gs.board[row][col]
                materialValue = self.pieceValues[piece * f]
                positionValue = self.SQUARE_VALUES[piece][row][col]
                score += materialValue + positionValue
        return score

    def pawnPromotion(self, move):
        move.setPromotionChoice = 'q'
        return move

    def pickRandomMove(self, allPossibleMoves=None):
        if allPossibleMoves == None:
            allPossibleMoves = self.gs.getValidMoves()
        index = random.randint(0, len(allPossibleMoves)-1)
        move = allPossibleMoves[index]
        if move.isPawnPromotion:
            move.setPromotionChoice = 'q'
        return allPossibleMoves[index]
