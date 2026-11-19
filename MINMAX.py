import time as te
import streamlit as st
import WINCHECKER as WR

def MM(board, depth_limit: int | None, time_limit: float | None = 2.0):
    
    start_time = te.perf_counter()
    ai = st.session_state['curr_player']
    col_heights = list(st.session_state['col_heights'])

    if ai == "Y":
        opponent = "R"
    else:
        opponent = "Y"

    WC = st.session_state['WC']
    cols = len(board[0])
    col_order = sorted(range(cols), key=lambda c: abs(c - (cols - 1) / 2))

    def valid_moves(board):
        return [c for c in col_order if board[0][c] == "E"]

    weights = [0] + [10 ** (i * 2) for i in range(WC)]
    win_score = weights[WC - 1] * 1000

    def evaluate(board):
        score = 0
        rows = len(board)
        cols = len(board[0])

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(rows):
            for c in range(cols):
                for dr, dc in directions:

                    end_r = r + (WC - 1) * dr
                    end_c = c + (WC - 1) * dc

                    if 0 <= end_r < rows and 0 <= end_c < cols:
                        window = [
                            board[r + i * dr][c + i * dc]
                            for i in range(WC)
                        ]

                        ai_count = window.count(ai)
                        opp_count = window.count(opponent)

                        if opp_count == 0 and ai_count > 0:
                            score += weights[ai_count]

                        elif ai_count == 0 and opp_count > 0:
                            score -= int(weights[opp_count] * 1.2)

        return score

    class SearchTimeout(Exception):
        pass

    nodes = 0

    # Actual Minmax function
    def minmax(depth, maximizing, last_move):
        nonlocal nodes
        nodes += 1
        if time_limit is not None and (nodes & 1023) == 0 and (te.perf_counter() - start_time) >= time_limit:
            raise SearchTimeout()

        result = WR.WINCHECKn(board, last_move, WC)

        if result == ai:
            return win_score + depth, None

        if result == opponent:
            return -win_score - depth, None

        if result == 'Draw':
            return 0, None

        moves = valid_moves(board)

        if depth == 0:
            return evaluate(board), None

        if not moves:
            return 0, None

        if maximizing:
            best_score = float('-inf')
            best_col = moves[0]

            for col in moves:

                row = col_heights[col]
                board[row][col] = ai
                col_heights[col] -= 1

                score, _ = minmax(depth - 1, False, (row, col))

                board[row][col] = 'E'
                col_heights[col] += 1

                if score > best_score:
                    best_score = score
                    best_col = col

            return best_score, best_col

        else:
            best_score = float('inf')
            best_col = moves[0]

            for col in moves:

                row = col_heights[col]
                board[row][col] = opponent
                col_heights[col] -= 1

                score, _ = minmax(depth - 1, True, (row, col))

                board[row][col] = 'E'
                col_heights[col] += 1

                if score < best_score:
                    best_score = score
                    best_col = col

            return best_score, best_col

    moves = valid_moves(board)
    if not moves:
        return None

    best_col = moves[0]
    empty_cells = sum(h + 1 for h in col_heights)
    max_depth = empty_cells if (depth_limit is None or depth_limit == float('inf')) else min(int(depth_limit), empty_cells)

    for d in range(1, max_depth + 1):
        if time_limit is not None and te.perf_counter() - start_time >= time_limit:
            break
        try:
            score, col = minmax(d, True, st.session_state['prev_move'])
            if col is not None:
                best_col = col
            if score >= win_score:
                break
        except SearchTimeout:
            break

    return best_col