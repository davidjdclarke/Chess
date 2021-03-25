import ChessEngine as eng
import ChessMain as cm
import random


class ComputerPlayer:
    def __init__(self, gs, isWhite):
        self.pieceValues = [0, 10, 30, 30, 50, 90, 10000]
        self.gs = gs
        self.isWhite = isWhite

    def makeMove(self, gs):
        self.gs = gs
        move = self.captureMostValuablePiece()
        if move.isPawnPromotion:
            self.pawnPromotion(move)
        return move

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

    def captureMostValuablePiece(self):
        """
        This function will return the move that captures the most valuable piece of the opponents.
        Depth = 1 move
        If no piece is available for capture a random move is selected
        """
        allPossibleMoves = self.gs.getValidMoves()
        f = 1 if self.isWhite else (-1)
        mostValuablePiece = 0
        mostValuableMove = None
        for move in allPossibleMoves:
            if self.pieceValues[abs(move.pieceCaptured)] > 0:
                if self.pieceValues[abs(move.pieceCaptured)] > mostValuablePiece:
                    captureProfit = self.evaluateCapture(move)
                    if captureProfit > 0:
                        mostValuablePiece = self.pieceValues[abs(move.pieceCaptured)]
                        mostValuableMove = move
                    else:
                        allPossibleMoves.remove(move)
        if mostValuablePiece > 0 and mostValuableMove != None:
            return mostValuableMove
        else:
            return self.pickRandomMove(allPossibleMoves)

    def evaluateCapture(self, move):
        """
        Will return an integer value with the score of a capture.
        valuePieceCaptured - valueMaterialLeftVulnerable
        """
        movedPieceValue = self.pieceValues[abs(move.pieceMoved)]
        capturedPieceValue = self.pieceValues[abs(move.pieceCaptured)]
        defenders = self.gs.getDefenders(move.endRow, move.endCol)
        if len(defenders) == 0:
            return capturedPieceValue
        else:
            self.gs.makeMove(move)
            attackers = self.gs.getDefenders(move.endRow, move.endCol)
            self.gs.undoMove()
            if len(attackers) == 0:
                return capturedPieceValue - movedPieceValue
            else:
                exchangeOver = False
                attackers.sort()
                defenders.sort()
                numAtt = len(attackers)
                numDef = len(defenders)
                outcomes = []
                outcomes.append(capturedPieceValue)
                for i in range(max(numAtt, numDef)):
                    if i < numAtt:
                        oppenentValue = outcomes[-1] - self.pieceValues[attackers[i]]
                        outcomes.append(oppenentValue)
                    if i < numDef:
                        computerValue = outcomes[-1] - self.pieceValues[defenders[i]]
                    if 1 < numDef or 1 < numAtt:
                        break
                computerChoices = []
                playerChoices = []
                bestPlayerMove = 10000
                bestPlayerMoveIndex = 0
                for i in range(len(outcomes)):
                    if i % 2:
                        computerChoices.append(outcomes[i])
                    else:
                        computerChoices.append(-10000)
                        if bestPlayerMove > outcomes[-i]:
                            bestPlayerMove = outcomes[-i]
                            bestPlayerMoveIndex = i
                        playerChoices.append(outcomes[i])
                return min(computerChoices)
