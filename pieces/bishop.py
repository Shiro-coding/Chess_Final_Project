from .utils import is_opponent_piece

def is_valid_bishop_move(board, from_row, from_col, to_row, to_col, is_white):
    if abs(from_row - to_row) != abs(from_col - to_col):
        return False

    step_r = 1 if to_row > from_row else -1
    step_c = 1 if to_col > from_col else -1

    r, c = from_row + step_r, from_col + step_c
    while (r, c) != (to_row, to_col):
        if board[r][c] != "":
            return False
        r += step_r
        c += step_c

    destination = board[to_row][to_col]
    return destination == "" or is_opponent_piece(destination, is_white)
