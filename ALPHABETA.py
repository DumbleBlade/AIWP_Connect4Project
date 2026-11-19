import time as te
import streamlit as st
import WINCHECKER as WR

def AB(board, depth_limit: int | None, time_limit: float | None = 2.0):
    
    start_time = te.perf_counter()
    ai = st.session_state["curr_player"]
    opponent = "R" if ai == "Y" else "Y"
    win_length = st.session_state["WC"]
    col_heights = list(st.session_state["col_heights"])

    rows = len(board)
    cols = len(board[0])
    centre = cols // 2
    col_order = sorted(range(cols), key=lambda c: (abs(c - centre), c))

    win_score = max(100000, (10 ** win_length) * 1000)

    def valid_moves(position):
        return [c for c in col_order if position[0][c] == "E"]

    def evaluate(position):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        # Prefer occupying the centre columns, which participate in more
        # possible win_length-in-a-row combinations.
        for r in range(rows):
            for c in range(cols):
                if position[r][c] == ai:
                    score += max(0, cols - abs(c - centre) * 2)
                elif position[r][c] == opponent:
                    score -= max(0, cols - abs(c - centre) * 2)

        # Evaluate every possible win_length-sized window.
        for r in range(rows):
            for c in range(cols):
                for dr, dc in directions:
                    end_r = r + (win_length - 1) * dr
                    end_c = c + (win_length - 1) * dc

                    if not (0 <= end_r < rows and 0 <= end_c < cols):
                        continue

                    window = [
                        position[r + i * dr][c + i * dc]
                        for i in range(win_length)
                    ]

                    ai_count = window.count(ai)
                    opp_count = window.count(opponent)
                    empty_count = window.count("E")

                    # A window containing both players cannot become a win
                    # for either side, so it contributes no score.
                    if ai_count and opp_count:
                        continue

                    if ai_count:
                        score += 10 ** ai_count
                        if ai_count == win_length - 1 and empty_count == 1:
                            score += 50
                    elif opp_count:
                        score -= 10 ** opp_count
                        if opp_count == win_length - 1 and empty_count == 1:
                            score -= 60

        return score

    class SearchTimeout(Exception):
        pass

    nodes = 0

    def minimax(depth, alpha, beta, maximizing, last_move):
        nonlocal nodes
        nodes += 1
        if time_limit is not None and (nodes & 1023) == 0 and (te.perf_counter() - start_time) >= time_limit:
            raise SearchTimeout()

        result = WR.WINCHECKn(board, last_move, win_length)

        if result == ai:
            return win_score + depth, None
        if result == opponent:
            return -win_score - depth, None
        if result == "Draw":
            return 0, None

        moves = valid_moves(board)

        if not moves:
            return 0, None

        if depth == 0:
            return evaluate(board), None

        best_col = moves[0]

        if maximizing:
            best_score = float("-inf")

            for col in moves:
                row = col_heights[col]
                board[row][col] = ai
                col_heights[col] -= 1

                score, _ = minimax(
                    depth - 1, alpha, beta, False, (row, col)
                )

                board[row][col] = "E"
                col_heights[col] += 1

                if score > best_score:
                    best_score = score
                    best_col = col

                alpha = max(alpha, best_score)

                # Remaining branches cannot improve MIN's decision.
                if alpha >= beta:
                    break

            return best_score, best_col

        else:
            best_score = float("inf")

            for col in moves:
                row = col_heights[col]
                board[row][col] = opponent
                col_heights[col] -= 1

                score, _ = minimax(
                    depth - 1, alpha, beta, True, (row, col)
                )

                board[row][col] = "E"
                col_heights[col] += 1

                if score < best_score:
                    best_score = score
                    best_col = col

                beta = min(beta, best_score)

                # Remaining branches cannot improve MAX's decision.
                if alpha >= beta:
                    break

            return best_score, best_col

    # The game may already be over or the board may be full.
    moves = valid_moves(board)
    if not moves:
        return None

    best_col = moves[0]
    empty_cells = sum(h + 1 for h in col_heights)
    max_depth = empty_cells if (depth_limit is None or depth_limit == float("inf")) else min(int(depth_limit), empty_cells)

    for d in range(1, max_depth + 1):
        if time_limit is not None and (te.perf_counter() - start_time) >= time_limit:
            break
        try:
            score, col = minimax(
                d,
                float("-inf"),
                float("inf"),
                True,
                st.session_state["prev_move"]
            )
            if col is not None:
                best_col = col
            if score >= win_score:
                break
        except SearchTimeout:
            break

    return best_col