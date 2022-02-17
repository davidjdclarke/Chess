import numpy as np
import engine
import tensorflow as tf
import chessnet
import preprocessor
from matplotlib import pyplot as plt
import timeit

from tensorflow.keras.layers import Input, Conv2D, Concatenate, Flatten, Dense, Softmax, MaxPooling2D
from tensorflow.keras.regularizers import l2


class ChessNet:
    def __init__(self, load_from_file='chessnetv1'):
        self.board = self.initialize_board()
        self.pieces = self.set_piece_value_lut()
        self.dropout_mask = np.zeros((64, 64))
        self.model = None

    def load_chess_net(self, file_path):
        """
        Load Chess Net

        Args:
            file_path -- string
        Return:
            None
        """
        try:
            self.model = tf.keras.Model.load_weights(file_path)
        except:
            print("Failed to load tf.keras.Model")

    def initial_conv_block(self, inputs=None, filters=[(16, 2), (64, 4), (64, 6), (16, 16)], dropout_prob=0, max_pooling=True):
        """
        Define the first layer of convolution for the ChessNet Architecture

        Arguments:
            inputs -- Input tensor
            filters -- Filter size and dimensions
        Returns
            output -- Next layer
        """
        conv_layers = []
        for filter in filters:
            n_filters, kernel_dim = filter[0], (filter[1], filter[1])
            conv = Conv2D(n_filters,
                          kernel_size=kernel_dim,
                          activation='relu',
                          strides=2,
                          padding="same", )(inputs)
            conv_layers.append(conv)
        output = Concatenate()(conv_layers)
        return output

    def create_chessnet(self):
        """
        Chess Net architecture

        Arguments:
            None
        Returns:
            model -- tf.keras.Model
        """
        input_shape = (16, 16, 1)
        inputs = Input(input_shape)
        conv1 = self.initial_conv_block(inputs)
        conv2 = Conv2D(filters=256,
                       kernel_size=(3, 3),
                       activation='relu',
                       padding="same")(conv1)
        conv3 = Conv2D(filters=512,
                       kernel_size=(3, 3),
                       activation='relu',
                       padding="same")(conv2)
        max1 = MaxPooling2D()(conv3)
        f1 = Flatten()(max1)
        dense1 = Dense(512,
                       activation='relu',
                       kernel_regularizer=l2(0.0001))(f1)
        dense2 = Dense(256,
                       activation='relu',
                       kernel_regularizer=l2(0.0001))(dense1)
        dense3 = Dense(4096,
                       activation='relu',
                       kernel_regularizer=l2(0.0001))(dense2)
        softmax = Softmax()(dense3)
        self.model = tf.keras.Model(inputs=inputs, outputs=softmax)

    def compile_model(self):
        self.model.compile(optimizer='adam',
                           loss=tf.keras.losses.MeanSquaredError(),
                           metrics=['accuracy'])

    def set_piece_value_lut(self):
        """
        Returns a numpy array look-up-table with the associated values of the white and black pieces.

        Input:
            None

        Output:
            lv: Layer Values, with piece weights
                - Type: np.ndarray()
                - Shape: 13 x 2 x 2
                - [empty, wP, wN, wB, wR, wQ, wK, bK, bQ, bR, bB, bN, bP]
        """
        nan = [[0, 0], [0, 0]]      # Empty Square
        P = [[1, 1], [0, 0]]        # White Pawn
        N = [[1, 0], [1, 0]]        # White Knight
        B = [[1, 1], [1, 0]]        # White Bishop
        R = [[1, 0], [0, 1]]        # White Rook
        Q = [[1, 1], [0, 1]]        # White Queen
        K = [[1, 1], [1, 1]]        # White King
        p = [[0, 1], [0, 0]]        # Black Pawn
        n = [[0, 0], [1, 0]]        # Black Knight
        b = [[0, 1], [1, 0]]        # Black Bishop
        r = [[0, 0], [0, 1]]        # Black Rook
        q = [[0, 1], [0, 1]]        # Black Queen
        k = [[0, 1], [1, 1]]        # Black King

        return np.array([nan, P, N, B, R, Q, K, k, q, r, b, n, p])

    def initialize_board(self):
        """
        Initialize the board with a numpy array of zeros (shape 16 x 16).

        Input:
            None

        Output:
            numpy zeros array of shape 16 x 16
        """
        return np.zeros((16, 16))

    def set_board(self, board=None, fen_str=None, return_array=True):
        """
        Set the board array in accordance to the game position indicated by either the FEN string input
        or, the GameState object.

        Inputs:
            gs:
                - Current games state
                - Type: GameState()

            fen_str:
                - FEN string
                - Type: String

            return_array:
                - True/False return the board state as a numpy array
                - Type: Boolean
        Outputs:
            None
        """
        if board is not None:
            for i in range(8):
                for j in range(8):
                    x, y = 2*i, 2*j
                    self.board[x:x+2, y:y+2] = self.pieces[board[i, j]]
        elif fen_str:
            pass
        if return_array:
            return self.board

    def create_dropout_mask(self,
                            legal_moves,
                            return_mask=True,
                            default_value=1,
                            as_str=False,
                            as_percentage=False,
                            player_is_white=True):
        """
        Create the dropout mask to be applied to the final layer of the output before the Softmax function
        is applied.

        Arguments:
            legal_moves -- [type(Move)], list of Move objects
            return_mask -- Boolean, return None or numpy array
            default_value -- float
            as_str -- Boolean
            as_percentage -- Boolean
            player_is_white -- Boolean

        Return:
            mask:
                - Mask of illegal moves
                - Type: numpy array
                - Shape: 64 x 64
        """
        self.dropout_mask = np.zeros((64, 64), dtype='float64')

        if as_percentage:
            value = 1 / len(legal_moves)
        else:
            value = default_value

        if as_str:
            lut = {"a": 0, "b": 8*1, "c": 8*2, "d": 8*3, "e": 8*4, "f": 8*5, "g": 8*6, "h": 8*7}      # Factors
            for m in legal_moves:
                x, y = lut[m[0]] + int(m[1]), lut[m[2]] + int(m[3])
                self.dropout_mask[x, y] = value
        else:
            if player_is_white:
                for m in legal_moves:
                    x = m.startRow + m.startCol * 8
                    y = m.endRow + m.endCol * 8
                    self.dropout_mask[x, y] = value
            else:
                lut = [7, 6, 5, 4, 3, 2, 1, 0]
                for m in legal_moves:
                    x = lut[m.startRow] + lut[m.startCol] * 8
                    y = lut[m.endRow] + lut[m.endCol] * 8
                    self.dropout_mask[x, y] = value
        if return_mask:
            return self.dropout_mask, value

    def get_squares_from_index(self, arr):
        """
        Returns the start and end row and column values given a network output index

        Arguments:
            arr -- tuple of length 2 (x, y)
        Return:
            start_row, start_col, end_row, end_col -- integers
        """
        index = np.argmax(arr)
        x = index // 64
        y = index % 64

        start_row = x % 8
        start_col = x // 8
        end_row = y % 8
        end_col = y // 8

        return (start_row, start_col, end_row, end_col)

    def select_move(self, gs):
        """
        Select the best move, given the current gamestate

        Args:
            gs -- GameState
        Returns:
            move -- Move
        """
        if gs.whiteToMove:
            board = gs.board
        else:
            board = (-1) * np.rot90(np.rot90(gs.board))
        board = self.set_board(board=board).reshape(1, 16, 16, 1)
        predictions = self.model.predict(board)

        legal_moves = gs.getValidMoves()
        legal_move_string = gs.getMovesAsStrings(legal_moves)
        dropout, _ = self.create_dropout_mask(legal_moves=legal_move_string, as_str=True)

        predictions = predictions.reshape(64, 64) * dropout
        pick = self.get_squares_from_index(predictions)

        for move in legal_moves:
            if move.startRow == pick[0] and move.startCol == pick[1]:
                if move.endRow == pick[2] and move.endCol == pick[3]:
                    return move
        print("Failed to find Valid Move")
        return legal_moves[np.random.ranint(0, len(legal_moves))]

    def train(self):
        """
        Train the ChessNet Model

        Arguments:
            None
        Return:
            chess_net -- tf.keras.Model
        """
        import os
        pgn_files = [f for f in os.listdir('./db')]

        MAX_GAMES_PER_SET = 20

        for file in pgn_files:
            games = preprocessor.getGames(file)
            x_train = np.zeros((len(moves), 16, 16, 1))
            y_train = np.zeros((len(moves), 64, 64))

            for i in range(MAX_GAMES_PER_SET):

        for num, game in enumerate(games):
            gs = engine.GameState()
            moves = game.Moves
            x_train = np.zeros((len(moves), 16, 16, 1))
            y_train = np.zeros((len(moves), 64, 64))
            for i, move in enumerate(moves):
                flag = False
                if gs.whiteToMove:
                    board = gs.board
                else:
                    board = (-1) * np.rot90(np.rot90(gs.board))

                try:
                    input_board = self.set_board(board=board).reshape(16, 16, 1)
                    x_train[i] = input_board

                    possible_moves = gs.getValidMoves()
                    y_train[i], value = self.create_dropout_mask(legal_moves=possible_moves,
                                                                 player_is_white=gs.whiteToMove)

                    next_move = gs.getMoveFromString(move)
                    temp, v = self.create_dropout_mask(legal_moves=[next_move],
                                                       default_value=1 - value,
                                                       as_percentage=False,
                                                       player_is_white=gs.whiteToMove)
                    y_train[i] = y_train[i] + temp

                    gs.makeMove(next_move)
                except:
                    flag = True
                    break

            if not flag:
                y_train = y_train.reshape(y_train.shape[0], 4096)
                self.model.fit(x_train, y_train, batch_size=32)

def train():
    """
    Train the ChessNet Model

    Arguments:
        None
    Return:
        chess_net -- tf.keras.Model
    """
    gp = ChessNet()
    model = chessnet.chessnet()

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.MeanSquaredError(),
                  metrics=['accuracy'])

    games = preprocessor.getGames()

    for num, game in enumerate(games):
        gs = engine.GameState()
        moves = game.Moves
        x_train = np.zeros((len(moves), 16, 16, 1))
        y_train = np.zeros((len(moves), 64, 64))
        for i, move in enumerate(moves):
            flag = False
            if gs.whiteToMove:
                board = gs.board
            else:
                board = (-1) * np.rot90(np.rot90(gs.board))

            try:
                input_board = gp.set_board(board=board).reshape(16, 16, 1)
                x_train[i] = input_board

                possible_moves = gs.getValidMoves()
                y_train[i], value = gp.create_dropout_mask(legal_moves=possible_moves,
                                                           player_is_white=gs.whiteToMove)

                next_move = gs.getMoveFromString(move)
                temp, v = gp.create_dropout_mask(legal_moves=[next_move],
                                                 default_value=1 - value,
                                                 as_percentage=False,
                                                 player_is_white=gs.whiteToMove)
                y_train[i] = y_train[i] + temp

                gs.makeMove(next_move)
            except:
                flag = True
                break

        if not flag:
            y_train = y_train.reshape(y_train.shape[0], 4096)
            model.fit(x_train, y_train, batch_size=32)
    print("Here")


def infitite_play():
    gs = engine.GameState()
    gp = ChessNet()
    model = chessnet.chessnet()

    while (1):
        if gs.whiteToMove:
            board = gs.board
        else:
            board = (-1) * np.rot90(np.rot90(gs.board))
        current_board = gp.set_board(board=board).reshape(1, 16, 16, 1)

        model_output = model.predict(current_board)

        legal_moves = gs.getValidMoves()
        legal_move_string = gs.getMovesAsStrings(legal_moves)
        dropout = gp.create_dropout_mask(legal_moves=legal_move_string)

        model_select = model_output.reshape(64, 64) * dropout

        pick = gp.get_squares_from_index(model_select)

        for move in legal_moves:
            if move.startRow == pick[0] and move.startCol == pick[1]:
                if move.endRow == pick[2] and move.endCol == pick[3]:
                    gs.makeMove(move)
                    break


def main():
    train_chessnet()


if __name__ == "__main__":
    chess_net = ChessNet()
    main()
    print("Hello World")
