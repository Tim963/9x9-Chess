import pygame
import sys

# Grundeinstellungen
BOARD_SIZE = 9
SQUARE_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE

WHITE = (245, 245, 220)
BLACK = (119, 148, 85)
HIGHLIGHT = (200, 230, 80)
SELECTED = (180, 180, 70)

# Buchstaben für Figuren (Groß: weiß, klein: schwarz)
PIECE_TEXT = {
    'K': 'K', 'D': 'D', 'L': 'L', 'S': 'S', 'T': 'T', 'B': 'B',
    'k': 'K', 'd': 'D', 'l': 'L', 's': 'S', 't': 'T', 'b': 'B'
}

def get_piece_color(piece):
    if piece is None:
        return None
    return "white" if piece.isupper() else "black"

# Startaufstellung 9x9 mit 2 Damen
initial_board = [
    ['t', 'l', 's', 'd', 'k', 'd', 's', 'l', 't'],
    ['b'] * 9,
    [None] * 9,
    [None] * 9,
    [None] * 9,
    [None] * 9,
    [None] * 9,
    ['B'] * 9,
    ['T', 'L', 'S', 'D', 'K', 'D', 'S', 'L', 'T']
]

def on_board(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def opponent(turn):
    return "black" if turn == "white" else "white"

def king_pos(board, color):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c].upper() == 'K' and get_piece_color(board[r][c]) == color:
                return r, c
    return None

def pawn_moves(r, c, piece, board):
    moves = []
    color = get_piece_color(piece)
    drow = -1 if color == 'white' else 1
    start_row = 7 if color == 'white' else 1
    enemy = "black" if color == "white" else "white"
    # Ein Feld vor
    nr = r + drow
    if on_board(nr, c) and board[nr][c] is None:
        moves.append((nr, c))
        # Doppelschritt nur vom Startfeld (und nur wenn beide Felder frei)
        nr2 = r + 2*drow
        if r == start_row and on_board(nr2, c) and board[nr2][c] is None and board[nr][c] is None:
            moves.append((nr2, c))
    # Schlagen
    for dc in [-1, 1]:
        nr, nc = r + drow, c + dc
        if on_board(nr, nc) and board[nr][nc] and get_piece_color(board[nr][nc]) == enemy:
            moves.append((nr, nc))
    return moves

def knight_moves(r, c, piece, board):
    moves = []
    color = get_piece_color(piece)
    deltas = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]
    for dr, dc in deltas:
        nr, nc = r+dr, c+dc
        if on_board(nr, nc):
            if board[nr][nc] is None or get_piece_color(board[nr][nc]) != color:
                moves.append((nr, nc))
    return moves

def sliding_moves(r, c, piece, board, directions):
    moves = []
    color = get_piece_color(piece)
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if board[nr][nc] is None:
                moves.append((nr, nc))
            elif get_piece_color(board[nr][nc]) != color:
                moves.append((nr, nc))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves

def bishop_moves(r, c, piece, board):
    return sliding_moves(r, c, piece, board, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

def rook_moves(r, c, piece, board):
    return sliding_moves(r, c, piece, board, [(1, 0), (-1, 0), (0, 1), (0, -1)])

def queen_moves(r, c, piece, board):
    return bishop_moves(r, c, piece, board) + rook_moves(r, c, piece, board)

def king_moves(r, c, piece, board):
    moves = []
    color = get_piece_color(piece)
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if on_board(nr, nc):
                if board[nr][nc] is None or get_piece_color(board[nr][nc]) != color:
                    moves.append((nr, nc))
    return moves

def legal_moves_for(r, c, board, ignore_check=False):
    piece = board[r][c]
    if piece is None: return []
    if piece.upper() == "B":
        moves = pawn_moves(r, c, piece, board)
    elif piece.upper() == "S":
        moves = knight_moves(r, c, piece, board)
    elif piece.upper() == "L":
        moves = bishop_moves(r, c, piece, board)
    elif piece.upper() == "T":
        moves = rook_moves(r, c, piece, board)
    elif piece.upper() == "D":
        moves = queen_moves(r, c, piece, board)
    elif piece.upper() == "K":
        moves = king_moves(r, c, piece, board)
    else:
        moves = []
    # Kein Zug, der ins eigene Schach führt
    if not ignore_check:
        color = get_piece_color(piece)
        legal = []
        for nr, nc in moves:
            b2 = [row[:] for row in board]
            b2[nr][nc] = b2[r][c]
            b2[r][c] = None
            if not is_in_check(b2, color):
                legal.append((nr, nc))
        moves = legal
    return moves

def all_moves_for_color(board, color):
    all_moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p and get_piece_color(p) == color:
                for nr, nc in legal_moves_for(r, c, board):
                    all_moves.append(((r, c), (nr, nc)))
    return all_moves

def is_in_check(board, color):
    kp = king_pos(board, color)
    if not kp: return True
    kr, kc = kp
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p and get_piece_color(p) == opponent(color):
                for nr, nc in legal_moves_for(r, c, board, ignore_check=True):
                    if (nr, nc) == (kr, kc):
                        return True
    return False

def game_result(board, turn):
    in_check = is_in_check(board, turn)
    moves = all_moves_for_color(board, turn)
    if in_check and not moves:
        return f"{opponent(turn).capitalize()} hat Schachmatt gewonnen!"
    elif not in_check and not moves:
        return "Patt: Unentschieden"
    return None  # läuft weiter

def draw_board(selected, moves, result):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            rect = (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            base_color = WHITE if (r + c) % 2 == 0 else BLACK
            color = base_color
            if (r, c) == selected:
                color = SELECTED
            elif (r, c) in moves:
                color = HIGHLIGHT
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (160, 160, 160), rect, 1)
    if result:
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((255,255,200,190))
        screen.blit(overlay, (0,0))
        result_surface = font_result.render(result, True, (70,0,0))
        rect = result_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
        screen.blit(result_surface, rect)

def draw_pieces(board):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            p = board[r][c]
            if p:
                # Weiß fett, Schwarz normal dunkelgrau
                color = (0,0,0) if p.isupper() else (60,60,60)
                text = PIECE_TEXT[p]
                font = font_white if p.isupper() else font_black
                t = font.render(text, True, color)
                rect = t.get_rect(center=((c + 0.5) * SQUARE_SIZE, (r + 0.5) * SQUARE_SIZE))
                screen.blit(t, rect)

pygame.init()
pygame.display.set_caption("9x9 CHESS")

try:
    font_white = pygame.font.SysFont('arial', 34, bold=True)
except:
    font_white = pygame.font.SysFont('sansserif', 34, bold=True)
font_black = pygame.font.SysFont('arial', 32)
font_result = pygame.font.SysFont('arial', 27, bold=True)
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

def main():
    board = [row[:] for row in initial_board]
    turn = "white"
    selected = None
    moves = []
    result = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and not result:
                mx, my = event.pos
                c, r = mx // SQUARE_SIZE, my // SQUARE_SIZE
                if on_board(r,c):
                    if selected is None:
                        if board[r][c] and get_piece_color(board[r][c]) == turn:
                            selected = (r, c)
                            moves = legal_moves_for(r, c, board)
                        else:
                            selected = None
                            moves = []
                    else:
                        if (r, c) == selected:
                            selected = None
                            moves = []
                        elif (r, c) in moves:
                            # Zug machen
                            piece = board[selected[0]][selected[1]]
                            board[r][c] = piece
                            board[selected[0]][selected[1]] = None
                            # Bauernumwandlung
                            if piece.upper() == "B":
                                if (turn == "white" and r == 0) or (turn == "black" and r == BOARD_SIZE-1):
                                    board[r][c] = "D" if turn == "white" else "d"
                            turn = opponent(turn)
                            selected = None
                            moves = []
                            result = game_result(board, turn)
                        else:
                            if board[r][c] and get_piece_color(board[r][c]) == turn:
                                selected = (r, c)
                                moves = legal_moves_for(r, c, board)
        draw_board(selected, moves, result)
        draw_pieces(board)
        pygame.display.flip()

if __name__ == "__main__":
    main()
