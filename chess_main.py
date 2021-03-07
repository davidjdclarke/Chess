import pygame as p
import chess_engine


p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
LUT = [None, 'wp', 'wN', 'wB', 'wR', 'wQ', 'wK', 'wK', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bp']
MAX_FPS = 15
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
    load_images(gs)
    running = True

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        
        clock.tick(MAX_FPS)
        draw_game_state(screen, gs)
        p.display.flip()



def draw_game_state(screen, gs):
    draw_board(screen)
    draw_pieces(screen, gs)


def draw_board(screen):
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


if __name__ == "__main__":
    main()
