import time as te
import copy
import streamlit as st
from ALPHABETA import AB
from MINMAX import MM
from ABC3 import ABC
from WINCHECKER import WINCHECK

#==================================================================================

st.set_page_config(

    "Connect 4 Engine",
    layout = 'wide',
    page_icon = ':material/smart_toy:'
    
)

if 'max_hist' not in st.session_state:

    st.session_state['max_hist'] = 5

if 'history' not in st.session_state:

    st.session_state['history'] = []

if 'hist_idx' not in st.session_state:

    st.session_state['hist_idx'] = -1

if 'paused' not in st.session_state:

    st.session_state['paused'] = True

if 'RC' not in st.session_state:

    st.session_state['RC'] = [6 , 6]

if 'VS' not in st.session_state:

    st.session_state['VS'] = 'PvP'

if 'WC' not in st.session_state:

    st.session_state['WC'] = 3

if 'Alg' not in st.session_state:

    st.session_state['Alg'] = 'MM'

if 'board' not in st.session_state:

    st.session_state['board'] = [['E' for _ in range(st.session_state['RC'][1])] for _ in range(st.session_state['RC'][0])]

if 'curr_player' not in st.session_state:

    st.session_state['curr_player'] = 'Y'

if 'user_move' not in st.session_state:

    st.session_state['user_move'] = True

if 'prev_move' not in st.session_state:

    st.session_state['prev_move'] = []

if 'delay' not in st.session_state:

    st.session_state['delay'] = 1

def save_state():

    st.session_state['history'] = st.session_state['history'][:st.session_state['hist_idx'] + 1]

    st.session_state['history'].append({

        'board': copy.deepcopy(st.session_state['board']),
        'curr_player': st.session_state['curr_player'],
        'prev_move': copy.deepcopy(st.session_state['prev_move']),
        'user_move': st.session_state['user_move']

    })
    
    if len(st.session_state['history']) > st.session_state['max_hist']:

        st.session_state['history'].pop(0)
        
    st.session_state['hist_idx'] = len(st.session_state['history']) - 1


def load_state():

    state = st.session_state['history'][st.session_state['hist_idx']]

    st.session_state['board'] = copy.deepcopy(state['board'])
    st.session_state['curr_player'] = state['curr_player']
    st.session_state['prev_move'] = copy.deepcopy(state['prev_move'])
    st.session_state['user_move'] = state['user_move']


if not st.session_state['history']:

    save_state()

#==================================================================================

st.markdown(

    f"""
    <style>
        .board-container {{
            display: grid;
            grid-template-columns: repeat({st.session_state['RC'][1]}, 1fr);
            gap: 0.5rem;
            background-color: #1e56a0;
            padding: 0.5rem;
            border-radius: 10px;
            width: 100%;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        .cell {{
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 50%;
            background-color: #16315c; 
            box-shadow: inset 0 3px 6px rgba(0,0,0,0.5);
        }}
        .p1 {{ 
            background-color: #ff4b4b; 
            box-shadow: inset 0 -3px 6px rgba(0,0,0,0.3); 
        }} 
        .p2 {{ 
            background-color: #ffd166; 
            box-shadow: inset 0 -3px 6px rgba(0,0,0,0.3); 
        }} 
    </style>
    """,
    unsafe_allow_html=True,

)

#==================================================================================

def render_button(disable_cond):

    cols = st.columns(st.session_state['RC'][1], gap = 'xxsmall')

    for col_idx, col_drop in enumerate(cols):

        col_full = (st.session_state['board'][0][col_idx] != 'E') or disable_cond

        if col_drop.button(

            "",
            icon = ':material/arrow_drop_down:',
            key = f"drop-{col_idx}",
            width = 'stretch',
            disabled = col_full

        ):

            for row_idx in reversed(range(st.session_state['RC'][0])):

                if st.session_state['board'][row_idx][col_idx] == 'E':

                    st.session_state['prev_move'] = [row_idx, col_idx]
                    st.session_state['board'][row_idx][col_idx] = st.session_state['curr_player']
                    st.session_state['curr_player'] = 'R' if st.session_state['curr_player'] == 'Y' else 'Y'
                    st.session_state['user_move'] = False
                    
                    save_state()

                    st.rerun()
        
                    break

def EngineMove():

    board_backup = copy.deepcopy(st.session_state['board'])

    if st.session_state['Alg'] == 'MM':

        col_idx = MM()

    elif st.session_state['Alg'] == 'AB':

        col_idx = AB()

    else:

        col_idx = ABC()

    st.session_state['board'] = board_backup

    for row_idx in reversed(range(st.session_state['RC'][0])):

        if st.session_state['board'][row_idx][col_idx] == 'E':

            st.session_state['prev_move'] = [row_idx, col_idx]
            st.session_state['board'][row_idx][col_idx] = st.session_state['curr_player']
            st.session_state['curr_player'] = 'R' if st.session_state['curr_player'] == 'Y' else 'Y'
            st.session_state['user_move'] = True
            
            save_state()

            break

def PvPMove():

    render_button(False)

def PvEMove():

    render_button(not st.session_state['user_move'])

#==================================================================================

col_settings, col_main, col_gap  = st.columns([1,3,1])

with col_settings:

    st.title(

        ":red[Sett]:yellow[ings]",
        text_alignment = 'center'

    )

    col_row, col_col = st.columns([1,1])

    with col_row:

        max_rows = st.number_input(

            "Max Rows",
            min_value = 6,
            max_value = 20,

        )

        curr_VS = st.selectbox(

            "Versus",
            options = ['PvP', 'PvE', 'EvE'],

        )

    with col_col:

        max_cols = st.number_input(

            "Max Cols",
            min_value = 6,
            max_value = 20,

        )
        
        alg = st.selectbox(

            "Algorithm",
            options = ['MM', 'AB', 'ABC'],
            disabled = (curr_VS == 'PvP')

        )

    WC = st.number_input(
    
        "Win Condition Length",
        min_value = 3,
        max_value = max(max_rows, max_cols) or 3,

    )

    FP = st.selectbox(

        "Play First or Second",
        options = ['Yellow, Goes First', 'Red Goes Second'],
        disabled = (curr_VS != 'PvE')

    )

    if st.toggle(

        'Other settings',

    ):
        
        ED = st.slider(

            "Delay Between Engine Moves",
            min_value = 0.0,
            max_value = 5.0,
            value = 0.0,
            step = 0.1

        )

        MH = st.slider(

            "History length",
            min_value = 0,
            max_value = 20,
            value = 5

        )


    SC = (

        max_rows != st.session_state['RC'][0]
        or max_cols != st.session_state['RC'][1]
        or curr_VS != st.session_state['VS']
        or alg != st.session_state['Alg']
        or WC != st.session_state['WC']
        or (FP == 'Yellow, Goes First') != st.session_state['user_move']
        or ED != st.session_state['delay']
        or MH != st.session_state['max_hist']

    )

    if SC:

        st.caption(":orange[:material/warning: Settings were modified. Confirm to reset.]")

    if st.button(
        
        "Reset/Confirm",
        type='primary', 
        width = 'stretch'
    
    ):

        st.session_state['Alg'] = alg
        st.session_state['user_move'] = (FP == 'Yellow, Goes First')
        st.session_state['prev_move'] = []
        st.session_state['WC'] = WC
        st.session_state['RC'] = [max_rows, max_cols]
        st.session_state['board'] = [['E' for _ in range(int(max_cols))] for _ in range(int(max_rows))]
        st.session_state['VS'] = curr_VS
        st.session_state['curr_player'] = 'Y'
        st.session_state['max_hist'] = MH
        st.session_state['delay'] = ED
        
        st.session_state['history'] = []
        st.session_state['hist_idx'] = -1
        st.session_state['paused'] = True
        
        save_state()

        st.rerun()

#==================================================================================

with col_main:

    st.title(

        ":red[Connect] :blue[4] :yellow[Engine]",
        text_alignment = 'center'

    )

    won = WINCHECK()

    status_placeholder = st.empty()
    buttons_placeholder = st.empty()
    board_placeholder = st.empty()
    controls_placeholder = st.empty()

    if won != 'Continue':

        if won == 'Draw':

            status_placeholder.info(f"Game Over! It was a Draw")

        else:

            color = 'yellow' if won == 'Y' else 'red'
            status_placeholder.subheader(f"Game Over! :{color}[{color}] wins", text_alignment = 'center') 

    else:

        with buttons_placeholder.container():

            if st.session_state['VS'] == 'PvP':

                PvPMove()

            elif st.session_state['VS'] == 'PvE':

                PvEMove()

    board_html = "<div class='board-container'>"

    for r in range(0, st.session_state['RC'][0]):

        for c in range(0, st.session_state['RC'][1]):

            val = st.session_state['board'][r][c]

            cell_class = "empty"

            if val == 'R':

                cell_class = "p1"

            elif val == 'Y':

                cell_class = "p2"

            board_html += f"<div class='cell {cell_class}'></div>"

    board_html += "</div>"

    board_placeholder.markdown(board_html, unsafe_allow_html = True)

    with controls_placeholder.container():

        st.write("") 

        c1, c2, c3 = st.columns(3)
        
        with c1:

            if st.button(

                "Undo", 
                use_container_width = True, 
                disabled = (st.session_state['hist_idx'] <= 0)

            ):

                steps = 2 if (st.session_state['VS'] == 'PvE' and st.session_state['user_move'] and st.session_state['hist_idx'] >= 2) else 1
                
                st.session_state['hist_idx'] -= steps
                
                load_state()
                
                st.rerun()
                
        with c2:

            if st.session_state['VS'] == 'EvE':

                if st.button(

                    "Redo", 
                    use_container_width = True, 
                    disabled = (st.session_state['hist_idx'] >= len(st.session_state['history']) - 1)

                ):

                    st.session_state['hist_idx'] += 1
                    
                    load_state()
                    
                    st.rerun()
                    
        with c3:

            if st.session_state['VS'] == 'EvE':

                if st.button(
                    
                    "Play/Pause", 
                    use_container_width = True,
                    type = 'primary'
                
                ):

                    st.session_state['paused'] = not st.session_state['paused']
                    
                    st.rerun()

    if won == 'Continue':

        if st.session_state['VS'] == 'PvE' and not st.session_state['user_move']:

            te.sleep(st.session_state['delay'])

            with status_placeholder.container():

                with st.spinner("Engine is thinking..."):

                    EngineMove()
            
            st.rerun()
            
        elif st.session_state['VS'] == 'EvE':

            if not st.session_state['paused']:

                te.sleep(st.session_state['delay'])

                with status_placeholder.container():

                    with st.spinner(f"Player {st.session_state['curr_player']} is thinking..."):

                        EngineMove()
                
                st.rerun()