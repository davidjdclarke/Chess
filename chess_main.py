import pygame as p
import chess_engine


p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
LUT = [None, 'wp', 'wN', 'wB', 'wR', 'wQ', 'wK', 'wK', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']
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
    gs = chess_engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False

    load_images(gs)
    running = True
    sq_selected = ()
    player_clicks = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handling
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x, y) position of the mouse
                col = location[0] // SQUARE_SIZE 
                row = location[1] // SQUARE_SIZE
                if sq_selected == (row, col): # clicked the same square twice
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)
                if len(player_clicks) == 2:
                    move = chess_engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(move)
                            print(move.get_chess_notation())
                            move_made = True
                        player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]       
            elif e.type ==p.KEYDOWN:
                if e.key == p.K_z:  # 'z' is pressed
                    gs.undo_move()
                    move_made = False

        if move_made:
            animate_move(gs.move_log[-1], screen, gs, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False

        clock.tick(MAX_FPS)
        draw_game_state(screen, gs, valid_moves, sq_selected)
        p.display.flip()


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if (gs.board[row][col] > 0 and gs.white_to_move) or (gs.board[row][col] < 0 and not gs.white_to_move):
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100) # transparency from 0 to 255
            s.fill(p.Color('blue'))
            screen.blit(s, (col*SQUARE_SIZE, row*SQUARE_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (SQUARE_SIZE * move.end_col, SQUARE_SIZE * move.end_row))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs)


def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))



def draw_pieces(screen, gs):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = LUT[int(gs.board[r][c])]
            if piece != None:
                screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def animate_move(move, screen, gs, clock):
    global colors
    coord = [] # list of locations to move through
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 15
    frame_count = int(pow(pow(abs(dR), 2) + pow(abs(dC), 2), 0.5)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = ((move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count))
        draw_board(screen)
        draw_pieces(screen, gs)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != 0:
            screen.blit(IMAGES[LUT[move.piece_captured]], end_square)
        screen.blit(IMAGES[LUT[move.piece_moved]], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(MAX_FPS)

if __name__ == "__main__":
    main()
