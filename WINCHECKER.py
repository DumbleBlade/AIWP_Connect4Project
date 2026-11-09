import streamlit as st

def WINCHECK(row: int, col:int) -> str:

    WC = st.session_state['WC']
    rows = st.session_state['RC'][0]
    cols = st.session_state['RC'][1]

    axes = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for dr, dc in axes:

        consecutive = 1

        r, c = row + dr, col + dc

        while 0 <= r < rows and 0 <= c < cols and st.session_state['board'][r][c] == st.session_state['curr_player']:
            
            consecutive += 1
            r += dr
            c += dc

        r, c = row - dr, col - dc

        while 0 <= r < rows and 0 <= c < cols and st.session_state['board'][r][c] == st.session_state['curr_player']:
            
            consecutive += 1

            r -= dr
            c -= dc

        if consecutive >= WC:

            return "Win"

    if 'E' not in st.session_state['board'][0]:
    
        return "Draw"

    return "Continue"
        

