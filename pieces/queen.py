from .rook import is_valid_rook_move
from .bishop import is_valid_bishop_move

def is_valid_queen_move(board, from_row, from_col, to_row, to_col, is_white):
    return (
        is_valid_rook_move(board, from_row, from_col, to_row, to_col, is_white)
        or
        is_valid_bishop_move(board, from_row, from_col, to_row, to_col, is_white)
    )
