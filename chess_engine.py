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

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = 0
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

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
        start_sq = (row, col)
        # White
        if self.white_to_move:
            if self.board[row+1][col] == 0:
                moves.append(Move((row, col), (row+1, col), self.board))
                if row < 7:
                    if self.board[row+1][col] == 0 and row == 1:
                        moves.append(Move((row, col), (row+2, col), self.board))
            if col < 7:
                if self.board[row+1][col+1] < 0:
                    moves.append(Move((row, col), (row+1, col+1), self.board))
            if col > 0:
                if self.board[row+1][col-1] < 0:
                    moves.append(Move((row, col), (row+1, col-1), self.board))

        # Black
        elif not self.white_to_move:
            if self.board[row-1][col] == 0:
                moves.append(Move((row, col), (row-1, col), self.board))
                if row > 1: 
                    if self.board[row-2][col] == 0 and row == 6:
                        moves.append(Move((row, col), (row-2, col), self.board))
            if col < 7:
                if self.board[row-1][col+1] > 0:
                    moves.append(Move((row, col), (row-1, col+1), self.board))
            if col > 0:
                if self.board[row-1][col-1] > 0:
                    moves.append(Move((row, col), (row-1, col-1), self.board))

    def get_knight_moves(self, row, col, moves):
        knightMoves = [(row+2, col+1), (row+2, col-1), (row-2, col+1), (row-2, col-1), (row+1, col+2), (row-1, col+2), (row+1, col-2), (row-1, col-2)]
        if self.white_to_move and self.board[row][col] > 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7):
                    if self.board[move[0]][move[1]] <= 0:
                        moves.append(Move((row, col), move, self.board))
        elif not self.white_to_move and self.board[row][col] < 0:
            for move in knightMoves:
                if (0 <= move[0] <= 7) and (0 <= move[1] <= 7):
                    if self.board[move[0]][move[1]] >= 0:
                        moves.append(Move((row, col), move, self.board))

    def get_bishop_moves(self, row, col, moves):
        d1 = row + 1
        d2 = col + 1
        d3 = 8 - row
        d4 = 8 - col
        if self.white_to_move and self.board[row][col] > 0:
            for i in range(1, min(d3, d4)):
                newRow = row + i
                newCol = col + i
                if self.board[newRow][newCol] == 0:
                    moves.append(Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] < 0:
                    moves.append(Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] > 0:
                    break
            for i in range(1, min(d1, d2)):
                newRow = row - i
                newCol = col - i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] < 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] > 0:
                    break
            for i in range(1, min(d2, d3)):
                newRow = row + i
                newCol = col - i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] < 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] > 0:
                    break
            for i in range(1, min(d1, d4)):
                newRow = row - i
                newCol = col + i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] < 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] > 0:
                    break
        
        if not self.white_to_move and self.board[row][col] < 0:
            for i in range(1, min(d3, d4)):
                newRow = row + i
                newCol = col + i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] > 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] < 0:
                    break
            for i in range(1, min(d1, d2)):
                newRow = row - i
                newCol = col - i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] > 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] < 0:
                    break
            for i in range(1, min(d2, d3)):
                newRow = row + i
                newCol = col - i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] > 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] < 0:
                    break
            for i in range(1, min(d1, d4)):
                newRow = row - i
                newCol = col + i
                if self.board[newRow][newCol] == 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                elif self.board[newRow][newCol] > 0:
                    moves.append(
                        Move((row, col), (newRow, newCol), self.board))
                    break
                if self.board[newRow][newCol] < 0:
                    break
             
    def get_rook_moves(self, row, col, moves):

        # White Rook's
        if self.white_to_move and self.board[row][col] > 0:
            for i in range(row+1, 8):
                # move up
                newSq = self.board[i][col]
                if newSq == 0:
                    moves.append(Move((row, col), (i, col), self.board))
                elif newSq < 0:
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                elif newSq > 0:
                    break
            for j in range(0, row):
                # move down
                i = row - (j + 1)
                newSq = self.board[i][col]
                if newSq == 0:
                    moves.append(Move((row, col), (i, col), self.board))
                elif newSq < 0:
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                elif newSq > 0:
                    break
            for i in range(col+1, 8):
                # move right
                newSq = self.board[row][i]
                if newSq == 0:
                    moves.append(Move((row, col), (row, i), self.board))
                elif newSq < 0:
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                elif newSq > 0:
                    break
            for j in range(0, col):
                # move left
                i = col - (j + 1)
                newSq = self.board[row][i]
                if newSq == 0:
                    moves.append(Move((row, col), (row, i), self.board))
                elif newSq < 0:
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                elif newSq > 0:
                    break
        
        # Black Rook's
        if not self.white_to_move and self.board[row][col] < 0:
            for i in range(row+1, 8):
                # move up
                newSq = self.board[i][col]
                if newSq == 0:
                    moves.append(Move((row, col), (i, col), self.board))
                elif newSq > 0:
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                elif newSq < 0:
                    break
            for j in range(0, row):
                # move down
                i = row - (j + 1)
                newSq = self.board[i][col]
                if newSq == 0:
                    moves.append(Move((row, col), (i, col), self.board))
                elif newSq > 0:
                    moves.append(Move((row, col), (i, col), self.board))
                    break
                elif newSq < 0:
                    break
            for i in range(col+1, 8):
                # move right
                newSq = self.board[row][i]
                if newSq == 0:
                    moves.append(Move((row, col), (row, i), self.board))
                elif newSq > 0:
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                elif newSq < 0:
                    break
            for j in range(0, col):
                # move left
                i = col - (j + 1)
                newSq = self.board[row][i]
                if newSq == 0:
                    moves.append(Move((row, col), (row, i), self.board))
                elif newSq > 0:
                    moves.append(Move((row, col), (row, i), self.board))
                    break
                elif newSq < 0:
                    break            

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        pass

    def get_valid_moves(self):
        return self.get_all_moves()

class Move():

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        # print(self.move_ID)

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

if __name__ == "__main__":
    gs = GameState()
    move = Move((0,0), (4,4), gs.board)
    gs.make_move(move)
    gs.get_valid_moves()
    exit()
