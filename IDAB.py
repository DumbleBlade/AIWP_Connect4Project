import time as te
import streamlit as st
import WINCHECKER as WR

EXACT = 0
LOWER = 1
UPPER = 2

def IDNAB(board, depth_limit: int | None, time_limit: float | None = 2.0):

    start_time = te.perf_counter()
    ai = st.session_state['curr_player']
    WC = st.session_state['WC']

    rows = len(board)
    cols = len(board[0])
    stride = rows + 1
    total_bits = cols * stride

    col_heights = [
        max((r for r in range(rows) if board[r][c] == "E"), default=-1)
        for c in range(cols)
    ]

    r_bits, y_bits = WR.ToBitboards(board, rows, cols, WC)

    # Precompute win-check shift amounts for each of the 4 directions
    shift_steps = []
    s = 1
    while (s << 1) <= WC:
        shift_steps.append(s)
        s <<= 1
    if WC - s > 0:
        shift_steps.append(WC - s)

    dir_shifts = tuple(
        tuple(step * d for step in shift_steps)
        for d in (1, stride, stride + 1, stride - 1)
    )

    def has_won(bb: int) -> bool:
        for shifts in dir_shifts:
            temp = bb
            for sh in shifts:
                temp &= temp >> sh
                if not temp:
                    break
            if temp:
                return True
        return False

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
    col_order = tuple(sorted(range(cols), key=lambda c: abs(c - (cols - 1) / 2)))

    # Next playable bit per column (0 if column is full)
    col_bits = [
        (1 << (c * stride + (rows - 1 - col_heights[c]))) if col_heights[c] >= 0 else 0
        for c in range(cols)
    ]

    weights = [0] + [10 ** (i * 2) for i in range(WC)]
    opp_weights = [int(w * 1.2) for w in weights]
    win_score = weights[WC - 1] * 1000

    def evaluate(p_bits: int, o_bits: int) -> int:
        score = ((p_bits & center_mask).bit_count() - (o_bits & center_mask).bit_count()) * 4

        for mask in valid_windows:
            p_m = p_bits & mask
            o_m = o_bits & mask

            if p_m and not o_m:
                score += weights[p_m.bit_count()]
            elif o_m and not p_m:
                score -= opp_weights[o_m.bit_count()]

        return score

    class SearchTimeout(Exception):
        pass

    # Transposition table: state_key -> (depth, flag, score, best_col)
    tt: dict[int, tuple[int, int, float, int]] = {}
    tt_max_size = 200000
    nodes = 0

    def negamax(
        depth: int,
        alpha: float,
        beta: float,
        player: str,
        r_bb: int,
        y_bb: int,
        empty_left: int,
    ) -> tuple[float, int | None]:
        nonlocal nodes
        nodes += 1
        if time_limit is not None and (nodes & 1023) == 0 and (te.perf_counter() - start_time) >= time_limit:
            raise SearchTimeout()

        if empty_left == 0:
            return 0, None

        moves = [c for c in col_order if col_heights[c] >= 0]
        if not moves:
            return 0, None

        # Immediate 1-ply win check before TT lookup or recursion
        curr_bb = y_bb if player == "Y" else r_bb
        for col in moves:
            if has_won(curr_bb | col_bits[col]):
                return win_score + depth, col

        if depth == 0:
            ai_bb, opp_bb = (y_bb, r_bb) if ai == "Y" else (r_bb, y_bb)
            score = evaluate(ai_bb, opp_bb)
            return (score if player == ai else -score), None

        orig_alpha = alpha
        key = (r_bb << total_bits) | y_bb
        entry = tt.get(key)
        tt_move: int | None = None

        if entry is not None:
            tt_depth, tt_flag, tt_score, tt_move = entry
            if tt_depth >= depth:
                if tt_flag == EXACT:
                    return tt_score, tt_move
                elif tt_flag == LOWER:
                    if tt_score > alpha:
                        alpha = tt_score
                elif tt_flag == UPPER:
                    if tt_score < beta:
                        beta = tt_score
                if alpha >= beta:
                    return tt_score, tt_move

        if tt_move is not None and tt_move in moves:
            moves.remove(tt_move)
            moves.insert(0, tt_move)

        best_score = float('-inf')
        best_col = moves[0]
        next_player = "R" if player == "Y" else "Y"

        for col in moves:
            bit = col_bits[col]
            col_heights[col] -= 1
            col_bits[col] = bit << 1

            if player == "Y":
                score, _ = negamax(depth - 1, -beta, -alpha, next_player, r_bb, y_bb | bit, empty_left - 1)
            else:
                score, _ = negamax(depth - 1, -beta, -alpha, next_player, r_bb | bit, y_bb, empty_left - 1)

            score = -score
            col_heights[col] += 1
            col_bits[col] = bit

            if score > best_score:
                best_score = score
                best_col = col

            if score > alpha:
                alpha = score
                if alpha >= beta:
                    break

        if best_score <= orig_alpha:
            flag = UPPER
        elif best_score >= beta:
            flag = LOWER
        else:
            flag = EXACT

        if len(tt) >= tt_max_size:
            tt.clear()
        tt[key] = (depth, flag, best_score, best_col)

        return best_score, best_col

    moves = [c for c in col_order if col_heights[c] >= 0]

    if not moves:

        return None

    best_move = moves[0]
    empty_cells = sum(h + 1 for h in col_heights)
    max_depth = empty_cells if (depth_limit is None or depth_limit == float('inf')) else min(int(depth_limit), empty_cells)

    for d in range(1, max_depth + 1):

        if time_limit is not None and te.perf_counter() - start_time >= time_limit:

            break

        try:

            score, col = negamax(d, float('-inf'), float('inf'), ai, r_bits, y_bits, empty_cells)

            if col is not None:

                best_move = col

            if score >= win_score:

                break

        except SearchTimeout:

            break

    return best_move