def ToBitboards(board, rows: int, cols: int, WC: int = 4) -> tuple[int, int]:

    r_bits = 0
    y_bits = 0
    stride = rows + WC

    for i in range(rows):

        for j in range(cols):

            cell = board[i][j]

            if cell == "Y":

                y_bits |= 1 << (j * stride + (rows - 1 - i))

            elif cell == "R":

                r_bits |= 1 << (j * stride + (rows - 1 - i))

    return r_bits, y_bits


def WINCHECKb(Rbits: int, Ybits: int, rows: int, cols: int, WC: int) -> str:

    h = rows + WC

    for player, bb in (('R', Rbits), ('Y', Ybits)):

        for stride in (1, h, h + 1, h - 1):

            temp = bb
            shift = 1

            while (shift << 1) <= WC:

                temp &= temp >> (shift * stride)
                shift <<= 1

            rem = WC - shift

            if rem > 0:

                temp &= temp >> (rem * stride)

            if temp != 0:

                return player

    full_mask = 0
    col_bits = (1 << rows) - 1

    for c in range(cols):

        full_mask |= col_bits << (c * h)

    if (Rbits | Ybits) == full_mask:
        
        return 'Draw'

    return 'Continue'

def WINCHECKn(board, last_move, WC):

    rows = len(board)
    cols = len(board[0])
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))

    if last_move:

        r0, c0 = last_move
        player = board[r0][c0]

        if player in ('R', 'Y'):

            for dr, dc in directions:

                count = 1

                for step in (1, -1):

                    r = r0 + dr * step
                    c = c0 + dc * step

                    while 0 <= r < rows and 0 <= c < cols and board[r][c] == player:

                        count += 1

                        if count >= WC:

                            return player

                        r += dr * step
                        c += dc * step

        if 'E' not in board[0]:

            return 'Draw'

        return 'Continue'

    for r in range(rows):

        for c in range(cols):

            player = board[r][c]

            if player == 'E':

                continue

            for dr, dc in directions:

                end_r = r + (WC - 1) * dr
                end_c = c + (WC - 1) * dc

                if 0 <= end_r < rows and 0 <= end_c < cols:

                    won = True

                    for i in range(1, WC):

                        if board[r + i * dr][c + i * dc] != player:

                            won = False
                            break

                    if won:

                        return player

    if 'E' not in board[0]:

        return 'Draw'

    return 'Continue'