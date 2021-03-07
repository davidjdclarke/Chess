import numpy as np

class GameState():
    def __init__(self):
        self.board = np.zeros((8, 8))
        self.reset()
    
    def reset(self):
        self.board = np.zeros((8, 8))
        self.board[0] = [4, 2, 3, 6, 5, 3, 2, 4]
        self.board[1] = [1, 1, 1, 1, 1, 1, 1, 1]
        self.board[6] = [-1, -1, -1, -1, -1, -1, -1, -1]
        self.board[7] = [-4, -2, -3, -6, -5, -3, -2, -4]
        
        self.LUT = {'bp': -1, 'bN': -2, 'bB': -3, 'bR': -4, 'bQ': -5, 'bK': -6,
                    'wp': 1, 'wN': 2, 'wB': 3, 'wR': 4, 'wQ': 5, 'wK': 6,
                    '--': 0}
        
        white_to_move = True
        move_log = []

if __name__ == "__main__":
    b = GameState()
    exit()