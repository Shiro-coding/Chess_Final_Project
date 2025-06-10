from .utils import is_opponent_piece

def is_valid_king_move(board, from_row, from_col, to_row, to_col, is_white):
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    target = board[to_row][to_col]

    # 國王只能移動一格（八方向）
    if max(row_diff, col_diff) == 1:
        return target == "" or is_opponent_piece(target, is_white)

    return False
