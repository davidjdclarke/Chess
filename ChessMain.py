import pygame as p
import ChessEngine


p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
LUT = [None, 'wp', 'wN', 'wB', 'wR', 'wQ', 'wK',
       'wK', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']
INVERSION = [7, 6, 5, 4, 3, 2, 1, 0]
MAX_FPS = 60
IMAGES = {}


def load_images(board):
    pieces = board.LUT
    del pieces['--']

    for piece in pieces.keys():
        IMAGES[piece] = p.image.load("images/" + str(piece) + ".png")


def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False

    load_images(gs)
    running = True
    squareSelected = ()
    playerClicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handling
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) position of the mouse
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                if playerIsWhite:
                    r, c = invertBoardSquare(row, col)
                else:
                    r, c = row, col
                if squareSelected == (row, col):  # clicked the same square twice
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (r, c)
                    playerClicks.append(squareSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(
                        playerClicks[0], playerClicks[1], gs.board)
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            if move.isPawnPromotion:
                                choiceMade = False
                                while (not choiceMade):
                                    for m in p.event.get():
                                        if m.type == p.KEYDOWN:
                                            if m.key == p.K_q:
                                                validMoves[i].setPromotionChoice('q')
                                                choiceMade = True
                                            elif m.key == p.K_r:
                                                validMoves[i].setPromotionChoice('r')
                                                choiceMade = True
                                            elif m.key == p.K_b:
                                                validMoves[i].setPromotionChoice('b')
                                                choiceMade = True
                                            elif m.key == p.K_n:
                                                validMoves[i].setPromotionChoice('n')
                                                choiceMade = True
                            gs.makeMove(validMoves[i])
                            print(move.getChessNotation())
                            moveMade = True
                        playerClicks = []
                    if not moveMade:
                        playerClicks = [squareSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # 'z' is pressed
                    gs.undoMove()
                    moveMade = False
                    validMoves = gs.getValidMoves()

        if moveMade:
            animateMove(gs.moveLog[-1], screen, gs, clock)
            validMoves = gs.getValidMoves()
            moveMade = False

        clock.tick(MAX_FPS)
        drawGameState(screen, gs, validMoves, squareSelected)
        p.display.flip()


def invertBoardSquare(row, col):
    """
    This function is going to 'invert' the board, flipping it so that the display can be viewed from either Black or Whites perspective.
    It will interact with drawBoard and drawPieces.
    """
    return (INVERSION[row], INVERSION[col])


def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        row, col = squareSelected
        if (gs.board[row][col] > 0 and gs.whiteToMove) or (gs.board[row][col] < 0 and not gs.whiteToMove):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # transparency from 0 to 255
            s.fill(p.Color('blue'))
            if playerIsWhite:
                r, c = invertBoardSquare(row, col)
            else:
                r, c = row, col
            screen.blit(s, (c*SQUARE_SIZE, r*SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    if playerIsWhite:
                        r, c = invertBoardSquare(move.endRow, move.endCol)
                    else:
                        r, c = move.endRow, move.endCol
                    screen.blit(s, (SQUARE_SIZE * c,
                                    SQUARE_SIZE * r))


def drawGameState(screen, gs, validMoves, squareSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen, gs)


def drawBoard(screen):
    """
    This function draws out the squares of the game board.  
    The colors are selcted from pygames Color Class as white and gray by defualt, but they can be changed to any color the user desires.
    """
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQUARE_SIZE, r *
                                              SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawPieces(screen, gs):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = LUT[int(gs.board[i][j])]
            if playerIsWhite:
                r, c = invertBoardSquare(i, j)
            else:
                r, c = i, j
            if piece != None:
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def animateMove(move, screen, gs, clock):
    global colors
    coord = []  # list of locations to move through
    if playerIsWhite:
        startRow, startCol = invertBoardSquare(move.startRow, move.startCol)
        endRow, endCol = invertBoardSquare(move.endRow, move.endCol)
    else:
        startRow, startCol = move.startRow, move.startCol
        endRow, endCol = move.endRow, move.endCol
    dR = endRow - startRow
    dC = endCol - startCol
    framesPerSquare = 15
    frameCount = int(
        pow(pow(abs(dR), 2) + pow(abs(dC), 2), 0.5)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((startRow + dR*frame/frameCount,
                 startCol + dC*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, gs)
        color = colors[(endRow + endCol) % 2]
        end_square = p.Rect(endCol*SQUARE_SIZE,
                            endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != 0:
            screen.blit(IMAGES[LUT[move.piece_captured]], end_square)
        screen.blit(IMAGES[LUT[move.pieceMoved]], p.Rect(
            c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    playerIsWhite = False
    main()
