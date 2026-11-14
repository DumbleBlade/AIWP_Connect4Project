import time as te
import copy
import streamlit as st
import streamlit.components.v1 as components

from ALPHABETA import AB
from MINMAX import MM
from ABC3 import ABC
from WINCHECKER import WINCHECK

#==================================================================================

st.set_page_config(

    "Connect 4 Engine",
    layout='wide',
    page_icon=':material/smart_toy:'

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

    st.session_state['WC'] = 4

if 'Alg' not in st.session_state:

    st.session_state['Alg'] = 'MM'

if 'board' not in st.session_state:
    
    st.session_state['board'] = [['E' for _ in range(st.session_state['RC'][1])] for _ in range(st.session_state['RC'][0])]

if 'curr_player' not in st.session_state:

    st.session_state['curr_player'] = 'Y'

if 'play_first' not in st.session_state:

    st.session_state['play_first'] = True

if 'user_move' not in st.session_state:

    st.session_state['user_move'] = True

if 'prev_move' not in st.session_state:

    st.session_state['prev_move'] = []

if 'delay' not in st.session_state:

    st.session_state['delay'] = 0.5

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

def process_move(col_idx):

    for row_idx in reversed(range(st.session_state['RC'][0])):

        if st.session_state['board'][row_idx][col_idx] == 'E':

            st.session_state['prev_move'] = [row_idx, col_idx]
            st.session_state['board'][row_idx][col_idx] = st.session_state['curr_player']
            st.session_state['curr_player'] = 'R' if st.session_state['curr_player'] == 'Y' else 'Y'
            st.session_state['user_move'] = False
            save_state()

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

#==================================================================================

cols_count = st.session_state['RC'][1]
hover_bg = "rgba(255, 209, 102, 0.25)" if st.session_state['curr_player'] == 'Y' else "rgba(255, 75, 75, 0.25)"

st.markdown(
    f"""
    <style>
        header[data-testid="stHeader"] {{ display: none !important; }}
        div[data-testid="stMainBlockContainer"] {{
            padding: 1rem 2rem;
            max-width: 100%;
        }}

        .board-wrapper {{
            display: flex;
            justify-content: center;
            width: 100%;
            margin-top: 1rem;
        }}
        
        .board-scaler {{
            position: relative;
            width: 100%;
            max-width: min(100%, min(calc({cols_count} * 5rem), calc({cols_count} * 8.5vh)));
            margin: 0 auto;
        }}

        .board-container {{
            display: grid;
            grid-template-columns: repeat({cols_count}, minmax(0, 1fr));
            gap: clamp(2px, 0.4vw, 0.5rem);
            background-color: #1e56a0;
            padding: clamp(4px, 0.8vw, 1rem);
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            width: 100%;
        }}
        
        .click-overlays {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            display: grid;
            grid-template-columns: repeat({cols_count}, 1fr);
            gap: clamp(2px, 0.4vw, 0.5rem);
            padding: clamp(4px, 0.8vw, 1rem);
            z-index: 10;
            box-sizing: border-box;
        }}
        
        .col-overlay {{
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.15s ease;
        }}
        .col-overlay:hover:not(.disabled) {{
            background-color: {hover_bg};
            box-shadow: inset 0 0 15px rgba(0,0,0,0.2);
        }}
        .col-overlay.disabled {{
            cursor: default;
        }}
        
        .cell {{
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 50%;
            background-color: #16315c; 
            box-shadow: inset 0 4px 8px rgba(0,0,0,0.5);
        }}
        .p1 {{ 
            background-color: #ff4b4b; 
            box-shadow: inset 0 -4px 8px rgba(0,0,0,0.3); 
        }} 
        .p2 {{ 
            background-color: #ffd166; 
            box-shadow: inset 0 -4px 8px rgba(0,0,0,0.3); 
        }}
        .last-move {{
            border: 3px solid #ffffff;
            box-shadow: 0 0 10px rgba(255,255,255,0.7), inset 0 -4px 8px rgba(0,0,0,0.3);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


#==================================================================================

with st.expander(":material/settings: Game Settings", expanded=True):

    c1, c2, c3 = st.columns(3)
    
    with c1:

        max_rows = st.number_input("Max Rows", min_value=6, max_value=20, value=st.session_state['RC'][0])
        curr_VS = st.selectbox("Versus", options=['PvP', 'PvE', 'EvE'], index=['PvP', 'PvE', 'EvE'].index(st.session_state['VS']))
        MH = st.slider("History length", min_value=0, max_value=20, value=st.session_state['max_hist'])
        
    with c2:

        max_cols = st.number_input("Max Cols", min_value=6, max_value=20, value=st.session_state['RC'][1])
        alg = st.selectbox("Algorithm", options=['MM', 'AB', 'ABC'], index=['MM', 'AB', 'ABC'].index(st.session_state['Alg']), disabled=(curr_VS == 'PvP'))
        ED = st.slider("Delay Between Engine Moves", min_value=0.0, max_value=5.0, value=float(st.session_state['delay']), step=0.1)

    with c3:

        WC = st.number_input("Win Condition Length", min_value=3, max_value=max(max_rows, max_cols) or 3, value=st.session_state['WC'])
        
        FP_index = 0 if st.session_state['play_first'] else 1
        FP = st.selectbox("Play First", options=['Yellow, Goes First', 'Red Goes Second'], index=FP_index, disabled=(curr_VS != 'PvE'))
        
        st.write("")

        if st.button(
            
            "Reset/Confirm Settings", 
            type='primary', 
            use_container_width=True

            ):
            
                st.session_state['Alg'] = alg
                
                st.session_state['play_first'] = (FP == 'Yellow, Goes First')
                st.session_state['user_move'] = st.session_state['play_first']
                
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

    SC = (

            max_rows != st.session_state['RC'][0] or 
            max_cols != st.session_state['RC'][1] or 
            curr_VS != st.session_state['VS'] or 
            alg != st.session_state['Alg'] or 
            WC != st.session_state['WC'] or 
            (FP == 'Yellow, Goes First') != st.session_state['play_first'] or 
            ED != st.session_state['delay'] or 
            MH != st.session_state['max_hist']
        
        )

    if SC:

        st.caption(":orange[:material/warning: Settings were modified. Confirm to reset.]")


st.title(

    ":red[Connect] :blue[4] :yellow[Engine]", 
    text_alignment='center'
    
    )

won = WINCHECK()

status_placeholder = st.empty()
disable_all_input = False

if won != 'Continue':

    disable_all_input = True

    if won == 'Draw':

        status_placeholder.info("Game Over! It was a Draw")

    else:

        color = 'yellow' if won == 'Y' else 'red'
        
        status_placeholder.subheader(f"Game Over! :{color}[{color}] wins", text_alignment='center') 
else:

    if st.session_state['VS'] == 'PvE' and not st.session_state['user_move']:

        disable_all_input = True

    elif st.session_state['VS'] == 'EvE':

        disable_all_input = True

cols = st.columns(st.session_state['RC'][1])

for c_idx, col in enumerate(cols):

    col_is_full = (st.session_state['board'][0][c_idx] != 'E')

    with col:

        st.button(

            f"DROP_COL_{c_idx}", 
            key=f"hidden_btn_{c_idx}", 
            disabled=(col_is_full or disable_all_input),
            on_click=process_move, 
            args=(c_idx,)

        )

board_html = "<div class='board-wrapper'><div class='board-scaler'>"

board_html += "<div class='board-container'>"

for r in range(st.session_state['RC'][0]):

    for c in range(st.session_state['RC'][1]):

        val = st.session_state['board'][r][c]

        cell_class = "empty"

        if val == 'R':

            cell_class = "p1"

        elif val == 'Y':

            cell_class = "p2"

        if st.session_state['prev_move'] == [r, c]:

            cell_class += " last-move"

        board_html += f"<div class='cell {cell_class}'></div>"

board_html += "</div>"

board_html += "<div class='click-overlays'>"

for c in range(st.session_state['RC'][1]):

    col_is_full = (st.session_state['board'][0][c] != 'E')
    overlay_class = "col-overlay disabled" if (col_is_full or disable_all_input) else "col-overlay"
    board_html += f"<div class='{overlay_class}'></div>"

board_html += "</div>"

board_html += "</div></div>"

st.markdown(board_html, unsafe_allow_html=True)

components.html(
    """
    <script>
        const doc = window.parent.document;
        
        function attachAndHide() {
            const allBtns = Array.from(doc.querySelectorAll('button'));
            const dropBtns = allBtns.filter(b => b.textContent && b.textContent.includes('DROP_COL_'));
            
            if (dropBtns.length > 0) {
                // 1. Hide the entire container holding the buttons
                const btnRow = dropBtns[0].closest('div[data-testid="stHorizontalBlock"]');
                if (btnRow) {
                    btnRow.style.display = 'none';
                    btnRow.style.position = 'absolute';
                    btnRow.style.visibility = 'hidden';
                }
                
                // 2. Map clicks from the visual board directly to the hidden buttons
                const overlays = doc.querySelectorAll('.col-overlay');
                overlays.forEach((overlay, idx) => {
                    // Clone and replace to prevent duplicate click listeners on re-runs
                    const newOverlay = overlay.cloneNode(true);
                    overlay.parentNode.replaceChild(newOverlay, overlay);
                    
                    newOverlay.addEventListener('click', () => {
                        const currentBtns = Array.from(doc.querySelectorAll('button'));
                        const targetBtn = currentBtns.find(b => b.textContent && b.textContent.includes('DROP_COL_' + idx));
                        
                        if (targetBtn && !targetBtn.disabled) {
                            targetBtn.click();
                        }
                    });
                });
                return true; // Successfully found and bound
            }
            return false; // Buttons aren't in the DOM yet
        }

        // Run immediately, and if it fails, retry rapidly until React finishes rendering
        if (!attachAndHide()) {
            const intervalId = setInterval(() => {
                if (attachAndHide()) {
                    clearInterval(intervalId);
                }
            }, 30); // Check every 30 milliseconds
            
            // Failsafe: stop checking after 5 seconds to prevent infinite loops
            setTimeout(() => clearInterval(intervalId), 5000);
        }
    </script>
    """,
    height=0, width=0
)

st.write("")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 1])

with col_ctrl1:

    if st.button(
        
        "Undo Move", 
        use_container_width=True, 
        disabled=(st.session_state['hist_idx'] <= 0)
        
        ):
        
            steps = 2 if (st.session_state['VS'] == 'PvE' and st.session_state['user_move'] and st.session_state['hist_idx'] >= 2) else 1
            st.session_state['hist_idx'] -= steps
            load_state()
            st.rerun()
        
with col_ctrl2:

    if st.session_state['VS'] == 'EvE':

        if st.button(
            
            "Redo Move", 
            use_container_width=True, 
            disabled=(st.session_state['hist_idx'] >= len(st.session_state['history']) - 1)
            
            ):
                
                st.session_state['hist_idx'] += 1
                load_state()
                st.rerun()
            
with col_ctrl3:

    if st.session_state['VS'] == 'EvE':

        if st.button(
            
            "Play / Pause Engine", 
            use_container_width=True, 
            type='primary'
            
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

                with st.spinner(f"Player {st.session_state['curr_player']} Engine is thinking..."):
                    
                    EngineMove()

            st.rerun()