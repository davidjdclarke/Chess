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
        
        self.white_to_move = True
        self.move_log = []
        self.isCheck = False
        self.white_king_location = (0, 3)
        self.whiteKingHasMoved = False
        self.black_king_location = (7, 3)
        self.blackKingHasMoved = False
        self.pins = ()
        self.checks = []
        self.winner = None
        self.game_over = False
        self.checkMate = False
        self.staleMate = False
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def make_move(self, move, promotion=None):
        self.board[move.start_row][move.start_col] = 0
        self.board[move.end_row][move.end_col] = move.piece_moved
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.promotion_choice
        if move.piece_moved == 6:
            self.white_king_location = (move.end_row, move.end_col)
            self.whiteKingHasMoved = True
        elif move.piece_moved == -6:
            self.black_king_location = (move.end_row, move.end_col)
            self.blackKingHasMoved = False
        self.move_log.append(move)

        # Castle Move
        if move.isCastle:
            f = 1 if self.white_to_move else (-1)
            if (move.start_col - move.end_col) > 0:     # Kingside Castle
                self.board[move.start_row][0] = 0
                self.board[move.start_row][move.end_col+1] = 4 * f
            else:   # Queenside Castle 
                self.board[move.start_row][7] = 0
                self.board[move.start_row][move.end_col-1] = 4 * f

        # update castling rights - whenever it is a rook or king move
        self.updateCastleRights(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

            # undo castling rights
            self.castleRightsLog.pop() # remove the last castle rights
            # set current castle rights to old values
            self.currentCastlingRight = self.castleRightsLog[-1]
 
    def updateCastleRights(self, move):
        piece = move.piece_moved
        if piece == 6:
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif piece == -6:
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif piece == 4:
            if move.start_col == 0:
                self.currentCastlingRight.wks = False
            if move.start_col == 7:
                self.currentCastlingRight.wqs = False
        elif piece == -4:
            if move.start_col == 0:
                self.currentCastlingRight.bks = False
            if move.start_col == 7:
                self.currentCastlingRight.bqs = False
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
    
    def get_all_moves(self):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if (piece > 0) and self.white_to_move:
                    # White to move
                    if piece == 1:
                        self.get_pawn_moves(row, col, moves)
                    elif piece == 2:
                        self.get_knight_moves(row, col, moves)
                    elif piece == 3:
                        self.get_bishop_moves(row, col, moves)
                    elif piece == 4:
                        self.get_rook_moves(row, col, moves)
                    elif piece == 5:
                        self.get_queen_moves(row, col, moves)
                    elif piece == 6:
                        self.get_king_moves(row, col, moves)
                elif (piece < 0) and not self.white_to_move:
                    # Black to move
                    if piece == -1:
                        self.get_pawn_moves(row, col, moves)
                    elif piece == -2:
                        self.get_knight_moves(row, col, moves)
                    elif piece == -3:
                        self.get_bishop_moves(row, col, moves)
                    elif piece == -4:
                        self.get_rook_moves(row, col, moves)
                    elif piece == -5:
                        self.get_queen_moves(row, col, moves)
                    elif piece == -6:
                        self.get_king_moves(row, col, moves)
        return moves

    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])

        start_sq = (row, col)
        # White
        if self.white_to_move:
            if self.board[row+1][col] == 0:
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((row, col), (row+1, col), self.board))
                    if row == 1:
                        if self.board[row+2][col] == 0:
                            moves.append(Move((row, col), (row+2, col), self.board))
            if col < 7:
                if self.board[row+1][col+1] < 0:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((row, col), (row+1, col+1), self.board))
            if col > 0:
                if self.board[row+1][col-1] < 0:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((row, col), (row+1, col-1), self.board))

        # Black
        elif not self.white_to_move:
            if self.board[row-1][col] == 0:
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((row, col), (row-1, col), self.board))
                    if row == 6:
                        if self.board[row-2][col] == 0:
                            moves.append(Move((row, col), (row-2, col), self.board))
            if col < 7:
                if self.board[row-1][col+1] > 0:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((row, col), (row-1, col+1), self.board))
            if col > 0:
                if self.board[row-1][col-1] > 0:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((row, col), (row-1, col-1), self.board))

    def get_knight_moves(self, row, col, moves):
        knightMoves = [(row+2, col+1), (row+2, col-1), (row-2, col+1), (row-2, col-1), (row+1, col+2), (row-1, col+2), (row+1, col-2), (row-1, col-2)]
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])

        if self.white_to_move and self.board[row][col] > 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7):
                    if self.board[move[0]][move[1]] <= 0 and not piece_pinned:
                        moves.append(Move((row, col), move, self.board))
        elif not self.white_to_move and self.board[row][col] < 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7) and not piece_pinned:
                    if self.board[move[0]][move[1]] >= 0:
                        moves.append(Move((row, col), move, self.board))
      
    def get_bishop_moves(self, row, col, moves):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
        f = 1 if self.white_to_move else (-1)

        for d in directions:
            if not piece_pinned or pin_direction == d:
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

    def get_rook_moves(self, row, col, moves):
        directions = [(0, -1), (0, 1), (1, 0), (-1, 0)]
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
        f = 1 if self.white_to_move else (-1)

        for d in directions:
            if not piece_pinned or pin_direction == d:
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

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        newMoves = [(row-1, col-1), (row-1, col), (row-1, col+1), (row, col-1), (row, col+1), (row+1, col-1), (row+1, col), (row+1, col+1)]
        f = 1 if self.white_to_move else (-1)
        if self.white_to_move:
            for move in newMoves:
                if (0 <= move[0] < 8) and (0 <= move[1] < 8):
                    if (self.board[move[0]][move[1]] * f < 0) or (self.board[move[0]][move[1]] == 0):
                        temp = self.white_king_location
                        self.white_king_location = (move[0], move[1])
                        isCheck, checks, pins = self.check_for_pins_and_checks()
                        self.white_king_location = temp
                        if not isCheck:
                            moves.append(Move((row, col), (move[0], move[1]), self.board))
        else:
            for move in newMoves:
                if (0 <= move[0] < 8) and (0 <= move[1] < 8):
                    if (self.board[move[0]][move[1]] * f < 0) or (self.board[move[0]][move[1]] == 0):
                        temp = self.black_king_location
                        self.black_king_location = (move[0], move[1])
                        isCheck, checks, pins = self.check_for_pins_and_checks()
                        self.black_king_location = temp
                        if not isCheck:
                            moves.append(Move((row, col), (move[0], move[1]), self.board))     
        self.getCastleMoves(row, col, moves, f)

    def getCastleMoves(self, row, col, moves, f):
        """
        Will generate all possible castle moves for the King, and append them to the moves list
        """
        if self.isCheck:
            return
        if (self.white_to_move and self.currentCastlingRight.wks) or (not self.white_to_move and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves, f)
        if (self.white_to_move and self.currentCastlingRight.wqs) or (not self.white_to_move and self.currentCastlingRight.bqs):
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

    def get_valid_moves(self):
        moves = []
        self.isCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.white_to_move:
            king_row = self.white_king_location[0]
            king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.isCheck:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.get_all_moves()
                check = self.checks[0] # Check information
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]  # Enemy piece attacking the King
                valid_squares = []  # Sqaures pieces can move to, to eliminate the check
                if abs(piece_checking) == 2:
                    # If the attacking piece is a knight, you must capture or move the king
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                # Remove all moves that don't block the check, or move the King
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved != abs(6): # Must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares:
                            if abs(moves[i].piece_moved) != 6: # King can still move out of check!
                                moves.remove(moves[i])
            else:  # Double check, must move the king
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check
            moves = self.get_all_moves()
        if len(moves) == 0:
            if self.isCheck:
                self.game_over = True
                if self.white_to_move:
                    self.winner = "Black"
                    print("Game Over: Black Wins!")
                else:
                    self.winner = "White"
                    print("Game Over: White Wins!")
            else:
                self.game_over = True
                self.winner = "Draw"
                print("Game Over: Draw")
                    
        return moves

    def inCheck(self):
        """
        Returns True, if and only if the King of the side to move is currently in check.
        """
        if self.white_to_move:
            row = self.white_king_location[0]
            col = self.white_king_location[1]
        else:
            row = self.black_king_location[0]
            col = self.black_king_location[1]
        return self.squareUnderAttack(row, col)

    def squareUnderAttack(self, row, col):
        """
        Checks if a square on the board is under attack from enemy pieces, returns True if the square is attacked or
        if the square is occupied by another piece.
        Returns false if the square is undefended and empty.
        """
        if self.board[row][col] != 0:
            return True
        if self.white_to_move:
            kingSquare = self.white_king_location
            self.white_king_location = (row, col)
            p, c, check = self.check_for_pins_and_checks()
            self.white_king_location = kingSquare
        else:
            kingSquare = self.black_king_location
            self.black_king_location = (row, col)
            p, c, check = self.check_for_pins_and_checks()
            self.black_king_location = kingSquare
        return check
        

    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        isCheck = False
        if self.white_to_move:
            f = 1
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            f = -1
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            posible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if (end_piece * f) > 0:
                        # If the end piece is of same side
                        if posible_pin == ():  # 1st piece blocking
                            posible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd piece blocking, so no possible pin
                            break
                    elif (end_piece * f) < 0:
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
                        if abs(end_piece) == 1 and i == 1:
                            if f == -1:  # Black to move
                                if j in [4, 5]:
                                    isCheck = True
                                    checks.append((end_row, end_col, d[0], d[1]))
                            else: 
                                if j in [6, 7]:  # White to move
                                    isCheck = True
                                    checks.append((end_row, end_col, d[0], d[1]))
                        #  Bishop and Queen (pt. 1)
                        elif abs(end_piece) in [3, 5] and j in [4, 5, 6, 7]:
                            if posible_pin == ():
                                isCheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(posible_pin)
                        #  Rook and Queen (pt. 2)
                        elif abs(end_piece) in [4, 5] and j in [0, 1, 2, 3]:
                            if posible_pin == ():
                                isCheck = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(posible_pin)
                        else:
                            break
                else:
                    break  # space off the board
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for j in knight_moves:
            end_row = start_row + j[0]
            end_col = start_col + j[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece == -2 * f:
                    isCheck = True
                    checks.append((end_row, end_col, j[0], j[1]))
        return isCheck, pins, checks

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    def __init__(self, start_sq, end_sq, board, isCastle=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = False
        self.promotion_choice = None
        self.isCastle = isCastle
        if (self.piece_moved == 1 and self.end_row == 7) or (self.piece_moved == -1 and self.end_row == 0):
            self.is_pawn_promotion = True
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        self.message = None


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        piece_moved_as_str = LUT[int(self.piece_moved)]
        start_sq_as_str = FILES[self.start_col] + ROWS[self.start_row]
        end_sq_as_str = FILES[self.end_col] + ROWS[self.end_row]
        
        move_str = "(" + piece_moved_as_str + ") " + start_sq_as_str + "x" + end_sq_as_str
        return str(move_str) 

    def set_promotion_choice(self, choice):
        pieces = {'q': 5, 'r': 4, 'b': 3, 'n': 2}
        f = 1 if self.piece_moved > 0 else (-1)
        self.promotion_choice = pieces[choice] * f

if __name__ == "__main__":
    gs = GameState()
    move = Move((0,0), (4,4), gs.board)
    gs.make_move(move)
    gs.get_valid_moves()
    exit()
