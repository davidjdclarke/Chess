import ChessEngine as eng
import ChessMain as cm
import random


class ComputerPlayer:
    def __init__(self, gs, isWhite):
        self.pieceValues = [0, 1, 3, 3, 5, 9, 1000]
        self.gs = gs
        self.isWhite = isWhite

    def makeMove(self, gs):
        return self.pickCaptureMostValuableCapture(gs)

    def pickRandomMove(self, allPossibleMoves):
        index = random.randint(0, len(allPossibleMoves)-1)
        move = allPossibleMoves[index]
        if move.isPawnPromotion:
            move.setPromotionChoice = 'q'
        return allPossibleMoves[index]

    def pickCaptureMostValuableCapture(self, gs):
        self.gs = gs
        allPossibleMoves = self.gs.getValidMoves()
        f = 1 if self.isWhite else (-1)
        mostValuablePiece = 0
        mostValuableMove = None
        for move in allPossibleMoves:
            if self.pieceValues[abs(move.pieceCaptured)] > 0:
                if self.pieceValues[abs(move.pieceCaptured)] > mostValuablePiece:
                    mostValuablePiece = self.pieceValues[abs(move.pieceCaptured)]
                    mostValuableMove = move
        if mostValuablePiece > 0 and mostValuableMove != None:
            return mostValuableMove
        else:
            return self.pickRandomMove(allPossibleMoves)
