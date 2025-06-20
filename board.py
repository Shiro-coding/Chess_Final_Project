# 棋子 Unicode 表
pieces = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

# 初始棋盤
def starting_board():
    return [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]
