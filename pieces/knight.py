from .utils import is_opponent_piece

def is_valid_knight_move(board, from_row, from_col, to_row, to_col, is_white):
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    target = board[to_row][to_col]

    # 馬走日：兩直一橫 or 兩橫一直
    is_l_shape = (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    if is_l_shape and (target == "" or is_opponent_piece(target, is_white)):
        return True

    return False
