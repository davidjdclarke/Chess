# Welcome
This project the merger between two passions of mine, Programming and the Game of Chess!

This project contains two files as of now, the of these is ChessMain.py.  This file uses the pygame libary to provide a graphical user interface for the user to interact with the pieces and play The Game of Chess.  The second, and more intersting file is the Chess Enigine (ChessEngine.py).  The Chess Engine is responsible for handling all logic related to the determining of moves, managing the game state and will be the main interactive program to go along side the addition of any decision making algorithms that I plan to add in the future.

## Getting Started
### Requirements
To run this program you will need the following.
- Python3.x.x active on your machine (Development was done using Python 3.8.5)
- Must have pip added to your system PATH (for setting up the virtual enviorment)
- You must have a Unix style terminal emulator installed, or an IDE that supports BASH style terminal commands
- Must have GIT installed on your machine

### Set Up
##### Cloning the repository
```
$ git clone https://github.com/davidjdclarke/Chess
```


# Chess
Chess is an abstract strategy game and involves no hidden information. It is played on a square chessboard with 64 squares arranged in an eight-by-eight grid. At the start, each player (one controlling the white pieces, the other controlling the black pieces) controls sixteen pieces: one king, one queen, two rooks, two knights, two bishops, and eight pawns. The object of the game is to checkmate the opponent's king, whereby the king is under immediate attack (in "check") and there is no way to remove it from attack on the next move. There are also several ways a game can end in a draw.

## Piece Movement
Moving is compulsory; it is illegal to skip a turn, even when having to move is detrimental. A player may not make any move that would put or leave the player's own king in check. If the player to move has no legal move, the game is over; the result is either checkmate (a loss for the player with no legal move) if the king is in check, or stalemate (a draw) if the king is not.

#### Pawn
A pawn can move forward to the unoccupied square immediately in front of it on the same file, or on its first move it can advance two squares along the same file, provided both squares are unoccupied (white dots in the diagram); or the pawn can capture an opponent's piece on a square diagonally in front of it on an adjacent file, by moving to that square (black "x"s). A pawn has two special moves: the en passant capture and promotion.

#### Knight
A knight moves to any of the closest squares that are not on the same rank, file, or diagonal. (Thus the move forms an "L"-shape: two squares vertically and one square horizontally, or two squares horizontally and one square vertically.) The knight is the only piece that can leap over other pieces.

#### Bishop
A bishop can move any number of squares diagonally, but cannot leap over other pieces.

#### Rook
A rook can move any number of squares along a rank or file, but cannot leap over other pieces. Along with the king, a rook is involved during the king's castling move.

#### Queen
A queen combines the power of a rook and bishop and can move any number of squares along a rank, file, or diagonal, but cannot leap over other pieces.

#### King
The king moves one square in any direction. The king also has a special move called castling that involves also moving a rook.