import streamlit as st

def WINCHECK() -> str:

    if st.session_state['prev_move']:

        row , col = st.session_state['prev_move'] 

    else:

        return 'Continue'

    WC = st.session_state['WC']
    max_rows, max_cols = st.session_state['RC']

    player = st.session_state['board'][row][col]

    axes = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in axes:

        consecutive = 1

        r, c = row + dr, col + dc

        while 0 <= r < max_rows and 0 <= c < max_cols and st.session_state['board'][r][c] == player:
            
            consecutive += 1
            r += dr
            c += dc

        r, c = row - dr, col - dc

        while 0 <= r < max_rows and 0 <= c < max_cols and st.session_state['board'][r][c] == player:
            
            consecutive += 1

            r -= dr
            c -= dc

        if consecutive >= WC:

            return player

    if 'E' not in st.session_state['board'][0]:
    
        return "Draw"

    return "Continue"
        

