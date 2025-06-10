# 判斷目標棋子是否為對方的棋子。
def is_opponent_piece(piece, is_white):
    return (piece.islower() and is_white) or (piece.isupper() and not is_white)

# 判斷目標棋子是否為己方棋子。
def is_own_piece(piece, is_white):
    return (piece.isupper() and is_white) or (piece.islower() and not is_white)
