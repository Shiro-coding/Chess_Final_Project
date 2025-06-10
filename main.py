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