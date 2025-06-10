---
title: README

---

# 以Python重建chess game的實作
## 前言
因為我本人很喜歡西洋棋，本身也是chess.com等級分(elo)1700的玩家。
所以想藉由這次機會，挑戰自己，重建這款遊戲。
本篇主要敘述我是如何實作、構想、遇到問題與解決方法等。
如果想查看我時記在哪天做了什麼，可以直接查看日誌。

## 目標

### 初期目標:
    1.完成基本規則
    2.棋盤顯示、棋子移動
### 中期目標:
    1.Check / Checkmate判斷
    2.和局判斷
    
### 後期目標:
    1.介面GUI (預期功能: 
                     1.棋盤/棋子樣式選擇
                     2.對戰模式選擇(本地、非本地、AI對手)
    2.加入AI對手
    3.非本地對戰             
 
## 首先是建立棋盤與棋子及main.py基本架構
本次將使用 tkinter，其是 Python 內建的 GUI（Graphical User Interface）圖形化介面套件，可以用來建立視窗、按鈕、文字框、標籤等互動式應用程式。
### 建立棋盤和棋子顯示
```
## main.py
import tkinter as tk

# 棋盤大小
ROWS, COLS = 8, 8
TILE_SIZE = 60

# 棋子 Unicode 符號（白: 大寫，黑: 小寫）
pieces = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙'
}

# 初始棋盤狀態
starting_board = [
    ["r", "n", "b", "q", "k", "b", "n", "r"],
    ["p"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["P"] * 8,
    ["R", "N", "B", "Q", "K", "B", "N", "R"]
]

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS * TILE_SIZE, height=ROWS * TILE_SIZE)
        self.canvas.pack()
        self.board = [row[:] for row in starting_board]
        self.selected = None
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = "white" if (r + c) % 2 == 0 else "gray"
                x1, y1 = c * TILE_SIZE, r * TILE_SIZE
                x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                piece = self.board[r][c]
                if piece:
                    self.canvas.create_text(
                        x1 + TILE_SIZE // 2,
                        y1 + TILE_SIZE // 2,
                        text=pieces[piece],
                        font=("Arial", 32)
                    )

    def on_click(self, event):
        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE
        print(f"Clicked: {row}, {col}")
        # 這裡之後會加選擇棋子與移動的邏輯

# 主程式
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess game")
    app = ChessGUI(root)
    root.mainloop()

```
###### Result:
<img style="display:block;margin:20px auto;padding:1px;border:1px #eee;width:70%;" src="https://hackmd.io/_uploads/SyepVUkXgx.png" />

## 加入基本移動功能
以```on_click()``` method 建立棋子的選取與移動，先使棋子具有移動的功能，尚未加入棋子的移動規則。
### 更新 on_click 函式的邏輯，加上「選擇 → 移動 → 重繪棋盤」的流程
```
    def on_click(self, event):
        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE
        clicked_piece = self.board[row][col]

        if self.selected is None:
            # 如果還沒選棋子，且這格有棋子，就選取它
            if clicked_piece:
                self.selected = (row, col)
                print(f"Selected: {clicked_piece} at ({row}, {col})")
        else:
            # 已選取，移動棋子到這格
            from_row, from_col = self.selected
            piece_to_move = self.board[from_row][from_col]
            print(f"Move {piece_to_move} from ({from_row},{from_col}) to ({row},{col})")

            self.board[row][col] = piece_to_move
            self.board[from_row][from_col] = ""
            self.selected = None
            self.draw_board()

```
###### Result:
![image](https://hackmd.io/_uploads/SkyAwIJQll.png =50%x) ![image](https://hackmd.io/_uploads/SyPW_UJXxl.png)


## 加入回合制與禁止移動敵方棋子
- 只能移動自己的棋子（白走白、黑走黑）
- 玩家輪流下（白→黑→白→...）
#### 更新 ChessGUI class中的 ```__init__()```和```on_click()``` method。
```
class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS * TILE_SIZE, height=ROWS * TILE_SIZE)
        self.canvas.pack()
        self.board = [row[:] for row in starting_board]
        self.selected = None
        self.turn = 'white'  #白方先下
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE
        clicked_piece = self.board[row][col]

        if self.selected is None:
            # 檢查是否點到「自己的」棋子
            if clicked_piece and self.is_own_piece(clicked_piece):
                self.selected = (row, col)
                print(f"Selected: {clicked_piece} at ({row}, {col})")
        else:
            from_row, from_col = self.selected
            piece_to_move = self.board[from_row][from_col]

            # 不讓吃自己
            if clicked_piece and self.is_own_piece(clicked_piece):
                self.selected = (row, col)
                return

            # 現在只做移動，不驗證合法性
            self.board[row][col] = piece_to_move
            self.board[from_row][from_col] = ""
            self.selected = None

            # 換回合
            self.turn = 'black' if self.turn == 'white' else 'white'
            print(f"Turn: {self.turn}")
            self.draw_board()

    def is_own_piece(self, piece):
        if self.turn == 'white':
            return piece.isupper()
        else:
            return piece.islower()

```
## 建立專案架構
把各種棋子的走法邏輯拆分到不同的 ```.py``` 檔案，讓程式乾淨好維護，更方便 debug 和擴充。
```
Chess/
│
├── main.py            ← GUI 主程式
├── board.py           ← 棋盤資料處理
└── pieces/
    ├── __init__.py    ← 讓這是個模組
    ├── pawn.py        ← 兵的走法邏輯
    ├── rook.py        ← 城堡的走法邏輯
    ├── knight.py      ← 騎士的走法邏輯
    ├── ...            ← 其他棋子(主教、皇后、國王)

```

## Pawn(兵) 的基本移動 ![plastic-pawn-icon-outline-style-vector](https://hackmd.io/_uploads/ryuQXrXQgl.jpg =5%x)

先介紹pawn，一般縮寫為**P**，在紀錄棋譜(紀錄一場棋局走過的每一步)甚至不標記，例如: Pe4 -> e4。
- 每個玩家都有8個pawn，pawn的走法為直線走一格，不過每一個pawn的第一步都可以走兩格，但之後都只能往前走一格。
![phpEH1kWv](https://hackmd.io/_uploads/rJQDW4mXxl.png =50%x)  

- pawn吃子與移動方式不同，不是往前吃而是往斜前吃
![phpvXSs5p](https://hackmd.io/_uploads/rk9CH4mQlg.png =50%x)


- 如果pawn前面有其他棋子且左前或右前沒有其他棋子可以吃則這隻兵就不能移動了。
![phpZxt6Ym](https://hackmd.io/_uploads/SJ2rVV7Qgx.png =50%x)  

以上是pawn的基本走法，其實還有promotion(升變)及En-Passant(吃過路兵)的特殊走法，我們之後再來說明。

### pieces/pawn.py 的基本走法程式
```
def is_valid_pawn_move(board, from_row, from_col, to_row, to_col, is_white):
    direction = -1 if is_white else 1
    start_row = 6 if is_white else 1
    target = board[to_row][to_col]

    # 一格向前走
    if to_col == from_col and to_row == from_row + direction and target == "":
        return True

    # 起始兩格
    if from_row == start_row and to_col == from_col and to_row == from_row + 2 * direction and board[from_row + direction][from_col] == "" and target == "":
        return True

    # 斜吃子
    if abs(to_col - from_col) == 1 and to_row == from_row + direction and target != "" and is_opponent_piece(target, is_white):
        return True

    return False

def is_opponent_piece(piece, is_white):
    return (piece.islower() and is_white) or (piece.isupper() and not is_white)

```
此外還要在main.py中引用:
```
from pieces.pawn import is_valid_pawn_move

# 移動時加判斷(on_click()下)
if piece_to_move.upper() == "P":
    is_white = piece_to_move.isupper()
    if not is_valid_pawn_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid pawn move")
        return
```
## Knight(馬) 的走法邏輯 ![image](https://hackmd.io/_uploads/SJiDVBQ7ge.png =7%x)

Knight，中文稱為馬或是騎士，英文簡稱**N**，不簡稱為K是因為會跟King(王)衝突。
- 雙方各有兩隻馬，白方的在b1格與g1格上，黑方的在b8格與g8格上。
![phptRZQID](https://hackmd.io/_uploads/ryFHLHmmge.png =50%x)

- knight走L字，以中文說就是走日字，兩格直 + 一格橫或反過來。
![phpVZb3tN (1)](https://hackmd.io/_uploads/BJcy1OmXll.png =50%x)

- 所以如果當一隻馬在e4格上，它就可以走到c3, c5, d2, d6, f2, f6, g3, g5八格。Knight的移動不會被阻擋，不存在象棋卡馬腳的問題，因此它也是西洋棋中非常靈活的棋子。
![phpVuLl4W](https://hackmd.io/_uploads/SyvygO7mxg.png =50%x)
### pieces/knight.py 走法邏輯程式
```
def is_valid_knight_move(board, from_row, from_col, to_row, to_col, is_white):
    dr = abs(to_row - from_row)
    dc = abs(to_col - from_col)
    target = board[to_row][to_col]

    # 馬走日：兩格直 + 一格橫 或 反過來
    if (dr == 2 and dc == 1) or (dr == 1 and dc == 2):
        if target == "" or is_opponent_piece(target, is_white):
            return True
    return False

def is_opponent_piece(piece, is_white):
    return (piece.islower() and is_white) or (piece.isupper() and not is_white)

```
此外還要在main.py中引用:
```
from pieces.knight import is_valid_knight_move

# 移動時加判斷(on_click())
if piece_to_move.upper() == "N":
    is_white = piece_to_move.isupper()
    if not is_valid_knight_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid knight move")
        return

```

## Bishop(主教) 的走法邏輯 ![image](https://hackmd.io/_uploads/rJRuBN4Qex.png =5%x)

Bishop，中文稱為主教，英文簡寫**B**。
- 雙方玩家各有兩個bishop，白方的在c1格與f1格上，黑方的在c8格與f8格上。
![phpqJNVSk](https://hackmd.io/_uploads/By0dLEE7le.png =50%x)

- bishop的移動方式為大斜線，只要敵方的棋子在斜線路徑上，且沒被其他棋子阻擋，bishop就可以進行吃子。
![phpdzgpdQ](https://hackmd.io/_uploads/S1PPD44Qlx.png =50%x)

- 雙方都各有一個黑格主bishop及一個白格bishop，黑格的無法走到白格上，反之亦然。
![php4dzIxh](https://hackmd.io/_uploads/BJr6_VEQge.png =50%x)


### pieces/bishop.py 走法邏輯程式

```
def is_valid_bishop_move(board, from_row, from_col, to_row, to_col, is_white):
    if abs(to_row - from_row) != abs(to_col - from_col):
        return False

    row_step = 1 if to_row > from_row else -1
    col_step = 1 if to_col > from_col else -1

    r, c = from_row + row_step, from_col + col_step
    while r != to_row and c != to_col:
        if board[r][c] is not None:
            return False
        r += row_step
        c += col_step

    destination = board[to_row][to_col]
    return destination is None or destination.isupper() != is_white
```
此外還要在main.py中引用:
```
from pieces.bishop import is_valid_bishop_move

# 移動時加判斷(on_click())
if piece_to_move.upper() == "B":
    is_white = piece_to_move.isupper()
    if not is_valid_bishop_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid bishop move")
        return
```
## Rook(車) 的走法邏輯 ![image](https://hackmd.io/_uploads/Bk3QTNNXxx.png =5%x)
Rook，中文稱為車或是城堡，英文簡稱**R**。
- 雙方玩家各有兩個rook，白方的在a1格與h1格上，黑方的在a8格與h8格上。
![image](https://hackmd.io/_uploads/Hy6XAVEXgg.png =50%x)

- rook的移動方式為大直線，只要敵方的棋子在直線路徑上，且沒被其他棋子阻擋，rook就可以進行吃子。 
![image](https://hackmd.io/_uploads/B13FC4V7lx.png =50%x)

### pieces/rook.py 走法邏輯程式
```
def is_valid_rook_move(board, from_row, from_col, to_row, to_col, is_white):
    if from_row != to_row and from_col != to_col:
        return False

    if from_row == to_row:
        step = 1 if to_col > from_col else -1
        for c in range(from_col + step, to_col, step):
            if board[from_row][c] is not None:
                return False
    else:
        step = 1 if to_row > from_row else -1
        for r in range(from_row + step, to_row, step):
            if board[r][from_col] is not None:
                return False

    destination = board[to_row][to_col]
    return destination is None or destination.isupper() != is_white

```
此外還要在main.py中引用:
```
from pieces.rook import is_valid_rook_move

# 移動時加判斷(on_click())
if piece_to_move.upper() == "R":
    is_white = piece_to_move.isupper()
    if not is_valid_rook_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid rook move")
        return
```

## Queen(皇后) 的走法邏輯 ![image](https://hackmd.io/_uploads/H1zvHD4mle.png =7%x)
Queen，中文稱為后或是皇后，英文簡稱**Q**。
- 雙方各有一個queen，白方的d1格上，黑方的在d8格上。
![phpGsIYjO](https://hackmd.io/_uploads/rkdcUDEXxe.png =50%x)


- Queen的移動方式就是bishop + rook，大直線加大斜線，因此queen是chess裡最強大的棋子。
![phpCQgsYR](https://hackmd.io/_uploads/HkRWPvV7el.png =50%x)
### pieces/queen.py 走法邏輯程式
```
from .bishop import is_valid_bishop_move
from .rook import is_valid_rook_move

def is_valid_queen_move(board, from_row, from_col, to_row, to_col, is_white):
    return (
        is_valid_bishop_move(board, from_row, from_col, to_row, to_col, is_white) or
        is_valid_rook_move(board, from_row, from_col, to_row, to_col, is_white)
    )
```
此外還要在main.py中引用:
```
from pieces.queen import is_valid_queen_move

# 移動時加判斷(on_click())
if piece_to_move.upper() == "Q":
    is_white = piece_to_move.isupper()
    if not is_valid_queen_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid queen move")
        return
```
## King(王) 的走法邏輯 ![3398_black-king](https://hackmd.io/_uploads/S1HlrO4Xeg.png =7%x)



King，中文稱為王或國王，英文簡稱**K**。
King是棋盤上唯一無法被吃掉的棋子，如果King受到攻擊，則稱為 "check" (將軍)。當king被check且無法移動任何一個格子則稱為"checkmate" (將殺)。被將殺的玩家輸掉本局遊戲。
- 在棋局開始時，白方的King位於e1格，而黑方的King位於e8格。
![phphyuHlD](https://hackmd.io/_uploads/rkMQGO4Xlg.png =50%x)

- King的移動方式為直線或斜線一格。因此國王非常脆弱，請務必保護好它!
![phpmVRKYr](https://hackmd.io/_uploads/rJolm_VXlg.png =50%x)

- 額外注意的是，當國王被check則一定要移走，否則犯規(illegal move)，例如下圖: 白方king被bishop check，此時只能選則將king移到e2格、f1格或是直接吃掉f2格上的bishop。
![phpFvrkZv](https://hackmd.io/_uploads/rJacrdV7el.png =50%x)

### pieces/king.py 走法邏輯程式
```
def is_valid_king_move(board, from_row, from_col, to_row, to_col, is_white):
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)

    if row_diff <= 1 and col_diff <= 1:
        destination = board[to_row][to_col]
        return destination is None or destination.isupper() != is_white
    return False

```
此外還要在main.py中引用:
```
from pieces.king import is_valid_king_move

# 移動時加判斷(on_click())
if piece_to_move.upper() == "K":
    is_white = piece_to_move.isupper()
    if not is_valid_King_move(self.board, from_row, from_col, row, col, is_white):
        print("Invalid King move")
        return
```
## 建立```__init__.py``` 讓Python把pieces/視為一個套件（package）。
### pieces/```__init__.py```

```
from .bishop import is_valid_bishop_move
from .rook import is_valid_rook_move
from .queen import is_valid_queen_move
from .king import is_valid_king_move
from .knight import is_valid_knight_move
from .pawn import is_valid_pawn_move
```

## 建立```utils.py```
在考慮到棋子吃子時會遇到判定是否為對方棋子，以避免吃到己方棋子，因此需要定義```is_opponent_piece()``` 及 ```is_own_piece()```，```pieces/```中的```.py```檔都會使用到，所以就創建```utils.py```統一整理，使得不重複程式碼且易維護。
### ```utils.py``` :
```
def is_opponent_piece(piece, is_white):
    """
    判斷目標棋子是否為對方的棋子。
    """
    return (piece.islower() and is_white) or (piece.isupper() and not is_white)

def is_own_piece(piece, is_white):
    """
    判斷目標棋子是否為己方棋子。
    """
    return (piece.isupper() and is_white) or (piece.islower() and not is_white)
```
並在```__init__.py```中加入:
```from .utils import is_own_piece, is_opponent_piece```
### 因為建立了```utils.py```，使得各個```pieces/```中的```.py```更好優化
以下是優化後的版本:
#### ```pawn.py``` :
```
from .utils import is_opponent_piece

def is_valid_pawn_move(board, from_row, from_col, to_row, to_col, is_white):
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

    return False
```
#### ```knight.py``` :
```
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
```
#### ```bishop.py``` :
```
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
```
#### ```rook.py``` : 
```
from .utils import is_opponent_piece

def is_valid_rook_move(board, from_row, from_col, to_row, to_col, is_white):
    if from_row != to_row and from_col != to_col:
        return False

    step_r = 0 if from_row == to_row else (1 if to_row > from_row else -1)
    step_c = 0 if from_col == to_col else (1 if to_col > from_col else -1)

    r, c = from_row + step_r, from_col + step_c
    while (r, c) != (to_row, to_col):
        if board[r][c] != "":
            return False
        r += step_r
        c += step_c

    destination = board[to_row][to_col]
    return destination == "" or is_opponent_piece(destination, is_white)
```
#### ```queen.py``` :
```
from .rook import is_valid_rook_move
from .bishop import is_valid_bishop_move

def is_valid_queen_move(board, from_row, from_col, to_row, to_col, is_white):
    return (
        is_valid_rook_move(board, from_row, from_col, to_row, to_col, is_white)
        or
        is_valid_bishop_move(board, from_row, from_col, to_row, to_col, is_white)
    )
```
#### ```king.py``` :
```
from .utils import is_opponent_piece

def is_valid_king_move(board, from_row, from_col, to_row, to_col, is_white):
    row_diff = abs(to_row - from_row)
    col_diff = abs(to_col - from_col)
    target = board[to_row][to_col]

    # 國王只能移動一格（八方向）
    if max(row_diff, col_diff) == 1:
        return target == "" or is_opponent_piece(target, is_white)

    return False
```
## 在 GUI 上顯示正確的棋盤座標（a~h 橫向，1~8 直向）
正確地擺放棋盤非常重要。原則是「白格在右」。當你面對棋盤時，最右邊的那個角格必須是白色的。當棋盤正確擺放時，這個規則對雙方玩家都適用。
![image](https://hackmd.io/_uploads/BJurn547lx.png)
棋盤也有正確的座標系，橫向八格為a\~h，直向八格為1\~8，建立正確的座標為了更好的建立棋譜，或是講述棋局。
![how-to-set-up-a-chessboard-7](https://hackmd.io/_uploads/r1cgoqNQxe.jpg =50%x)

### 更新```draw_board()``` 
```
def draw_board(self):
    self.canvas.delete("all")
    offset = 20  # 邊界空間
    for r in range(ROWS):
        for c in range(COLS):
            color = "white" if (r + c) % 2 == 0 else "gray"
            x1 = c * TILE_SIZE + offset
            y1 = r * TILE_SIZE + offset
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

            piece = self.board[r][c]
            if piece:
                self.canvas.create_text(
                    x1 + TILE_SIZE // 2,
                    y1 + TILE_SIZE // 2,
                    text=pieces[piece],
                    font=("Arial", 32)
                )

            # 畫橫向 a~h
            if r == 7:
                self.canvas.create_text(
                    x1 + TILE_SIZE // 2,
                    y2 + 10,
                    text=chr(ord("a") + c),
                    font=("Arial", 12)
                )

            # 畫直向 8~1
            if c == 0:
                self.canvas.create_text(
                    x1 - 10,
                    y1 + TILE_SIZE // 2,
                    text=str(8 - r),
                    font=("Arial", 12)
                )
```
及修改```on_click()```中:
```
row = (event.y - 20) // TILE_SIZE
col = (event.x - 20) // TILE_SIZE
```

### 點擊選擇棋子時提示正確棋盤座標
修改```on_click()```中self.selected的判斷式:
```
if self.selected is None:
    if clicked_piece and self.is_own_piece(clicked_piece):
        self.selected = (row, col)
        col_letter = chr(ord('a') + col)
        row_number = 8 - row
        print(f"已選擇: {clicked_piece} 在 {col_letter}{row_number}")
```
###### Result:
<img style="display:block;margin:20px auto;padding:1px;border:1px #eee;width:60%;" src="https://hackmd.io/_uploads/SyF4_sV7gl.png" />

## 紀錄棋譜
我們可以將棋譜記錄改為類似 Chess.com 的標準西洋棋代數記譜法（Algebraic Notation），這樣會更專業也更容易閱讀。
什麼是代數記譜法？
代數記譜法是目前最常用的西洋棋記譜方式，格式如下：
- 棋子代號：K（國王）、Q（皇后）、R（城堡）、B（主教）、N（騎士），兵（Pawn）不使用代號。
- 目的地座標：例如 e4。
- 吃子：使用 x 表示，例如 Nxe5 表示騎士吃掉 e5 的棋子。
- 王車易位：短易位為 0-0，長易位為 0-0-0。
- 升變：例如 e8=Q 表示兵升變為皇后。
- 將軍與將死：+ 表示將軍，# 表示將死。

### 建立```log_move()```
因為程式中還沒有關於 is_capture、is_check、is_checkmate 的規則定義，所以先寫is_capture判斷，暫時不處理 is_check 與 is_checkmate。將它們的部分用註解暫時停用，日後可以隨時啟用。
```
def log_move(self, piece, from_row, from_col, to_row, to_col):
    piece_notation = '' if piece.upper() == 'P' else piece.upper()
    from_file = chr(ord('a') + from_col)
    from_rank = str(8 - from_row)
    to_file = chr(ord('a') + to_col)
    to_rank = str(8 - to_row)

    target_piece = self.board[to_row][to_col]
    is_capture = bool(target_piece) and not self.is_own_piece(target_piece)

    capture_symbol = 'x' if is_capture else ''

    # 預留未來用的將軍與將死符號
    # check_symbol = '+' if is_check else '#' if is_checkmate else ''
    check_symbol = ''  # 目前尚未實作

    move_notation = f"{piece_notation}{from_file}{from_rank}{capture_symbol}{to_file}{to_rank}{check_symbol}"

    self.move_log.config(state='normal')
    if self.turn == 'white':
        self.move_count += 1
        self.move_log.insert('end', f"{self.move_count}. {move_notation} ")
    else:
        self.move_log.insert('end', f"{move_notation}\n")
    self.move_log.config(state='disabled')
    self.move_log.see('end')  # 自動滾動到最新

```

### 棋盤右側顯示棋譜
在棋盤右側建立區域使棋譜可視化。改用```tk.Frame```來放置棋盤和棋譜區域（左右並排）：
```
 def __init__(self, root):
        self.root = root
        self.root.title("Chess game")

        # 初始化棋盤大小與格數
        self.TILE_SIZE = 80
        self.ROWS = 8
        self.COLS = 8

        # 建立主框架與 GUI 元件
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # 建立棋盤 Canvas（左側）
        self.canvas = tk.Canvas(frame, width=self.COLS * self.TILE_SIZE, height=self.ROWS * self.TILE_SIZE)
        self.canvas.grid(row=0, column=0)

        # 建立棋譜區 Text（右側）
        self.move_log = tk.Text(frame, width=30, height=35, state='disabled', font=("Consolas", 12))
        self.move_log.grid(row=0, column=1, padx=10, sticky='n')

        # 其他初始化（畫棋盤、放棋子等）
        self.draw_board()
        self.place_initial_pieces()
```
### 因為改了很多```main.py```的部份，因此我下方放了目前為止完整的版本，順便優化了冗長或重複的程式碼，及做了更多的標註。
#### main.py優化版本:
```
import tkinter as tk
from board import pieces, starting_board
from pieces import (
    is_valid_knight_move,
    is_valid_bishop_move,
    is_valid_pawn_move,
    is_valid_queen_move,
    is_valid_rook_move,
    is_valid_king_move
)

# 棋盤參數
ROWS, COLS = 8, 8
TILE_SIZE = 80
OFFSET = 20  # 在繪製棋盤時，讓畫布向右下偏移 20px，留出座標標籤空間

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess game")

        # 初始化棋盤狀態
        self.board = [row[:] for row in starting_board()]
        self.turn = 'white'       # 白方先下
        self.selected = None      # 當前被選中的棋子座標 (row, col)
        self.move_count = 0       # 記錄回合數（每白方移動一次 +1）

        # 建立主框架：左側為棋盤，右側為棋譜區
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # 左側：棋盤 Canvas（淨畫布大小 = 8 格 * TILE_SIZE）
        self.canvas = tk.Canvas(
            frame,
            width=COLS * TILE_SIZE + OFFSET,
            height=ROWS * TILE_SIZE + OFFSET + 30
        )
        self.canvas.grid(row=0, column=0)

        # 右側：棋譜區（Text widget）
        self.move_log = tk.Text(
            frame,
            width=30,
            height=35,
            state='disabled',
            font=("Consolas", 12)
        )
        self.move_log.grid(row=0, column=1, padx=10, sticky='n')

        # 綁定滑鼠左鍵：點擊棋盤後觸發 on_click()
        self.canvas.bind("<Button-1>", self.on_click)

        # 首次繪製棋盤
        self.draw_board()

    def draw_board(self):
        """
        在 Canvas 上繪製棋盤格、座標標籤，以及當前所有棋子。
        """
        self.canvas.delete("all")
        # 先畫棋格與棋子，再畫座標標籤
        for r in range(ROWS):
            for c in range(COLS):
                # 計算這個格子的左上與右下座標 (加上 OFFSET)
                x1 = c * TILE_SIZE + OFFSET
                y1 = r * TILE_SIZE + OFFSET
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE

                # 棋格顏色：白格/灰格
                color = "white" if (r + c) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                # 如果此格有棋子，就畫出它
                piece = self.board[r][c]
                if piece:
                    self.canvas.create_text(
                        x1 + TILE_SIZE // 2,
                        y1 + TILE_SIZE // 2,
                        text=pieces[piece],
                        font=("Arial", 32)
                    )

        # 繪製橫向座標 a~h（在棋格下方）
        for c in range(COLS):
            x = c * TILE_SIZE + OFFSET + TILE_SIZE // 2
            y = ROWS * TILE_SIZE + OFFSET + 10  # 在棋格下方多 10px
            file_label = chr(ord('a') + c)
            self.canvas.create_text(x, y, text=file_label, font=("Arial", 12))

        # 繪製直向座標 8~1（在棋格左側）
        for r in range(ROWS):
            x = OFFSET - 10  # 在棋格左側多 10px
            y = r * TILE_SIZE + OFFSET + TILE_SIZE // 2
            rank_label = str(8 - r)
            self.canvas.create_text(x, y, text=rank_label, font=("Arial", 12))

    def is_own_piece(self, piece):
        """
        判斷傳入的 piece 是否屬於當前玩家 self.turn。
        白方棋子為大寫，黑方棋子為小寫。
        """
        if self.turn == 'white':
            return piece.isupper()
        else:
            return piece.islower()

    def on_click(self, event):
        """
        處理滑鼠左鍵點擊事件：選棋子、移動棋子、檢查合法性、更新棋譜、重繪棋盤。
        """
        # 把畫布座標換算回棋盤行列
        x_click = event.x
        y_click = event.y

        # 如果點擊在 OFFSET 之外才可能是有效棋盤區域
        if x_click < OFFSET or y_click < OFFSET:
            return

        col = (x_click - OFFSET) // TILE_SIZE
        row = (y_click - OFFSET) // TILE_SIZE

        # 如果點擊位置不在 0<=row<8, 0<=col<8 範圍，忽略
        if not (0 <= row < ROWS and 0 <= col < COLS):
            return

        clicked_piece = self.board[row][col]

        # --------------------------------------------------
        # Step1：如果尚未選取棋子 (self.selected is None)
        # --------------------------------------------------
        if self.selected is None:
            # 只能點到「自己」的棋子才算有效選取
            if clicked_piece and self.is_own_piece(clicked_piece):
                self.selected = (row, col)
            return

        # --------------------------------------------------
        # Step2：已選取過棋子，現在要嘗試移動
        # --------------------------------------------------
        from_row, from_col = self.selected
        piece_to_move = self.board[from_row][from_col]

        # 如果目標格有自己人棋子，就重新選取
        if clicked_piece and self.is_own_piece(clicked_piece):
            self.selected = (row, col)
            return

        # 移動前先檢查「合法性」
        is_white = piece_to_move.isupper()
        piece_type = piece_to_move.upper()

        valid = False
        if piece_type == "P":
            valid = is_valid_pawn_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "N":
            valid = is_valid_knight_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "R":
            valid = is_valid_rook_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "B":
            valid = is_valid_bishop_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "Q":
            valid = is_valid_queen_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "K":
            valid = is_valid_king_move(self.board, from_row, from_col, row, col, is_white)

        if not valid:
            print(f"Invalid {piece_type} move")
            self.selected = None
            return

        # --------------------------------------------------
        # Step3：若合法才「吃或走格子」並更新棋譜
        # --------------------------------------------------
        # 判斷是否吃子：只要目標格非空且非己方
        target_piece = self.board[row][col]
        is_capture = bool(target_piece) and not self.is_own_piece(target_piece)

        # 先更新棋盤陣列
        self.board[row][col] = piece_to_move
        self.board[from_row][from_col] = ""
        self.selected = None

        # 記錄棋譜
        self.log_move(piece_to_move, from_row, from_col, row, col, is_capture)

        # 換回合
        self.turn = 'black' if self.turn == 'white' else 'white'
        print(f"Turn: {self.turn}")

        # 重繪棋盤
        self.draw_board()

    def log_move(self, piece, from_row, from_col, to_row, to_col, is_capture=False):
        """
        以代數記譜法記錄單步移動：
        - 兵(Pawn) 不顯示符號，其它棋子顯示大寫字母。
        - 若吃子，在來源與目的之間加 'x'。
        - 目前不處理將軍 or 將死。
        """
        # 棋子代號 (Pawn 不顯示)
        piece_notation = '' if piece.upper() == 'P' else piece.upper()
        # 起始座標
        from_file = chr(ord('a') + from_col)
        from_rank = str(8 - from_row)
        # 目標座標
        to_file = chr(ord('a') + to_col)
        to_rank = str(8 - to_row)
        # 吃子符號
        capture_symbol = 'x' if is_capture else ''

        move_notation = f"{piece_notation}{from_file}{from_rank}{capture_symbol}{to_file}{to_rank}"

        # 更新 Text widget：白方先列回合號 + 空格，黑方則換行
        self.move_log.config(state='normal')
        if self.turn == 'white':
            self.move_count += 1
            self.move_log.insert('end', f"{self.move_count}. {move_notation} ")
        else:
            self.move_log.insert('end', f"{move_notation}\n")
        self.move_log.config(state='disabled')
        self.move_log.see('end')  # 自動滾動到底部

# 主程式：建立 TK 視窗並啟動
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

```
###### Result:
<img style="display:block;margin:0px auto;padding:1px;border:1px #eee;width:80%;" src="https://hackmd.io/_uploads/HJAND2Vmgg.png" />


## en passant實作
「en passant」（吃過路兵）是chess中一種特殊的兵卒吃子的規則，其原文為法語，意為「順便」或「路過時」。此規則的要點如下：

1. 適用棋子
   只有Pawn可以執行 en passant 吃子。規則既適用於棋盤任何位置的兵卒，也對黑白雙方對等。
   
2. 觸發條件

   - 一方兵尚未移動過，且位於第五橫列（White 的兵在第五橫列是 rank 5，Black 的兵在第五橫列是 rank 4）。
   - 對方剛好用第一次移動，從自己的第二橫列（一律 rank 2 或 rank 7）向前兩格直行，並且路過了你的兵所控制的那個格子。

3. 吃子方式

   - 當對方兵以兩格跨越方式移至與你的兵並列（即兩兵在同一橫列，相鄰直線相隔一格）之後，
   - 你可以在緊接的下一手（*must*，若跳過則喪失機會）中，將自己的兵斜向前移到對方兵「所路過」的那格，
   - 同時將對方的兵移出棋盤，完成吃子。

4. 示例
   假設白兵位於 e5，黑兵位於 d7，現在黑先手：
    &nbsp;&nbsp;1… d7–d5 : 黑兵跳至 d5，與白兵 e5 並列，中間橫跨了 d6，此時白可執行 en passant。

   2. e5xd6 en passant : 白兵從 e5 斜進 d6，並將剛剛移到 d5 的黑兵拿掉。
![image](https://hackmd.io/_uploads/SktcyaV7xl.png =40%x) -> ![image](https://hackmd.io/_uploads/Bkhxg6Emxx.png =40%x)

5. 記譜

   - 通常標記為「exd6 e.p.」，其中「e」是吃子的兵出發檔列，「xd6」表示吃入目標格，後綴「e.p.」表明是過路吃。

### 在```pawn.py```裡```if abs(col_diff) == 1 and row_diff == direction:``` 加入新的判斷式
```
if target == "" and en_passant_target == (to_row, to_col):
    return True
```
### 紀錄可以被 en passant 吃掉的目標格 (row, col)，若無則為 None:
在```__init__```中定義```self.en_passant_target = None```
### 在```on_click()```中呼叫```is_valid_pawn_move```時傳入 ```self.en_passant_target```:
```
if piece_type == "P":
    valid = is_valid_pawn_move(
        self.board,
        from_row, from_col,
        row, col,
        is_white,
        self.en_passant_target  # 傳入可過路吃的目標格
    )
```
在「執行移動」之後更新```self.en_passant_target```，並處理 en passant 捕獲:
```
# —— 先處理 en passant 捕獲 —— 
if piece_type == "P" and (row, col) == self.en_passant_target and self.en_passant_target is not None:
    # 被吃掉的兵位於原地斜走目標列的同一行
    captured_row = from_row
    captured_col = col
    self.board[captured_row][captured_col] = ""
    is_capture = true

# —— 然後更新棋盤陣列，移動兵或其他棋子 —— 
self.board[row][col] = piece_to_move
self.board[from_row][from_col] = ""
self.selected = None

# —— 記錄此移動棋譜 —— 
self.log_move(piece_to_move, from_row, from_col, row, col, is_capture)

# —— 更新 en_passant_target —— 
if piece_type == "P" and abs(row - from_row) == 2:
    # 記錄可被過路吃的格子：中間那一格
    self.en_passant_target = ((from_row + row) // 2, from_col)
else:
    self.en_passant_target = None
```
## 處裡```log_move()```的移動歧異
稍微說明移動歧異，當同時有兩個同色且相同的棋子都可以走到同一格，紀錄棋譜時若沒說明是從哪一列來的，就會使人看不懂，例如下圖: 
![image](https://hackmd.io/_uploads/SyLNyvBQxe.png =50%x)
此時兩個knight都可以走到e4格，若只紀錄Ne4，就會不知道是哪個knight走上去的。

#### 因此我定義了ambiguous變數來判斷歧異:
##### ```on_click()```:
```
ambiguous = False
        if piece_type in ("N", "R"):
            # 掃描所有同型同色棋子能否走到 (row, col)
            for r in range(ROWS):
                for c in range(COLS):
                    if (r, c) != (from_row, from_col) and self.board[r][
                        c].upper() == piece_type and self.is_own_piece(self.board[r][c]):
                        # 其他同型棋子也能走到同一格，算作歧義
                        fn = is_valid_knight_move if piece_type == "N" else is_valid_rook_move
                        # Pawn 的 en passant 不影響 N/R
                        if fn(self.board, r, c, row, col, is_white):
                            ambiguous = True
                            break
                if ambiguous:
                    break
```
```
if piece.upper() == 'P':
            # 兵的記譜
            if is_capture:
                # 吃子：來源檔 + x + 目標
                move_notation = f"{from_file}x{to_file}{to_rank}"
            else:
                # 非吃子：直接目標
                move_notation = f"{to_file}{to_rank}"
        else:
            # 其它棋子：字母 + (x?) + 目標
            piece_notation = piece.upper()
            capture_symbol = 'x' if is_capture else ''
            move_notation = f"{piece_notation}{capture_symbol}{to_file}{to_rank}"
```
##### 並且將 log_move 改成接受 ambiguous 參數
```
 def log_move(self, piece, from_row, from_col, to_row, to_col, is_capture=False, ambiguous=False):
        from_file = chr(ord('a') + from_col)
        to_file = chr(ord('a') + to_col)
        to_rank = str(8 - to_row)

        # 兵的記譜
        if piece.upper() == 'P':
            if is_capture:
                move_notation = f"{from_file}x{to_file}{to_rank}"
            else:
                move_notation = f"{to_file}{to_rank}"
        else:
            cap = 'x' if is_capture else ''
            if ambiguous:
                # ambiguous
                move_notation = f"{piece.upper()}{from_file}{cap}{to_file}{to_rank}"
            else:
                # 正常
                move_notation = f"{piece.upper()}{cap}{to_file}{to_rank}"
```
## pawn的特殊規則: Promotion(升變)
**什麼是升變（Promotion）？**
當一個兵成功走到棋盤最底端的一列（白方是第8排，黑方是第1排），該兵就可以立即被升變為其他棋子，除了國王以外。

**可以升變成什麼棋子？**
除了國王都可以變，大多數情況都是變成queen，少數情況才會選擇變成其他piece，這種情況稱為 "Underpromotion"，不能選擇「不升變」。

### 一、在```on_click()```中檢查升變時機
在「執行移動」並更新棋盤後，呼叫 promotion_dialog，並依玩家選擇把兵升變成所選棋子。
```
# === 執行移動後 ===
self.board[row][col] = piece_to_move
self.board[from_row][from_col] = ""
self.selected = None

# —— 新增：若兵到達底線，彈出升變選單 —— 
if piece_type == "P" and (row == 0 or row == 7):
    promoted = self.promotion_dialog(is_white)
    # 將該格的"P"或"p"換成選擇的大寫（白）或小寫（黑）
    self.board[row][col] = promoted if is_white else promoted.lower()

# 記錄棋譜
self.log_move(piece_to_move, from_row, from_col, row, col, is_capture)
```
### 二、實作 promotion_dialog
用 tk.simpledialog 讓玩家選擇升變棋子。
```
import tkinter.simpledialog as sd

class ChessGUI:
    # … 其餘程式 …

    def promotion_dialog(self, is_white):
        """
        當 Pawn 升變時呼叫，傳回升變後的棋子大寫字母：Q, R, B, N
        """
        choices = ['Q', 'R', 'B', 'N']
        prompt = "Choose promotion piece: Q (Queen), R (Rook), B (Bishop), N (Knight)"
        while True:
            res = sd.askstring("Promotion", prompt)
            if res and res.upper() in choices:
                return res.upper()
            # 持續詢問直到輸入合法
```
### 三、在 log_move 中標記升變
```
def log_move(self, piece, from_row, from_col, to_row, to_col, is_capture=False, ambiguous=False):
    # … 原有代數記譜邏輯 …

    # 如果剛才是升變，board[to_row][to_col] 現在是新的棋子
    new_piece = self.board[to_row][to_col].upper()
    if piece.upper() == 'P' and new_piece in ('Q','R','B','N'):
        # 加上 =Q 等
        move_notation += f"={new_piece}"
```
###### Result:
![image](https://hackmd.io/_uploads/SJpufE8Xlx.png =80%x)
執行升變時，詢問玩家。
![image](https://hackmd.io/_uploads/B1jpMEU7lx.png =80%x)


## Castling 
Castling，中文稱王車易位或是入堡是chess中一個非常獨特且重要的特殊走法。這是唯一一次可以讓兩個棋子（國王和城堡/車）在同一回合移動的規則。
Castling 的目的：
- 保護國王（把國王移到比較安全的位置）
- 讓車參與戰局（把車從角落移出來）

Castling 怎麼做？
王車易位有兩種方向：
- 王側易位（Kingside Castling）：

        國王從 e1 → g1（白方）或 e8 → g8（黑方）
        車從 h1 → f1（白方）或 h8 → f8（黑方）

- 后側易位（Queenside Castling）：

        國王從 e1 → c1（白方）或 e8 → c8（黑方）
        車從 a1 → d1（白方）或 a8 → d8（黑方）

⚠️ 無論哪一側，國王總是移動兩格，車跳過國王並站在緊鄰的位置。

Castling 的條件（四大限制）
國王和車要符合以下條件才能進行王車易位：
- 國王與車都還沒移動過（全局只能用一次）。
- 國王路徑中間沒有任何棋子。
- 國王不在被將軍（check）狀態下。
- 國王不能經過或停在被攻擊的格子。

棋譜記錄：
short-castle(短易位)記錄為 "O-O"
long-castle(長易位)記錄為 "O-O-O"

### 在```__init__```加入旗標
```
class ChessGUI:
    def __init__(self, root):
        # … 既有程式 …

        # 加入旗標：追蹤白/黑國王與左右 Rook 是否已移動
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False  # a1
        self.white_rook_h_moved = False  # h1
        self.black_rook_a_moved = False  # a8
        self.black_rook_h_moved = False  # h8

        # … 繼續其它初始化 …
```
### on_click() 中新增易位檢測（在合法性檢查前）
```
        # 判斷是否嘗試王車易位：King 走兩格
        if piece_type == "K" and from_row in (0,7) and row == from_row and abs(col - from_col) == 2:
            # 決定是短易位還是長易位
            kingside = (col - from_col) == 2
            # 取得對方 Rook 的初始位置、移動後位置
            if from_row == 7:  # 白方
                king_moved = self.white_king_moved
                rook_a_moved = self.white_rook_a_moved
                rook_h_moved = self.white_rook_h_moved
            else:  # 黑方
                king_moved = self.black_king_moved
                rook_a_moved = self.black_rook_a_moved
                rook_h_moved = self.black_rook_h_moved

            # 如果國王或對應 Rook 已移動過，不能易位
            if king_moved:
                valid = False
            else:
                if kingside:
                    # short castle: 檢查 h 檔 rook 及 f,g 檔空
                    rook_col, new_rook_col = COLS-1, from_col+1
                    if (not rook_h_moved
                        and self.board[from_row][rook_col].upper()=="R"
                        and self.board[from_row][from_col+1]=="" 
                        and self.board[from_row][from_col+2]=="" ):
                        valid = True
                    else:
                        valid = False
                else:
                    # long castle: 檢查 a 檔 rook 及 b,c,d 檔空
                    rook_col, new_rook_col = 0, from_col-1
                    if (not rook_a_moved
                        and self.board[from_row][rook_col].upper()=="R"
                        and self.board[from_row][from_col-1]=="" 
                        and self.board[from_row][from_col-2]=="" 
                        and self.board[from_row][from_col-3]=="" ):
                        valid = True
                    else:
                        valid = False

            if valid:
                # 執行易位：移動 King
                self.board[row][col] = piece_to_move
                self.board[from_row][from_col] = ""
                # 移動對應 Rook
                rook_piece = self.board[from_row][rook_col]
                self.board[from_row][rook_col] = ""
                self.board[from_row][new_rook_col] = rook_piece

                # 更新 moved flags
                if from_row == 7:
                    self.white_king_moved = True
                    if kingside: self.white_rook_h_moved = True
                    else:       self.white_rook_a_moved = True
                else:
                    self.black_king_moved = True
                    if kingside: self.black_rook_h_moved = True
                    else:       self.black_rook_a_moved = True

                # 記錄棋譜
                notation = "0-0" if kingside else "0-0-0"
                self.move_log.config(state='normal')
                if self.turn == 'white':
                    self.move_count += 1
                    self.move_log.insert('end', f"{self.move_count}. {notation:<6}")
                else:
                    self.move_log.insert('end', f"{notation}\n")
                self.move_log.config(state='disabled')
                self.move_log.see('end')

                # 換回合並重繪
                self.turn = 'black' if self.turn=='white' else 'white'
                self.draw_board()
                self.selected = None
            else:
                print("Invalid castling")
                self.selected = None
            return
```
### 更新一般移動後的旗標
```
# 執行一般移動後
self.board[row][col] = piece_to_move
self.board[from_row][from_col] = ""
# 若移動的是 King
if piece_type=="K":
    if is_white: self.white_king_moved = True
    else:        self.black_king_moved = True
# 若移動的是 Rook，更新對應旗標
elif piece_type=="R":
    if is_white:
        if from_row==7 and from_col==0: self.white_rook_a_moved = True
        if from_row==7 and from_col==7: self.white_rook_h_moved = True
    else:
        if from_row==0 and from_col==0: self.black_rook_a_moved = True
        if from_row==0 and from_col==7: self.black_rook_h_moved = True

self.selected = None
```
### Castling 的記譜
```
def record_castle(self, notation):
    """
    記錄castling移動，使用與log_move相同的格式
    """
    num_width, move_width = 3, 8
    self.move_log.config(state='normal')
    if self.turn == 'white':
        self.move_count += 1
        text = f"{self.move_count:>{num_width}}. {notation:<{move_width}}"
    else:
        text = f"{notation}\n"
    self.move_log.insert('end', text)
    self.move_log.config(state='disabled')
    self.move_log.see('end')
```
###### Result:
![image](https://hackmd.io/_uploads/BykUjfIQll.png =80%x)
白方進行short-catle，黑方進行long-castle。

## 檢查「check」與「checkmate」狀態
**什麼是 Check（將軍）？**
Check 意指：
有敵方的棋子正在威脅吃掉你的國王。
當你處於「被將軍」狀態時，你必須在下一步解除這個威脅，否則你就會被將死。
**解決 Check 的三種方法：**
- 移動國王到安全格子（不被攻擊）。
- 用其他棋子擋住攻擊路線（限於直線攻擊，如車、主教、皇后）。
- 吃掉發動攻擊的敵棋子（如果可以吃掉）。

**什麼是 Checkmate（將死）？**
當你的國王被將軍，而且沒有任何方法可以脫離危險，遊戲就結束了，你輸了。
###  實作```is_in_check```
```
def is_in_check(self, is_white):
    """
    回傳 True 表示「is_white」方的國王目前被將軍。
    """
    # 1. 找到該方國王的位置
    king_symbol = 'K' if is_white else 'k'
    king_pos = None
    for r in range(ROWS):
        for c in range(COLS):
            if self.board[r][c] == king_symbol:
                king_pos = (r, c)
                break
        if king_pos:
            break

    # 如果找不到國王（理論上不會發生），我們不當作將軍
    if not king_pos:
        return False
    kr, kc = king_pos

    # 2. 掃描對方所有棋子，看是否能走到國王格
    for r in range(ROWS):
        for c in range(COLS):
            p = self.board[r][c]
            if p and self.is_enemy_piece(p, is_white):
                pt = p.upper()
                # 根據 p 類型呼叫相應的合法走法函式
                if   pt == 'P' and is_valid_pawn_move(self.board, r, c, kr, kc, not is_white, self.en_passant_target):
                    return True
                elif pt == 'N' and is_valid_knight_move(self.board, r, c, kr, kc, not is_white):
                    return True
                elif pt == 'B' and is_valid_bishop_move(self.board, r, c, kr, kc, not is_white):
                    return True
                elif pt == 'R' and is_valid_rook_move(self.board, r, c, kr, kc, not is_white):
                    return True
                elif pt == 'Q' and is_valid_queen_move(self.board, r, c, kr, kc, not is_white):
                    return True
                elif pt == 'K' and is_valid_king_move(self.board, r, c, kr, kc, not is_white):
                    # 注意：王對王直攻問題，可視情況略過或保留
                    return True
    return False
```
### 實作 is_checkmate
```
def is_checkmate(self, is_white):
    """
    回傳 True 表示「is_white」方已經將死。
    """
    # 1. 如果沒有被將軍，不是將死
    if not self.is_in_check(is_white):
        return False

    # 2. 掃描該方所有棋子，模擬所有合法移動，看看是否能逃脫將軍
    for r in range(ROWS):
        for c in range(COLS):
            p = self.board[r][c]
            if p and ((is_white and p.isupper()) or (not is_white and p.islower())):
                # 該棋子能走的所有格子
                for tr in range(ROWS):
                    for tc in range(COLS):
                        # 跳過原地
                        if (r, c) == (tr, tc):
                            continue
                        # 檢查該走法是否合法
                        pt = p.upper()
                        valid = False
                        if   pt == 'P':
                            valid = is_valid_pawn_move(self.board, r, c, tr, tc, is_white, self.en_passant_target)
                        elif pt == 'N':
                            valid = is_valid_knight_move(self.board, r, c, tr, tc, is_white)
                        elif pt == 'B':
                            valid = is_valid_bishop_move(self.board, r, c, tr, tc, is_white)
                        elif pt == 'R':
                            valid = is_valid_rook_move(self.board, r, c, tr, tc, is_white)
                        elif pt == 'Q':
                            valid = is_valid_queen_move(self.board, r, c, tr, tc, is_white)
                        elif pt == 'K':
                            valid = is_valid_king_move(self.board, r, c, tr, tc, is_white)
                        if not valid:
                            continue

                        # 模擬走子
                        orig_from, orig_to = self.board[r][c], self.board[tr][tc]
                        self.board[tr][tc] = self.board[r][c]
                        self.board[r][c] = ''
                        # 檢查模擬後是否仍在將軍
                        in_check = self.is_in_check(is_white)
                        # 還原
                        self.board[r][c], self.board[tr][tc] = orig_from, orig_to

                        if not in_check:
                            # 找到一個能破解將軍的走法，就不是將死
                            return False
    # 所有走法都無法破解，則將死
    return True
```
### 在移動後呼叫並提示用來判斷並跳出對話框提醒
```
if in_checkmate:
            sd.showinfo("Checkmate", f"{'白方' if opponent_is_white else '黑方'}國王被將死！遊戲結束。")
```
###### Result:
![image](https://hackmd.io/_uploads/BJdHb7Imgl.png =80%x)
將殺時跳出結束提醒。

## 和局
和局的情況（六種常見）
1. 雙方協議和局（Draw by Agreement）
兩位玩家都同意結束比賽，判定平手。
在比賽中通常透過提議：「你要和嗎？（Draw?）」
2. 逼和：無子可動（Stalemate）
一方不是被將軍，但無法合法走任何一步。
這是一種被動平手，即使你佔優也無法取勝。
例子：
黑方只有國王，白方逼得黑王無處可走又沒被將軍 → 和局！
3. 三次重複局面（Threefold Repetition）
若同一局面重複出現三次（不必連續），且：
所有棋子的移動權限相同（王可不被將軍走到同樣格子）。
任一方都可以向裁判請求和局。
4. 五十步規則（Fifty-Move Rule）
連續50回合都沒有任何吃子或兵移動，即可申請和局。
這是防止無意義拖延的規則。
5. 無法將死對手（Insufficient Material）
如果雙方都無法用手上棋子將死對手，自動和局。
    常見情況：
    只剩 王 vs 王
    王 + 主教 vs 王
    王 + 騎士 vs 王
    王 + 主教 vs 王 + 主教（同色）

本次未實作1、5

### Stalemate:
#### 定義is_stalemate
```
def is_stalemate(self, is_white):
    """
    回傳 True 表示「is_white」方此時雖不在將軍，
    但已經沒有任何合法走法──和棋。
    """
    # 1. 如果還在將軍，就不是和棋
    if self.is_in_check(is_white):
        return False

    # 2. 掃描所有同色棋子，看是否至少有一個合法走法
    for r in range(ROWS):
        for c in range(COLS):
            p = self.board[r][c]
            if not p:
                continue
            if is_white and not p.isupper():
                continue
            if not is_white and not p.islower():
                continue

            # 計算這個棋子的合法走法
            moves = self.compute_legal_moves(r, c)
            # 如果至少有一個走法，還能繼續下，非和棋
            if moves:
                # 為了更嚴謹，也要模擬走子後確保不會進入將軍
                for tr, tc in moves:
                    orig_from, orig_to = self.board[r][c], self.board[tr][tc]
                    self.board[tr][tc] = self.board[r][c]
                    self.board[r][c] = ''
                    still_in_check = self.is_in_check(is_white)
                    # 還原
                    self.board[r][c], self.board[tr][tc] = orig_from, orig_to
                    if not still_in_check:
                        return False
    # 沒有任何可以走且不會將軍的走法 → 和棋
    return True
```
#### 在移動後檢查並提示(on_click() 中、draw_board() 之後)
```
# 假設這裡 turn 已經換到下一位玩家
opponent_is_white = (self.turn == 'white')

# 1. 檢查將軍
if self.is_in_check(opponent_is_white):
    mb.showinfo("Check", f"{'白方' if opponent_is_white else '黑方'}國王被將軍！")
    # 再檢查將死
    if self.is_checkmate(opponent_is_white):
        mb.showinfo("Checkmate", f"{'白方' if opponent_is_white else '黑方'}國王被將死！遊戲結束。")
        return

# 2. 若不在將軍，檢查是否和棋
else:
    if self.is_stalemate(opponent_is_white):
        mb.showinfo("Stalemate", f"{'白方' if opponent_is_white else '黑方'}無路可走，和棋！")
        # 遊戲結束處理
        return

```
###### Result:
![image](https://hackmd.io/_uploads/ByNau7UXlx.png =80%x)
無子可走時，跳出和棋提醒。

### Fifty-Move Rule
#### 新增 50 步規則計數器
```
self.halfmove_clock = 0  # 自上次吃子或兵移動以來的半步數
```
#### 定義is_fifty_move_rule
```
def is_fifty_move_rule(self):
    """
    檢查是否達到50步規則（100半步）
    """
    return self.half_move_clock >= 100
```
#### Castling 視為+1
```
# on_click()裡
if self.can_castle(kingside, is_white):
    if self.perform_castle(kingside, is_white):
        self.selected = None
        # Castling 不重置 50 步計數器（因為沒有吃子或兵移動）
        self.half_move_clock += 1
        # 換回合
        self.turn = 'black' if self.turn == 'white' else 'white'
        print(f"Castling performed. Turn: {self.turn}")
        # 重繪棋盤
        self.draw_board()
        return
```
#### 更新 50 步規則計數器
```
# on_click()裡
if piece_type == "P" or is_capture:
    # 兵移動或吃子，重置計數器
    self.half_move_clock = 0
else:
    # 其他移動，增加計數器
    self.half_move_clock += 1
```
###### Result:
![image](https://hackmd.io/_uploads/ryAMjmIQxe.png =80%x)
連續50回合都沒有任何吃子或兵移動，跳出和棋提醒。

### Threefold Repetition
#### 追蹤歷史局面
在```ChessGUI.__init__```中，新增一個屬性來記錄每一次移動完之後的局面表示：
```
class ChessGUI:
    def __init__(self, tk_root):
        # … 既有初始化程式 …
        # 加一行：
        self.position_history = []
        # 在一開始（初始棋局）也要加進去：
        self.record_current_position()

```
```
def record_current_position(self):
    """
    將目前棋盤、執行權、castling 權、en passant 目標等資訊
    轉成一個字串，並 append 到 position_history。
    為簡化，只取棋子位置＋回合＋castling＋en passant。
    """
    # 1. 棋子佈局：用「每列 8 個字元」的字串 + '/' 分隔
    rows = []
    for r in self.board:
        row_s = ''.join(piece if piece else '.' for piece in r)
        rows.append(row_s)
    board_part = '/'.join(rows)
    # 2. 執行權：w 或 b
    turn_part = 'w' if self.turn == 'white' else 'b'
    # 3. castling 權：KQkq 或 '-'
    rights = ''
    if not self.white_king_moved:
        if not self.white_rook_h_moved: rights += 'K'
        if not self.white_rook_a_moved: rights += 'Q'
    if not self.black_king_moved:
        if not self.black_rook_h_moved: rights += 'k'
        if not self.black_rook_a_moved: rights += 'q'
    castle_part = rights if rights else '-'
    # 4. en passant 目標：座標 or '-'
    if self.en_passant_target:
        ep = self.en_passant_target
        file = chr(ord('a') + ep[1])
        rank = str(8 - ep[0])
        ep_part = file + rank
    else:
        ep_part = '-'

    pos_str = f"{board_part} {turn_part} {castle_part} {ep_part}"
    self.position_history.append(pos_str)
```
#### 判斷三重重複
新增一個方法，每次走子後呼叫，去計算 position_history 中，最後一個局面字串出現的次數:
```
def is_threefold_repetition(self):
    """
    若最後一個局面已經至少出現 3 次，回傳 True。
    """
    if not self.position_history:
        return False
    last = self.position_history[-1]
    # count occurrences
    return self.position_history.count(last) >= 3
```
#### 加入和棋提示
```
 if self.is_stalemate(opponent_is_white):
            mb.showinfo("Stalemate", "無路可走，和棋！")
            return
```
###### Result:
![image](https://hackmd.io/_uploads/HJZe6XImxl.png =80%x)
三次重複局面後，跳出和棋提醒。

## 以上就是本次我們期末專案的內容了，目前已經建立好基本且完整的規則，且可以實踐再同一台電腦對戰其實還有一些目標礙於時間不足沒有達成，未來有機會的話我會把它寫完，可以經由以下連接查看:[連結](https://hackmd.io/@bTirselxR2aOr7nVJhqHqg/HyYYuXqMge)

因為後來做了很多東西，使得```main.py```非常的亂，不要鞭我了，之後會做優化，將內容拆開整理，但目前就將就著看吧(；´ﾟωﾟ｀人)
#### ```main.py```
```
import tkinter as tk
import tkinter.simpledialog as sd
from tkinter import messagebox as mb
from board import pieces, starting_board
from pieces import (
    is_valid_knight_move,
    is_valid_bishop_move,
    is_valid_pawn_move,
    is_valid_queen_move,
    is_valid_rook_move,
    is_valid_king_move
)

# 棋盤參數
ROWS, COLS = 8, 8
TILE_SIZE = 80
OFFSET = 20  # 在繪製棋盤時，讓畫布向右下偏移 20px，留出座標標籤空間


class ChessGUI:
    def __init__(self, tk_root):
        self.root = tk_root
        self.root.title("Chess game")

        # 紀錄可以被 en passant 吃掉的目標格 (row, col)，若無則為 None
        self.en_passant_target = None

        # 初始化棋盤狀態
        self.board = [row[:] for row in starting_board()]
        self.turn = 'white'  # 白方先下
        self.selected = None  # 當前被選中的棋子座標 (row, col)
        self.move_count = 0  # 記錄回合數（每白方移動一次 +1）

        # 加入旗標：追蹤白/黑國王與左右 Rook 是否已移動
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False  # a1
        self.white_rook_h_moved = False  # h1
        self.black_rook_a_moved = False  # a8
        self.black_rook_h_moved = False  # h8

        # 建立主框架：左側為棋盤，右側為棋譜區
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # 左側：棋盤 Canvas（淨畫布大小 = 8 格 * TILE_SIZE）
        self.canvas = tk.Canvas(
            frame,
            width=COLS * TILE_SIZE + OFFSET,
            height=ROWS * TILE_SIZE + OFFSET + 30
        )
        self.canvas.grid(row=0, column=0)

        # 右側：棋譜區（Text widget）
        self.move_log = tk.Text(
            frame,
            width=30,
            height=35,
            state='disabled',
            font=("Consolas", 12)
        )
        self.move_log.grid(row=0, column=1, padx=10, sticky='n')

        # 綁定滑鼠左鍵：點擊棋盤後觸發 on_click()
        self.canvas.bind("<Button-1>", self.on_click)

        # 首次繪製棋盤
        self.draw_board()

        # 被選中後的合法走法列表
        self.legal_moves = []

        # 50 步規則計數器
        self.half_move_clock = 0  # 自上次吃子或兵移動以來的半步數

        # 加一行：
        self.position_history = []
        # 在一開始（初始棋局）也要加進去：
        self.record_current_position()

    def record_current_position(self):
        """
        將目前棋盤、執行權、castling 權、en passant 目標等資訊
        轉成一個字串，並 append 到 position_history。
        為簡化，只取棋子位置＋回合＋castling＋en passant。
        """
        # 1. 棋子佈局：用「每列 8 個字元」的字串 + '/' 分隔
        rows = []
        for r in self.board:
            row_s = ''.join(piece if piece else '.' for piece in r)
            rows.append(row_s)
        board_part = '/'.join(rows)
        # 2. 執行權：w 或 b
        turn_part = 'w' if self.turn == 'white' else 'b'
        # 3. castling 權：KQkq 或 '-'
        rights = ''
        if not self.white_king_moved:
            if not self.white_rook_h_moved: rights += 'K'
            if not self.white_rook_a_moved: rights += 'Q'
        if not self.black_king_moved:
            if not self.black_rook_h_moved: rights += 'k'
            if not self.black_rook_a_moved: rights += 'q'
        castle_part = rights if rights else '-'
        # 4. en passant 目標：座標 or '-'
        if self.en_passant_target:
            ep = self.en_passant_target
            file = chr(ord('a') + ep[1])
            rank = str(8 - ep[0])
            ep_part = file + rank
        else:
            ep_part = '-'

        pos_str = f"{board_part} {turn_part} {castle_part} {ep_part}"
        self.position_history.append(pos_str)

    def is_threefold_repetition(self):
        """
        若最後一個局面已經至少出現 3 次，回傳 True。
        """
        if not self.position_history:
            return False
        last = self.position_history[-1]
        # count occurrences
        return self.position_history.count(last) >= 3

    def draw_board(self):
        """
        在 Canvas 上繪製棋盤格、座標標籤，以及當前所有棋子。
        """
        self.canvas.delete("all")
        # 先畫棋格與棋子，再畫座標標籤
        for r in range(ROWS):
            for c in range(COLS):
                # 計算這個格子的左上與右下座標 (加上 OFFSET)
                x1 = c * TILE_SIZE + OFFSET
                y1 = r * TILE_SIZE + OFFSET
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE

                # 棋格顏色
                color = "#FFFFFF" if (r + c) % 2 == 0 else "#9370BE"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                # 如果此格有棋子，就畫出它
                piece = self.board[r][c]
                if piece:
                    self.canvas.create_text(
                        x1 + TILE_SIZE // 2,
                        y1 + TILE_SIZE // 2,
                        text=pieces[piece],
                        font=("Arial", 32)
                    )

        # 繪製橫向座標 a~h（在棋格下方）
        for c in range(COLS):
            x = c * TILE_SIZE + OFFSET + TILE_SIZE // 2
            y = ROWS * TILE_SIZE + OFFSET + 10  # 在棋格下方多 10px
            file_label = chr(ord('a') + c)
            self.canvas.create_text(x, y, text=file_label, font=("Arial", 12))

        # 繪製直向座標 8~1（在棋格左側）
        for r in range(ROWS):
            x = OFFSET - 10  # 在棋格左側多 10px
            y = r * TILE_SIZE + OFFSET + TILE_SIZE // 2
            rank_label = str(8 - r)
            self.canvas.create_text(x, y, text=rank_label, font=("Arial", 12))

    def is_own_piece(self, piece):
        """
        判斷傳入的 piece 是否屬於當前玩家 self.turn。
        白方棋子為大寫，黑方棋子為小寫。
        """
        if self.turn == 'white':
            return piece.isupper()
        else:
            return piece.islower()

    def get_all_legal_moves(self, is_white):
        """
        獲取指定顏色所有合法移動
        """
        legal_moves = []

        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if not piece:
                    continue

                # 檢查是否為該方的棋子
                if (is_white and piece.islower()) or (not is_white and piece.isupper()):
                    continue

                # 檢查所有可能的目標位置
                for tr in range(ROWS):
                    for tc in range(COLS):
                        # 跳過原地
                        if (r, c) == (tr, tc):
                            continue

                        # 檢查該移動是否基本合法
                        if not self.is_valid_move(r, c, tr, tc, is_white):
                            continue

                        # 檢查移動後是否會讓自己國王陷入將軍
                        if self.will_be_in_check_after_move(r, c, tr, tc, is_white):
                            continue

                        legal_moves.append(((r, c), (tr, tc)))

        return legal_moves

    def is_enemy_piece(self, piece, is_white):
        """
        判斷傳入的 piece 是否為敵方棋子
        """
        if is_white:
            return piece.islower()  # 白方看黑方為敵方
        else:
            return piece.isupper()  # 黑方看白方為敵方

    def promotion_dialog(self, is_white):
        """
        當 Pawn 升變時呼叫，傳回升變後的棋子大寫字母：Q, R, B, N
        """
        choices = ['Q', 'R', 'B', 'N']
        prompt = "Choose promotion piece: Q (Queen), R (Rook), B (Bishop), N (Knight)"
        while True:
            res = sd.askstring("Promotion", prompt)
            if res and res.upper() in choices:
                return res.upper()
            # 持續詢問直到輸入合法

    def record_castle(self, notation):
        """
        記錄castling移動，使用與log_move相同的格式
        """
        num_width, move_width = 3, 8
        self.move_log.config(state='normal')
        if self.turn == 'white':
            self.move_count += 1
            text = f"{self.move_count:>{num_width}}. {notation:<{move_width}}"
        else:
            text = f"{notation}\n"
        self.move_log.insert('end', text)
        self.move_log.config(state='disabled')
        self.move_log.see('end')

    def can_castle(self, kingside, is_white):
        """
        檢查是否可以進行 castling
        """
        if is_white:
            king_row = 7
            king_moved = self.white_king_moved
            rook_moved = self.white_rook_h_moved if kingside else self.white_rook_a_moved
        else:
            king_row = 0
            king_moved = self.black_king_moved
            rook_moved = self.black_rook_h_moved if kingside else self.black_rook_a_moved

        # 國王或城堡已移動
        if king_moved or rook_moved:
            return False

        # 檢查路徑是否清空
        if kingside:
            # 短易位：檢查 f 和 g 格
            return self.board[king_row][5] == "" and self.board[king_row][6] == ""
        else:
            # 長易位：檢查 b, c, d 格
            return (self.board[king_row][1] == "" and
                    self.board[king_row][2] == "" and
                    self.board[king_row][3] == "")

    def perform_castle(self, kingside, is_white):
        """
        執行 castling 移動
        """
        if is_white:
            king_row = 7
            king_col = 4
        else:
            king_row = 0
            king_col = 4

        if kingside:
            # 短易位
            new_king_col = 6
            rook_col = 7
            new_rook_col = 5
            notation = "O-O"
        else:
            # 長易位
            new_king_col = 2
            rook_col = 0
            new_rook_col = 3
            notation = "O-O-O"

        # 移動國王
        king_piece = self.board[king_row][king_col]
        self.board[king_row][new_king_col] = king_piece
        self.board[king_row][king_col] = ""

        # 移動城堡
        rook_piece = self.board[king_row][rook_col]
        self.board[king_row][new_rook_col] = rook_piece
        self.board[king_row][rook_col] = ""

        # 標記國王已移動
        if is_white:
            self.white_king_moved = True
        else:
            self.black_king_moved = True

        # 記錄棋譜
        self.record_castle(notation)

        return True

    def is_in_check(self, is_white):
        """
        回傳 True 表示「is_white」方的國王目前被將軍。
        """
        # 1. 找到該方國王的位置
        king_symbol = 'K' if is_white else 'k'
        king_pos = None
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c] == king_symbol:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        # 如果找不到國王（理論上不會發生），我們不當作將軍
        if not king_pos:
            return False
        kr, kc = king_pos

        # 2. 掃描對方所有棋子，看是否能走到國王格
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p and self.is_enemy_piece(p, is_white):
                    pt = p.upper()
                    # 根據 p 類型呼叫相應的合法走法函式
                    # 注意：這裡要傳入攻擊方的顏色
                    attacking_is_white = p.isupper()
                    if pt == 'P' and is_valid_pawn_move(self.board, r, c, kr, kc, attacking_is_white,
                                                        self.en_passant_target):
                        return True
                    elif pt == 'N' and is_valid_knight_move(self.board, r, c, kr, kc, attacking_is_white):
                        return True
                    elif pt == 'B' and is_valid_bishop_move(self.board, r, c, kr, kc, attacking_is_white):
                        return True
                    elif pt == 'R' and is_valid_rook_move(self.board, r, c, kr, kc, attacking_is_white):
                        return True
                    elif pt == 'Q' and is_valid_queen_move(self.board, r, c, kr, kc, attacking_is_white):
                        return True
                    elif pt == 'K' and is_valid_king_move(self.board, r, c, kr, kc, attacking_is_white):
                        return True
        return False

    def is_valid_move(self, from_r, from_c, to_r, to_c, is_white):
        """
        檢查一個移動是否合法（不包含會讓自己國王被將軍的情況）
        """
        piece = self.board[from_r][from_c]
        if not piece:
            return False

        # 這行幫助 IDE 理解 piece 的類型（可選）
        assert isinstance(piece, str), f"Expected string, got {type(piece)}"

        # 確保棋子顏色正確
        if (is_white and piece.islower()) or (not is_white and piece.isupper()):
            return False

        piece_type = piece.upper()

        # 檢查基本移動合法性
        if piece_type == 'P':
            return is_valid_pawn_move(self.board, from_r, from_c, to_r, to_c, is_white, self.en_passant_target)
        elif piece_type == 'N':
            return is_valid_knight_move(self.board, from_r, from_c, to_r, to_c, is_white)
        elif piece_type == 'B':
            return is_valid_bishop_move(self.board, from_r, from_c, to_r, to_c, is_white)
        elif piece_type == 'R':
            return is_valid_rook_move(self.board, from_r, from_c, to_r, to_c, is_white)
        elif piece_type == 'Q':
            return is_valid_queen_move(self.board, from_r, from_c, to_r, to_c, is_white)
        elif piece_type == 'K':
            return is_valid_king_move(self.board, from_r, from_c, to_r, to_c, is_white)
        return False

    def is_checkmate(self, is_white):
        """
        回傳 True 表示「is_white」方已經將死。
        """
        # 1. 如果沒有被將軍，不是將死
        if not self.is_in_check(is_white):
            return False

        # 2. 掃描該方所有棋子，模擬所有合法移動，看看是否能逃脫將軍
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                # 檢查是否為該方的棋子
                if p and ((is_white and p.isupper()) or (not is_white and p.islower())):
                    # 該棋子能走的所有格子
                    for tr in range(ROWS):
                        for tc in range(COLS):
                            # 跳過原地
                            if (r, c) == (tr, tc):
                                continue

                            # 檢查該走法是否合法
                            if not self.is_valid_move(r, c, tr, tc, is_white):
                                continue

                            # 模擬走子
                            orig_from, orig_to = self.board[r][c], self.board[tr][tc]
                            self.board[tr][tc] = self.board[r][c]
                            self.board[r][c] = ''

                            # 檢查模擬後是否仍在將軍
                            in_check = self.is_in_check(is_white)

                            # 還原
                            self.board[r][c], self.board[tr][tc] = orig_from, orig_to

                            if not in_check:
                                # 找到一個能破解將軍的走法，就不是將死
                                return False

        # 所有走法都無法破解，則將死
        return True

    def will_be_in_check_after_move(self, from_r, from_c, to_r, to_c, is_white):
        """
        檢查移動後是否會讓自己國王陷入將軍
        """
        # 模擬移動
        orig_from = self.board[from_r][from_c]
        orig_to = self.board[to_r][to_c]

        self.board[to_r][to_c] = orig_from
        self.board[from_r][from_c] = ""

        # 檢查是否被將軍
        in_check = self.is_in_check(is_white)

        # 還原棋盤
        self.board[from_r][from_c] = orig_from
        self.board[to_r][to_c] = orig_to

        return in_check

    def is_stalemate(self, is_white):
        """
        回傳 True 表示「is_white」方此時雖不在將軍，
        但已經沒有任何合法走法──和棋。
        """
        # 1. 如果還在將軍，就不是和棋
        if self.is_in_check(is_white):
            return False

        # 2. 檢查是否有任何合法移動
        legal_moves = self.get_all_legal_moves(is_white)
        return len(legal_moves) == 0

    def is_fifty_move_rule(self):
        """
        檢查是否達到50步規則（100半步）
        """
        return self.half_move_clock >= 100


    def on_click(self, event):
        """
        處理滑鼠左鍵點擊事件：選棋子、移動棋子、檢查合法性、更新棋譜、重繪棋盤。
        """
        # 把畫布座標換算回棋盤行列
        x_click = event.x
        y_click = event.y

        # 如果點擊在 OFFSET 之外才可能是有效棋盤區域
        if x_click < OFFSET or y_click < OFFSET:
            return

        col = (x_click - OFFSET) // TILE_SIZE
        row = (y_click - OFFSET) // TILE_SIZE

        # 如果點擊位置不在 0<=row<8, 0<=col<8 範圍，忽略
        if not (0 <= row < ROWS and 0 <= col < COLS):
            return

        clicked_piece = self.board[row][col]

        # Step1：如果尚未選取棋子 (self.selected is None)
        if self.selected is None:
            # 只能點到「自己」的棋子才算有效選取
            if clicked_piece and self.is_own_piece(clicked_piece):
                self.selected = (row, col)
            return

        # Step2：已選取過棋子，現在要嘗試移動
        from_row, from_col = self.selected
        piece_to_move = self.board[from_row][from_col]

        # 如果目標格有自己人棋子，就重新選取
        if clicked_piece and self.is_own_piece(clicked_piece):
            self.selected = (row, col)
            return

        # 移動前先檢查「合法性」
        is_white = piece_to_move.isupper()
        piece_type = piece_to_move.upper()

        # 檢查是否為 Castling 移動
        if (piece_type == "K" and from_row == row and
                from_col == 4 and abs(col - from_col) == 2):

            kingside = (col > from_col)  # 如果目標列大於起始列，則為短易位

            if self.can_castle(kingside, is_white):
                if self.perform_castle(kingside, is_white):
                    self.selected = None
                    # Castling 不重置 50 步計數器（因為沒有吃子或兵移動）
                    self.half_move_clock += 1
                    # 換回合
                    self.turn = 'black' if self.turn == 'white' else 'white'
                    print(f"Castling performed. Turn: {self.turn}")
                    # 重繪棋盤
                    self.draw_board()
                    return
            else:
                print("Invalid castling move")
                self.selected = None
                return

        # 一般移動檢查
        valid = False
        if piece_type == "P":
            valid = is_valid_pawn_move(self.board, from_row, from_col, row, col, is_white, self.en_passant_target)
        elif piece_type == "N":
            valid = is_valid_knight_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "R":
            valid = is_valid_rook_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "B":
            valid = is_valid_bishop_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "Q":
            valid = is_valid_queen_move(self.board, from_row, from_col, row, col, is_white)
        elif piece_type == "K":
            valid = is_valid_king_move(self.board, from_row, from_col, row, col, is_white)

        if not valid:
            print(f"Invalid {piece_type} move")
            self.selected = None
            return

        # 檢查移動後是否會讓自己國王陷入將軍
        if self.will_be_in_check_after_move(from_row, from_col, row, col, is_white):
            print("Move would leave king in check")
            self.selected = None
            return

        # 檢查 Knight / Rook 歧義
        ambiguous = False
        if piece_type in ("N", "R"):
            # 掃描所有同型同色棋子能否走到 (row, col)
            for r in range(ROWS):
                for c in range(COLS):
                    if (r, c) != (from_row, from_col) and self.board[r][c].upper() == piece_type and self.is_own_piece(
                            self.board[r][c]):
                        # 其他同型棋子也能走到同一格，算作歧義
                        fn = is_valid_knight_move if piece_type == "N" else is_valid_rook_move
                        if fn(self.board, r, c, row, col, is_white):
                            # 還要檢查該移動不會讓自己國王陷入將軍
                            if not self.will_be_in_check_after_move(r, c, row, col, is_white):
                                ambiguous = True
                                break
                if ambiguous:
                    break

        # Step3：若合法才「吃或走格子」並更新棋譜
        # 判斷是否吃子：只要目標格非空且非己方
        target_piece = self.board[row][col]
        is_capture = bool(target_piece) and not self.is_own_piece(target_piece)

        # 先處理 en passant 捕獲
        if piece_type == "P" and (row, col) == self.en_passant_target and self.en_passant_target is not None:
            # 被吃掉的兵位於「from_row, to_col」的相對位置
            captured_row = from_row  # 斜行，原本兵所在地行
            captured_col = col  # 新行的欄
            # 從棋盤上移除那顆被吃的兵
            self.board[captured_row][captured_col] = ""
            is_capture = True

        # 更新 50 步規則計數器
        if piece_type == "P" or is_capture:
            # 兵移動或吃子，重置計數器
            self.half_move_clock = 0
        else:
            # 其他移動，增加計數器
            self.half_move_clock += 1

        # 更新自己兵的位置
        self.board[row][col] = piece_to_move
        self.board[from_row][from_col] = ""
        self.selected = None

        # 更新移動標記
        if piece_type == "R":
            if is_white and from_row == 7 and from_col == 0:
                self.white_rook_a_moved = True
            elif is_white and from_row == 7 and from_col == 7:
                self.white_rook_h_moved = True
            elif not is_white and from_row == 0 and from_col == 0:
                self.black_rook_a_moved = True
            elif not is_white and from_row == 0 and from_col == 7:
                self.black_rook_h_moved = True
        elif piece_type == "K":
            if is_white:
                self.white_king_moved = True
            else:
                self.black_king_moved = True

        # 若兵到達底線，彈出升變選單
        if piece_type == "P" and (row == 0 or row == 7):
            promoted = self.promotion_dialog(is_white)
            # 將該格的"P"或"p"換成選擇的大寫（白）或小寫（黑）
            self.board[row][col] = promoted if is_white else promoted.lower()

        # 最後更新 en_passant_target
        # 當此步是兵從初始位置兩格前進，才設定下一步可被過路吃的目標格
        if piece_type == "P" and abs(row - from_row) == 2:
            # 例如白方兵從 row=6 -> row=4，en passant 目標為 (5, from_col)
            self.en_passant_target = ((from_row + row) // 2, from_col)
        else:
            self.en_passant_target = None

        # 換回合
        self.turn = 'black' if self.turn == 'white' else 'white'

        # 檢查對手是否被將軍或將死
        opponent_is_white = (self.turn == 'white')
        in_check = self.is_in_check(opponent_is_white)
        in_checkmate = False

        if in_check:
            in_checkmate = self.is_checkmate(opponent_is_white)

        # 記錄棋譜 (包含 + 和 # 標記)
        self.log_move(piece_to_move, from_row, from_col, row, col, is_capture, ambiguous, in_check, in_checkmate)

        print(f"Turn: {self.turn}")

        # 1) 記錄新的局面
        self.record_current_position()

        # 重繪棋盤
        self.draw_board()

        # 顯示將死訊息
        if in_checkmate:
            mb.showinfo("Checkmate", f"{'白方' if opponent_is_white else '黑方'}國王被將死！遊戲結束。")
        else:
            if self.is_stalemate(opponent_is_white):
                mb.showinfo("Stalemate", f"{'白方' if opponent_is_white else '黑方'}無路可走，和棋！")
                return
            elif self.is_fifty_move_rule():
                mb.showinfo("Stalemate", f"{'白方' if opponent_is_white else '黑方'}50步規則：和棋！")
                return
            elif self.is_threefold_repetition():
                mb.showinfo("Stalemate", "三重重複局面：和棋！")
                return

    def log_move(self, piece, from_row, from_col, to_row, to_col, is_capture=False, ambiguous=False, in_check=False,
                 in_checkmate=False):
        from_file = chr(ord('a') + from_col)
        to_file = chr(ord('a') + to_col)
        to_rank = str(8 - to_row)

        # 兵的記譜
        if piece.upper() == 'P':
            if is_capture:
                move_notation = f"{from_file}x{to_file}{to_rank}"
            else:
                move_notation = f"{to_file}{to_rank}"
        else:
            cap = 'x' if is_capture else ''
            if ambiguous:
                # ambiguous
                move_notation = f"{piece.upper()}{from_file}{cap}{to_file}{to_rank}"
            else:
                # 正常
                move_notation = f"{piece.upper()}{cap}{to_file}{to_rank}"

        # 如果剛才是升變，board[to_row][to_col] 現在是新的棋子
        new_piece = self.board[to_row][to_col].upper()
        if piece.upper() == 'P' and new_piece in ('Q', 'R', 'B', 'N'):
            # 加上 =Q 等
            move_notation += f"={new_piece}"

        # 添加將軍和將死標記
        if in_checkmate:
            move_notation += "#"
        elif in_check:
            move_notation += "+"

        # 對齊 & 插入
        num_width, move_width = 3, 8
        self.move_log.config(state='normal')
        if self.turn == 'black':  # 剛移動完的是白方
            self.move_count += 1
            text = f"{self.move_count:>{num_width}}. {move_notation:<{move_width}}"
        else:  # 剛移動完的是黑方
            text = f"{move_notation}\n"
        self.move_log.insert('end', text)
        self.move_log.config(state='disabled')
        self.move_log.see('end')

# 主程式：建立 TK 視窗並啟動
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
```