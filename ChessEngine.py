import numpy as np

LUT = [None, 'wp', 'wN', 'wB', 'wR', 'wQ', 'wK',
       'wK', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']

FILES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8']

class GameState():
    def __init__(self):
        self.board = np.zeros((8, 8))
        self.reset()

    def reset(self):
        self.board = np.zeros((8, 8), dtype='int8')
        self.board[0] = [4, 2, 3, 6, 5, 3, 2, 4]
        self.board[1] = [1, 1, 1, 1, 1, 1, 1, 1]
        self.board[6] = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.board[7] = [-4, -2, -3, -6, -5, -3, -2, -4]

        self.LUT = {'bp': -1, 'bN': -2, 'bB': -3, 'bR': -4, 'bQ': -5, 'bK': -6,
                    'wp': 1, 'wN': 2, 'wB': 3, 'wR': 4, 'wQ': 5, 'wK': 6,
                    '--': 0}

        self.whiteToMove = True
        self.moveLog = []
        self.isCheck = False
        self.whiteKingLocation = (0, 3)
        self.whiteKingHasMoved = False
        self.blackKingLocation = (7, 3)
        self.blackKingHasMoved = False
        self.pins = ()
        self.checks = []
        self.winner = None
        self.gameOver = False
        self.checkMate = False
        self.staleMate = False
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move, promotion=None):
        self.board[move.startRow][move.startCol] = 0
        self.board[move.endRow][move.endCol] = move.pieceMoved
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.promotionChoice
        if move.pieceMoved == 6:
            self.whiteKingLocation = (move.endRow, move.endCol)
            self.whiteKingHasMoved = True
        elif move.pieceMoved == -6:
            self.blackKingLocation = (move.endRow, move.endCol)
            self.blackKingHasMoved = False

        # Enpassant
        if move.isEnpassant:
            lastMove = self.moveLog[-1]
            self.board[lastMove.endRow][lastMove.endCol] = 0

        # Castle Move
        if move.isCastle:
            f = 1 if self.whiteToMove else (-1)
            if (move.startCol - move.endCol) > 0:     # Kingside Castle
                self.board[move.startRow][0] = 0
                self.board[move.startRow][move.endCol+1] = 4 * f
            else:   # Queenside Castle
                self.board[move.startRow][7] = 0
                self.board[move.startRow][move.endCol-1] = 4 * f

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # undo castling rights
            self.castleRightsLog.pop() # remove the last castle rights
            # set current castle rights to old values
            self.currentCastlingRight = self.castleRightsLog[-1]

    def updateCastleRights(self, move):
        squares = [(0, 0), (0, 7), (7, 0), (7, 7)]
        piece = move.pieceMoved
        endSquare = (move.endRow, move.endCol)
        if endSquare == squares[0]:
            self.currentCastlingRight.wks = False
        elif endSquare == squares[1]:
            self.currentCastlingRight.wqs = False
        elif endSquare == squares[2]:
            self.currentCastlingRight.bks = False
        elif endSquare == squares[3]:
            self.currentCastlingRight.bqs = False
        if piece == 6:
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif piece == -6:
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif piece == 4:
            if move.startCol == 0:
                self.currentCastlingRight.wks = False
            if move.startCol == 7:
                self.currentCastlingRight.wqs = False
        elif piece == -4:
            if move.startCol == 0:
                self.currentCastlingRight.bks = False
            if move.startCol == 7:
                self.currentCastlingRight.bqs = False
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def getAllMoves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece > 0) and self.whiteToMove:
                    # White to move
                    if piece == 1:
                        self.getPawnMoves(row, col, moves)
                    elif piece == 2:
                        self.getKnightMoves(row, col, moves)
                    elif piece == 3:
                        self.getBishopMoves(row, col, moves)
                    elif piece == 4:
                        self.getRookMoves(row, col, moves)
                    elif piece == 5:
                        self.getQueenMoves(row, col, moves)
                    elif piece == 6:
                        self.getKingMoves(row, col, moves)
                elif (piece < 0) and not self.whiteToMove:
                    # Black to move
                    if piece == -1:
                        self.getPawnMoves(row, col, moves)
                    elif piece == -2:
                        self.getKnightMoves(row, col, moves)
                    elif piece == -3:
                        self.getBishopMoves(row, col, moves)
                    elif piece == -4:
                        self.getRookMoves(row, col, moves)
                    elif piece == -5:
                        self.getQueenMoves(row, col, moves)
                    elif piece == -6:
                        self.getKingMoves(row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])

        startSquare = (row, col)
        # White
        if self.whiteToMove:
            if self.board[row+1][col] == 0:
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row+1, col), self.board))
                    if row == 1:
                        if self.board[row+2][col] == 0:
                            moves.append(Move((row, col), (row+2, col), self.board))
            if col < 7:
                if self.board[row+1][col+1] < 0:
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((row, col), (row+1, col+1), self.board))
            if col > 0:
                if self.board[row+1][col-1] < 0:
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((row, col), (row+1, col-1), self.board))
            if len(self.moveLog) > 0:
                lastMove = self.moveLog[-1]
                if lastMove.enpassantPossible and (row, col) in lastMove.enpassantSquares:
                    if self.board[row+1][lastMove.endCol] == 0:
                        move = Move((row, col), (row+1, lastMove.endCol), self.board, isEnpassant=True)
                        moves.append(move)

        # Black
        elif not self.whiteToMove:
            if self.board[row-1][col] == 0:
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row-1, col), self.board))
                    if row == 6:
                        if self.board[row-2][col] == 0:
                            moves.append(Move((row, col), (row-2, col), self.board))
            if col < 7:
                if self.board[row-1][col+1] > 0:
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((row, col), (row-1, col+1), self.board))
            if col > 0:
                if self.board[row-1][col-1] > 0:
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board))
            if len(self.moveLog) > 0:
                lastMove = self.moveLog[-1]
                if lastMove.enpassantPossible and (row, col) in lastMove.enpassantSquares:
                    if self.board[row-1][lastMove.endCol] == 0:
                        move = Move((row, col), (row-1, lastMove.endCol),
                                    self.board, isEnpassant=True)
                        moves.append(move)

    def getKnightMoves(self, row, col, moves):
        knightMoves = [(row+2, col+1), (row+2, col-1), (row-2, col+1), (row-2, col-1), (row+1, col+2), (row-1, col+2), (row+1, col-2), (row-1, col-2)]
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])

        if self.whiteToMove and self.board[row][col] > 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7):
                    if self.board[move[0]][move[1]] <= 0 and not piecePinned:
                        moves.append(Move((row, col), move, self.board))
        elif not self.whiteToMove and self.board[row][col] < 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7) and not piecePinned:
                    if self.board[move[0]][move[1]] >= 0:
                        moves.append(Move((row, col), move, self.board))

    def getBishopMoves(self, row, col, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
        f = 1 if self.whiteToMove else (-1)

        for d in directions:
            if not piecePinned or pinDirection == d:
                for i in range(1, 8):
                    newRow = row + i * d[0]
                    newCol = col + i * d[1]
                    if 0 <= newCol < 8 and 0 <= newRow < 8:
                        if self.board[newRow][newCol] == 0:
                            moves.append(Move((row, col), (newRow, newCol), self.board))
                        elif self.board[newRow][newCol] * f < 0:
                            moves.append(Move((row, col), (newRow, newCol), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getRookMoves(self, row, col, moves):
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
        f = 1 if self.whiteToMove else (-1)

        for d in directions:
            if not piecePinned or pinDirection == d:
                for i in range(1, 8):
                    newRow = row + i * d[0]
                    newCol = col + i * d[1]
                    if 0 <= newCol < 8 and 0 <= newRow < 8:
                        if self.board[newRow][newCol] == 0:
                            moves.append(
                                Move((row, col), (newRow, newCol), self.board))
                        elif self.board[newRow][newCol] * f < 0:
                            moves.append(
                                Move((row, col), (newRow, newCol), self.board))
                            break
                        else:
                            break
                    else:
                        break

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        newMoves = [(row-1, col-1), (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col), (row+1, col+1)]
        f = 1 if self.whiteToMove else (-1)
        if self.whiteToMove:
            for move in newMoves:
                if (0 <= move[0] < 8) and (0 <= move[1] < 8):
                    if (self.board[move[0]][move[1]] * f < 0) or (self.board[move[0]][move[1]] == 0):
                        temp = self.whiteKingLocation
                        self.whiteKingLocation = (move[0], move[1])
                        isCheck, checks, pins = self.checkForPinsAndChecks()
                        self.whiteKingLocation = temp
                        if not isCheck:
                            moves.append(Move((row, col), (move[0], move[1]), self.board))
        else:
            for move in newMoves:
                if (0 <= move[0] < 8) and (0 <= move[1] < 8):
                    if (self.board[move[0]][move[1]] * f < 0) or (self.board[move[0]][move[1]] == 0):
                        temp = self.blackKingLocation
                        self.blackKingLocation = (move[0], move[1])
                        isCheck, checks, pins = self.checkForPinsAndChecks()
                        self.blackKingLocation = temp
                        if not isCheck:
                            moves.append(Move((row, col), (move[0], move[1]), self.board))
        self.getCastleMoves(row, col, moves, f)

    def getCastleMoves(self, row, col, moves, f):
        """
        Will generate all possible castle moves for the King, and append them to the moves list
        """
        if self.isCheck:
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves, f)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves, f)

    def getKingsideCastleMoves(self, row, col, moves, f):
        if self.board[row][col-1] == 0 and self.board[row][col-2] == 0:
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                move = Move((row, col), (row, col-2), self.board, isCastle=True)
                move.message = "Fuck this piece of shit"
                moves.append(move)

    def getQueensideCastleMoves(self, row, col, moves, f):
        if self.board[row][col+1] == 0 and self.board[row][col+2] == 0 and self.board[row][col+3] == 0:
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, isCastle=True))

    def getValidMoves(self):
        moves = []
        self.isCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.isCheck:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllMoves()
                check = self.checks[0] # Check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # Enemy piece attacking the King
                validSquares = []  # Sqaures pieces can move to, to eliminate the check
                if abs(pieceChecking) == 2:
                    # If the attacking piece is a knight, you must capture or move the king
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # Remove all moves that don't block the check, or move the King
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved != abs(6): # Must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            if abs(moves[i].pieceMoved) != 6: # King can still move out of check!
                                moves.remove(moves[i])
            else:  # Double check, must move the king
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check
            moves = self.getAllMoves()
        if len(moves) == 0:
            if self.isCheck:
                self.checkMate = True
                self.gameOver = True
                if self.whiteToMove:
                    self.winner = "Black"
                    print("Game Over: Black Wins!")
                else:
                    self.winner = "White"
                    print("Game Over: White Wins!")
            else:
                self.staleMate = True
                self.gameOver = True
                self.winner = "Draw"
                print("Game Over: Draw")
        return moves

    def inCheck(self):
        """
        Returns True, if and only if the King of the side to move is currently in check.
        """
        if self.whiteToMove:
            row = self.whiteKingLocation[0]
            col = self.whiteKingLocation[1]
        else:
            row = self.blackKingLocation[0]
            col = self.blackKingLocation[1]
        return self.squareUnderAttack(row, col)

    def squareUnderAttack(self, row, col):
        """
        Checks if a square on the board is under attack from enemy pieces, returns True if the square is attacked or
        if the square is occupied by another piece.
        Returns false if the square is undefended and empty.
        """
        if self.board[row][col] != 0:
            return True
        if self.whiteToMove:
            kingSquare = self.whiteKingLocation
            self.whiteKingLocation = (row, col)
            p, c, check = self.checkForPinsAndChecks()
            self.whiteKingLocation = kingSquare
        else:
            kingSquare = self.blackKingLocation
            self.blackKingLocation = (row, col)
            p, c, check = self.checkForPinsAndChecks()
            self.blackKingLocation = kingSquare
        return check

    def getDefenders(self, row, col):
        """
        Returns a list of all pieces with an attack on the position row, col.
        """
        self.whiteToMove = not self.whiteToMove
        attacks = []
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        knightMoves = [(row+2, col+1), (row+2, col-1), (row-2, col+1), (row-2, col-1),
                       (row+1, col+2), (row-1, col+2), (row+1, col-2), (row-1, col-2)]
        f = 1 if self.whiteToMove else (-1)
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                r = row + i * d[0]
                c = col + i * d[1]
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = self.board[r][c]
                    if piece * f > 0:  # if enemy piece
                        if j in [4, 5, 6, 7]: # diagonal move
                            if abs(piece) in [3, 5] or (abs(piece) == 6 and i == 1):
                                attacks.append(abs(piece))
                                if (abs(piece)) == 6:
                                    break
                            elif abs(piece) in [2, 4]:
                                break
                            elif abs(piece) == 1:
                                if i == 1 and d[0] == -f:
                                    attacks.append(abs(piece))
                                else:
                                    break
                        if j in [0, 1, 2, 3]:  # vertical/straight move
                            if abs(piece) in [4, 5] or (abs(piece) == 6 and i == 1):
                                attacks.append(abs(piece))
                                if (abs(piece)) == 6:
                                    break
                            elif abs(piece) in [1, 2, 3]:
                                break
                else:
                    break
        for j in range(len(knightMoves)):
            r = knightMoves[j][0]
            c = knightMoves[j][1]
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] * f == 2:
                    attacks.append(2)
        self.whiteToMove = not self.whiteToMove
        return attacks
                            
            

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        isCheck = False
        if self.whiteToMove:
            f = 1
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            f = -1
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            posiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if (endPiece * f) > 0:
                        # If the end piece is of same side
                        if posiblePin == ():  # 1st piece blocking
                            posiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd piece blocking, so no possible pin
                            break
                    elif (endPiece * f) < 0:
                        """
                        This is a little tricky, in this case we have found an enemy piece with a potential attack on the King.
                        There are multiple cases that can occur, they depend on what type of piece is attacking.
                        Cases:
                        1.  Pawn
                        2.  Bishop
                        3.  Rook
                        4.  Queen
                        """
                        #  Pawn
                        if abs(endPiece) == 1 and i == 1:
                            if f == -1:  # Black to move
                                if j in [4, 5]:
                                    isCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                            else:
                                if j in [6, 7]:  # White to move
                                    isCheck = True
                                    checks.append((endRow, endCol, d[0], d[1]))
                        #  Bishop and Queen (pt. 1)
                        elif abs(endPiece) in [3, 5] and j in [4, 5, 6, 7]:
                            if posiblePin == ():
                                isCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                            else:
                                pins.append(posiblePin)
                        #  Rook and Queen (pt. 2)
                        elif abs(endPiece) in [4, 5] and j in [0, 1, 2, 3]:
                            if posiblePin == ():
                                isCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                            else:
                                pins.append(posiblePin)
                        else:
                            break
                else:
                    break  # space off the board
        possibleNightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for j in possibleNightMoves:
            endRow = startRow + j[0]
            endCol = startCol + j[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == -2 * f:
                    isCheck = True
                    checks.append((endRow, endCol, j[0], j[1]))
        return isCheck, pins, checks

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    def __init__(self, startSquare, endSquare, board, isEnpassant=False, isCastle=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.board = board
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        self.promotionChoice = None
        self.isCastle = isCastle
        self.isEnpassant = isEnpassant
        self.enpassantPossible = False
        self.enpassantSquares = []
        if (self.pieceMoved == 1 and self.endRow == 7) or (self.pieceMoved == -1 and self.endRow == 0):
            self.isPawnPromotion = True

        # Checks if enpassant
        if abs(self.pieceMoved) == 1 and abs(self.startRow - self.endRow) == 2:
            f = 1 if self.pieceMoved > 0 else (-1)
            for i in [-1, 1]:
                col = self.endCol + i
                if 0 <= col < 8:
                    if self.board[self.endRow][col] == -1 * f:
                        self.enpassantPossible = True
                        self.enpassantSquares.append((self.endRow, col))
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.message = None


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        pieceMovedAsStr = LUT[int(self.pieceMoved)]
        startSquareAsString = FILES[self.startCol] + ROWS[self.startRow]
        endSquareAsString = FILES[self.endCol] + ROWS[self.endRow]

        moveString = "(" + pieceMovedAsStr + ") " + startSquareAsString + "x" + endSquareAsString
        return str(moveString)

    def setPromotionChoice(self, choice):
        pieces = {'q': 5, 'r': 4, 'b': 3, 'n': 2}
        f = 1 if self.pieceMoved > 0 else (-1)
        self.promotionChoice = pieces[choice] * f

if __name__ == "__main__":
    gs = GameState()
    move = Move((0,0), (4,4), gs.board)
    gs.makeMove(move)
    gs.getValidMoves()
    exit()
