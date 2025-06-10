from .utils import is_opponent_piece

def is_valid_pawn_move(board, from_row, from_col, to_row, to_col, is_white, en_passant_target = None):
    direction = -1 if is_white else 1
    start_row = 6 if is_white else 1
    target = board[to_row][to_col]

    row_diff = to_row - from_row
    col_diff = to_col - from_col

    # 一格向前走
    if col_diff == 0 and row_diff == direction and target == "":
        return True

    # 起始兩格前進
    if from_row == start_row and col_diff == 0 and row_diff == 2 * direction:
        between = board[from_row + direction][from_col]
        if between == "" and target == "":
            return True

    # 斜向吃子
    if abs(col_diff) == 1 and row_diff == direction:
        if target != "" and is_opponent_piece(target, is_white):
            return True
        # en passant：斜走到 en_passant_target，目標格必須為空
        if target == "" and en_passant_target == (to_row, to_col):
            return True
    return False

