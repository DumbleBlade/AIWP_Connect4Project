import time as te
import streamlit as st
import WINCHECKER as WR

def IDNAB(board, depth_limit: int | None, time_limit: float | None = 2.0):
    start_time = te.perf_counter()
    ai = st.session_state['curr_player']
    WC = st.session_state['WC']

    rows = len(board)
    cols = len(board[0])
    stride = rows + WC

    col_heights = [
        max((r for r in range(rows) if board[r][c] == "E"), default=-1)
        for c in range(cols)
    ]

    r_bits, y_bits = WR.ToBitboards(board, rows, cols, WC)

    # Precompute valid windows
    valid_windows = []
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(rows):
        for c in range(cols):
            for dr, dc in directions:
                end_r = r + (WC - 1) * dr
                end_c = c + (WC - 1) * dc
                if 0 <= end_r < rows and 0 <= end_c < cols:
                    mask = 0
                    for i in range(WC):
                        rr = r + i * dr
                        cc = c + i * dc
                        mask |= 1 << (cc * stride + (rows - 1 - rr))
                    valid_windows.append(mask)

    center = cols // 2
    center_cols = [center] if cols % 2 == 1 else [center - 1, center]
    center_mask = sum(1 << (c * stride + r) for c in center_cols for r in range(rows))
    col_order = sorted(range(cols), key=lambda c: abs(c - (cols - 1) / 2))

    def valid_moves():
        return [c for c in col_order if col_heights[c] >= 0]

    weights = [0] + [10 ** (i * 2) for i in range(WC)]
    win_score = weights[WC - 1] * 1000

    def evaluate(p_bits, o_bits):
        score = ((p_bits & center_mask).bit_count() - (o_bits & center_mask).bit_count()) * 4

        for mask in valid_windows:
            p_count = (p_bits & mask).bit_count()
            o_count = (o_bits & mask).bit_count()

            if o_count == 0 and p_count > 0:
                score += weights[p_count]
            elif p_count == 0 and o_count > 0:
                score -= int(weights[o_count] * 1.2)

        return score

    class SearchTimeout(Exception):
        pass

    nodes = 0

    def negamax(depth, alpha, beta, player, r_bb, y_bb, pv_col=None):
        nonlocal nodes
        nodes += 1
        if time_limit is not None and (nodes & 1023) == 0 and (te.perf_counter() - start_time) >= time_limit:
            raise SearchTimeout()

        other = "R" if player == "Y" else "Y"

        result = WR.WINCHECKb(r_bb, y_bb, rows, cols, WC)
        if result == player:
            return win_score + depth, None
        if result == other:
            return -win_score - depth, None
        if result == 'Draw':
            return 0, None

        moves = valid_moves()
        if not moves:
            return 0, None

        if depth == 0:
            ai_bb, opp_bb = (y_bb, r_bb) if ai == "Y" else (r_bb, y_bb)
            score = evaluate(ai_bb, opp_bb)
            return (score if player == ai else -score), None

        if pv_col is not None and pv_col in moves:
            moves.remove(pv_col)
            moves.insert(0, pv_col)

        best_score = float('-inf')
        best_col = moves[0]

        for col in moves:
            row = col_heights[col]
            bit = 1 << (col * stride + (rows - 1 - row))

            col_heights[col] -= 1

            if player == "Y":
                score, _ = negamax(depth - 1, -beta, -alpha, "R", r_bb, y_bb | bit)
            else:
                score, _ = negamax(depth - 1, -beta, -alpha, "Y", r_bb | bit, y_bb)

            score = -score
            col_heights[col] += 1

            if score > best_score:
                best_score = score
                best_col = col

            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_score, best_col

    moves = valid_moves()
    
    if not moves:

        return None

    best_move = moves[0]
    empty_cells = sum(h + 1 for h in col_heights)
    max_depth = empty_cells if (depth_limit is None or depth_limit == float('inf')) else min(int(depth_limit), empty_cells)

    for d in range(1, max_depth + 1):

        if time_limit is not None and te.perf_counter() - start_time >= time_limit:

            break

        try:

            score, col = negamax(d, float('-inf'), float('inf'), ai, r_bits, y_bits, pv_col=best_move)
            
            if col is not None:

                best_move = col

            if score >= win_score:

                break

        except SearchTimeout:

            break

    return best_move