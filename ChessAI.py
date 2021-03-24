import ChessEngine as eng
import ChessMain as cm
import random

class ComputerPlayer:
    def pickRandomMove(self, gs):
        allPossibleMoves = gs.getValidMoves()
        index = random.randint(0, len(allPossibleMoves)-1)
        move = allPossibleMoves[index]
        if move.isPawnPromotion:
            move.setPromotionChoice = 'q'
        return allPossibleMoves[index]
