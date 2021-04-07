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
        '''
        allPossibleMoves = self.gs.getValidMoves()
        captureMoves = self.findAllCaptures(allPossibleMoves)
        move = None
        if len(captureMoves) > 0:
            move = self.giveBestCaptures(captureMoves)
        if move == None:
            move = self.pickRandomMove()
        '''
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
            bestMinMaxScore = -10000 * f
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

    def searchForPotentialAttacks(self):
        """
        Returns a list of sqaures that are under attack from the opponent.
        ie. an opponent move could produce a loss of material.
        """
        self.gs.whiteToMove = not self.gs.whiteToMove

    def giveBestCaptures(self, captures, threshold=0):
        maxCapture = 0
        bestCapture = None
        for move in captures:
            if move.captureValue > threshold:
                maxCapture = move.captureValue
                bestCapture = move
        return bestCapture

    def findAllCaptures(self, moves):
        """
        This function will return the move that captures the most valuable piece of the opponents.
        Depth = 1 move
        If no piece is available for capture a random move is selected
        """
        allPossibleMoves = moves
        f = 1 if self.isWhite else (-1)
        capturingMoves = []
        searchedPositions = []
        for move in allPossibleMoves:
            if self.pieceValues[abs(move.pieceCaptured)] > 0:
                position = (move.endRow, move.endCol)
                if position not in searchedPositions:
                    firstMove = self.evaluateCapturesExchange(position)
                    capturingMoves.append(firstMove)
                    searchedPositions.append(position)
        return capturingMoves

    def evaluateCapturesExchange(self, pos, scores=[0], isPlayerMove=True, depth=0):
        """
        
        """
        officialMoves = []
        scores = [0]
        finished = False
        while not finished:
            if depth > 0:
                allPossibleMoves = self.gs.getValidMoves()
            else:
                allPossibleMoves = self.moves
            moves = []
            for move in allPossibleMoves:
                if move.endRow == pos[0] and move.endCol == pos[1]:
                    moves.append(move)
            if len(moves) > 0:
                lowest = 1000000
                for move in moves:
                    if abs(move.pieceMoved) < lowest:
                        lowest = abs(move.pieceMoved)
                        bestMove = move
                officialMoves.append(bestMove)
                f = 1 if isPlayerMove else (-1)
                newScore = scores[-1] + f * self.pieceValues[abs(bestMove.pieceCaptured)]
                scores.append(newScore)
                self.gs.makeMove(bestMove)
                isPlayerMove = not isPlayerMove
                depth += 1
            else:
                for i in range(depth):
                    self.gs.undoMove()
                finished = True
        numMoves = len(scores)
        if numMoves <= 2:
            finalScore = scores[-1]
        else:
            finalScore = scores[2]
            f = 1
            for i in range(2, numMoves):
                if f == -1:
                    if (scores[i] >= scores[i-2]) and (scores[i] >= scores[i-2]):
                        finalScore = min(scores[i-1], scores[i])
                    else:
                        break
                else:
                    if (scores[i] <= scores[i-2]) and (scores[i] <= scores[i-2]):
                        pass
                    else:
                        break
                f = f * (-1)
        firstMove = officialMoves[0]
        firstMove.setCapturesValue(finalScore)
        return firstMove

    def evaluateCapture(self, move):
        """
        Will return an integer value with the score of a capture.
        valuePieceCaptured - valueMaterialLeftVulnerable
        """
        evalGame = copy.copy(self.gs)
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
