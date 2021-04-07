import ChessEngine as eng
import ChessMain as cm
import random
import copy

CHECKMATE = 10000


class ComputerPlayer:
    def __init__(self, gs, isWhite):
        self.pieceValues = [0, 10, 30, 30, 50, 90, 10000, -10000, -90, -50, -30, -30, -10]
        self.gs = gs
        self.isWhite = isWhite

    def makeMove(self, gs):
        self.gs = gs
        self.moves = self.gs.getValidMoves()
        move = self.findBestMove()
        if move.isPawnPromotion:
            self.pawnPromotionChoice = 5 if self.isWhite else (-5)
        return move

    def findBestMove(self, maxDepth=3, depth=0):
        f = 1 if depth % 2 == 0 else (-1)
        if depth == maxDepth:
            return self.scoreMaterial()
        else:
            possibleMoves = self.gs.getValidMoves()
            bestMinMaxScore = -100000 * f
            bestMove = None
            for move in possibleMoves:
                self.gs.makeMove(move)
                score = self.findBestMove(depth=depth+1, maxDepth=maxDepth)
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
            if bestMinMaxScore == 0:
                return self.pickRandomMove()
            else:
                return bestMove
        else:
            return bestMinMaxScore

    def scoreMaterial(self):
        score = 0
        f = 1 if self.isWhite else (-1)
        for row in range(8):
            for col in range(8):
                score += self.pieceValues[self.gs.board[row][col] * f]
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