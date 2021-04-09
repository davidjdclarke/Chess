# Welcome
This project covers a chess engine implimented in Python, a graphical user interface from which the player can verse the computer or a human opponnent and a chess playing AI.

## Getting Started
### Requirements
To run this program you will need the following.
- Python3.x.x active on your machine (Development was done using Python 3.8.5)
- Must have pip added to your system PATH (for setting up the virtual enviorment)
- You must have a Unix style terminal emulator installed, or an IDE that supports BASH style terminal commands
- Must have GIT installed on your machine

### Set Up
The following will walk you through how to set up the project enviorment on your machine.
##### Cloning the repository
The first step is to get a version of the project onto your machine.  In your terminal navigate to the root of your destination directory, then issue the following command:
```
$ git clone https://github.com/davidjdclarke/Chess
```
#### Setting Up The Virtual Enviorment
The next step is to create a virtual enviorment for python to run within.  The project source files you just downloaded includes a text file 'requirements.txt'.  This is a specially formatted file generated by pip to easy the process of library installation.

##### Create the virtual enviorment:
```
$ python3 -m venv chess-venv
```

##### Activate the Enviorment:
```
$ source chess-venv/bin/activate
```

##### Install Dependancies 
```
$ pip3 install -r requirements.txt
```
### Running the Code
One last step before you run the code is you must unzip the compressed_images file, and rename the image directory as simply 'images'. 

This can be done with the following command:
```
$ unzip images.zip
```

The final step is simply to start the game!

Use this command:
```
$ python3 ChessMain.py
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
