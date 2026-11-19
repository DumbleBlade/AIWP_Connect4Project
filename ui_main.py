import time as te
import copy
import streamlit as st
import streamlit.components.v1 as components

from ALPHABETA import AB
from MINMAX import MM
from IDAB import IDNAB
import WINCHECKER as WR

#==================================================================================

st.set_page_config(

    "Connect 4 Engine",
    layout='wide',
    page_icon=':material/smart_toy:'

)

default_states = {

    'max_hist': 5,
    'history': [],
    'hist_idx': 0,
    'paused': True,
    'RC': [6, 6],
    'VS': 'PvP',
    'WC': 4,
    'curr_player': 'Y',
    'play_first': True,
    'user_move': True,
    'prev_move': [],
    'delay': 0.5,
    'alg': 'MM',
    'limit_mode': 'Both',
    'depth_limit': 5,
    'time_limit': 2.0,
    'alg_y': 'MM',
    'limit_mode_y': 'Both',
    'depth_y': 5,
    'time_y': 2.0,
    'alg_r': 'MM',
    'limit_mode_r': 'Both',
    'depth_r': 5,
    'time_r': 2.0

}

for key, val in default_states.items():

    if key not in st.session_state:

        st.session_state[key] = val

if 'board' not in st.session_state:

    st.session_state['board'] = [['E' for _ in range(st.session_state['RC'][1])] for _ in range(st.session_state['RC'][0])]

if 'col_heights' not in st.session_state:

    st.session_state['col_heights'] = [st.session_state['RC'][0] - 1] * st.session_state['RC'][1]

#==================================================================================

def DropPiece(col_idx, next_user_move):

    row_idx = st.session_state['col_heights'][col_idx]

    if row_idx >= 0:

        st.session_state['col_heights'][col_idx] -= 1
        st.session_state['prev_move'] = [row_idx, col_idx]
        st.session_state['board'][row_idx][col_idx] = st.session_state['curr_player']
        st.session_state['curr_player'] = 'R' if st.session_state['curr_player'] == 'Y' else 'Y'
        st.session_state['user_move'] = next_user_move

        st.session_state['history'] = st.session_state['history'][:st.session_state['hist_idx']]
        st.session_state['history'].append([row_idx, col_idx])
        st.session_state['hist_idx'] = len(st.session_state['history'])

def ApplyHistoryStep(delta):

    target_idx = st.session_state['hist_idx'] + delta

    if delta < 0:

        for idx in range(st.session_state['hist_idx'] - 1, target_idx - 1, -1):

            r_idx, c_idx = st.session_state['history'][idx]
            st.session_state['board'][r_idx][c_idx] = 'E'
            st.session_state['col_heights'][c_idx] += 1

    else:

        for idx in range(st.session_state['hist_idx'], target_idx):

            r_idx, c_idx = st.session_state['history'][idx]
            player = 'Y' if idx % 2 == 0 else 'R'
            st.session_state['board'][r_idx][c_idx] = player
            st.session_state['col_heights'][c_idx] -= 1

    st.session_state['hist_idx'] = target_idx
    st.session_state['curr_player'] = 'Y' if target_idx % 2 == 0 else 'R'
    st.session_state['prev_move'] = list(st.session_state['history'][target_idx - 1]) if target_idx > 0 else []

    if st.session_state['VS'] == 'PvE':

        is_yellow_turn = (target_idx % 2 == 0)
        st.session_state['user_move'] = (is_yellow_turn == st.session_state['play_first'])

    else:

        st.session_state['user_move'] = True

def ProcessMove(col_idx):

    next_user_move = True if st.session_state['VS'] == 'PvP' else False
    DropPiece(col_idx, next_user_move)

def EngineMove():

    board_copy = [row[:] for row in st.session_state['board']]

    if st.session_state['VS'] == 'PvE':

        curr_alg = st.session_state['alg']
        curr_mode = st.session_state['limit_mode']
        curr_depth = None if curr_mode == 'Time' else st.session_state['depth_limit']
        curr_time = None if curr_mode == 'Depth' else st.session_state['time_limit']

    else:

        if st.session_state['curr_player'] == 'Y':

            curr_alg = st.session_state['alg_y']
            curr_mode = st.session_state['limit_mode_y']
            curr_depth = None if curr_mode == 'Time' else st.session_state['depth_y']
            curr_time = None if curr_mode == 'Depth' else st.session_state['time_y']

        else:

            curr_alg = st.session_state['alg_r']
            curr_mode = st.session_state['limit_mode_r']
            curr_depth = None if curr_mode == 'Time' else st.session_state['depth_r']
            curr_time = None if curr_mode == 'Depth' else st.session_state['time_r']

    if curr_alg == 'MM':

        col_idx = MM(board_copy, curr_depth, curr_time)

    elif curr_alg == 'AB':

        col_idx = AB(board_copy, curr_depth, curr_time)

    else:

        col_idx = IDNAB(board_copy, curr_depth, curr_time)

    if col_idx is not None:

        next_user_move = (st.session_state['VS'] == 'PvE')
        DropPiece(col_idx, next_user_move)

    else:

        st.session_state['paused'] = True
        st.session_state['user_move'] = True

#==================================================================================

st.markdown(
    """
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        div[data-testid="stMainBlockContainer"] {
            padding: 1rem 2rem;
            max-width: 100%;
        }

        .board-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-top: 1rem;
        }
        
        .board-scaler {
            position: relative;
            width: 100%;
            max-width: min(100%, min(calc(var(--cols-count) * 5rem), calc(var(--cols-count) * 8.5vh)));
            margin: 0 auto;
        }

        .board-container {
            display: grid;
            grid-template-columns: repeat(var(--cols-count), minmax(0, 1fr));
            gap: clamp(2px, 0.4vw, 0.5rem);
            background-color: #1e56a0;
            padding: clamp(4px, 0.8vw, 1rem);
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.4);
            width: 100%;
        }
        
        .click-overlays {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            display: grid;
            grid-template-columns: repeat(var(--cols-count), 1fr);
            gap: clamp(2px, 0.4vw, 0.5rem);
            padding: clamp(4px, 0.8vw, 1rem);
            z-index: 10;
            box-sizing: border-box;
        }
        
        .col-overlay {
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.15s ease;
        }
        .col-overlay:hover:not(.disabled) {
            background-color: var(--hover-bg);
            box-shadow: inset 0 0 15px rgba(0,0,0,0.2);
        }
        .col-overlay.disabled {
            cursor: default;
        }
        
        .cell {
            width: 100%;
            aspect-ratio: 1 / 1;
            border-radius: 50%;
            background-color: #16315c; 
            box-shadow: inset 0 4px 8px rgba(0,0,0,0.5);
        }
        .p1 { 
            background-color: #ff4b4b; 
            box-shadow: inset 0 -4px 8px rgba(0,0,0,0.3); 
        } 
        .p2 { 
            background-color: #ffd166; 
            box-shadow: inset 0 -4px 8px rgba(0,0,0,0.3); 
        }
        .last-move {
            border: 3px solid #ffffff;
            box-shadow: 0 0 10px rgba(255,255,255,0.7), inset 0 -4px 8px rgba(0,0,0,0.3);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(
    """
    <script>
        const parentWin = window.parent;
        const doc = parentWin.document;

        function bindBoardOverlays() {
            const allBtns = Array.from(doc.querySelectorAll('button'));
            const dropBtns = allBtns.filter(b => b.textContent && b.textContent.includes('DROP_COL_'));

            if (dropBtns.length > 0) {
                const btnRow = dropBtns[0].closest('div[data-testid="stHorizontalBlock"]');
                if (btnRow && btnRow.style.display !== 'none') {
                    btnRow.style.display = 'none';
                    btnRow.style.position = 'absolute';
                    btnRow.style.visibility = 'hidden';
                }

                const overlays = doc.querySelectorAll('.col-overlay:not([data-bound="true"])');
                overlays.forEach((overlay) => {
                    overlay.setAttribute('data-bound', 'true');
                    overlay.addEventListener('click', () => {
                        const colIdx = overlay.getAttribute('data-col');
                        const currentBtns = Array.from(doc.querySelectorAll('button'));
                        const targetBtn = currentBtns.find(b => b.textContent && b.textContent.trim() === 'DROP_COL_' + colIdx);
                        if (targetBtn && !targetBtn.disabled) {
                            targetBtn.click();
                        }
                    });
                });
            }
        }

        if (!parentWin.__c4ObserverAttached) {
            const observer = new MutationObserver(() => bindBoardOverlays());
            observer.observe(doc.body, { childList: true, subtree: true });
            parentWin.__c4ObserverAttached = true;
        }

        bindBoardOverlays();
    </script>
    """,
    height=0, width=0
)

#==================================================================================

with st.expander(":material/settings: Game Settings", expanded=True):

    c1, c2, c3 = st.columns(3)
    
    with c1:

        max_rows = st.number_input("Max Rows", min_value=6, max_value=20, value=st.session_state['RC'][0])
        curr_VS = st.selectbox("Versus", options=['PvP', 'PvE', 'EvE'], index=['PvP', 'PvE', 'EvE'].index(st.session_state['VS']))
        
    with c2:

        max_cols = st.number_input("Max Cols", min_value=6, max_value=20, value=st.session_state['RC'][1])
        WC = st.number_input("Win Condition Length", min_value=3, max_value=max(max_rows, max_cols) or 3, value=min(st.session_state['WC'], max(max_rows, max_cols) or 3))

    with c3:

        MH = st.slider("History Length", min_value=0, max_value=20, value=st.session_state['max_hist'])

        if curr_VS in ['PvE', 'EvE']:

            ED = st.slider("Delay Between Engine Moves", min_value=0.0, max_value=5.0, value=float(st.session_state['delay']), step=0.1)

        else:

            ED = st.session_state['delay']

    alg = st.session_state['alg']
    limit_mode = st.session_state['limit_mode']
    depth_limit = st.session_state['depth_limit']
    time_limit = st.session_state['time_limit']
    FP_bool = st.session_state['play_first']

    alg_y = st.session_state['alg_y']
    limit_mode_y = st.session_state['limit_mode_y']
    depth_y = st.session_state['depth_y']
    time_y = st.session_state['time_y']

    alg_r = st.session_state['alg_r']
    limit_mode_r = st.session_state['limit_mode_r']
    depth_r = st.session_state['depth_r']
    time_r = st.session_state['time_r']

    if curr_VS == 'PvE':

        st.divider()
        p1, p2, p3, p4, p5 = st.columns(5)

        with p1:

            alg = st.selectbox("Algorithm", options=['MM', 'AB', 'IDNAB'], index=['MM', 'AB', 'IDNAB'].index(st.session_state['alg']))

        with p2:

            limit_mode = st.selectbox("Constraint", options=['Depth', 'Time', 'Both'], index=['Depth', 'Time', 'Both'].index(st.session_state['limit_mode']))

        with p3:

            depth_limit = st.number_input("Depth Limit", min_value=1, max_value=20, value=st.session_state['depth_limit'], disabled=(limit_mode == 'Time'))

        with p4:

            time_limit = st.number_input("Time Limit (s)", min_value=0.1, max_value=60.0, value=float(st.session_state['time_limit']), step=0.1, disabled=(limit_mode == 'Depth'))

        with p5:

            FP_index = 0 if st.session_state['play_first'] else 1
            FP = st.selectbox("Play As", options=['First (Yellow)', 'Second (Red)'], index=FP_index)
            FP_bool = (FP == 'First (Yellow)')

    elif curr_VS == 'EvE':

        st.divider()
        e1, e2, e3, e4 = st.columns(4)

        with e1:

            alg_y = st.selectbox("Yellow Algorithm (Y)", options=['MM', 'AB', 'IDNAB'], index=['MM', 'AB', 'IDNAB'].index(st.session_state['alg_y']))
            alg_r = st.selectbox("Red Algorithm (R)", options=['MM', 'AB', 'IDNAB'], index=['MM', 'AB', 'IDNAB'].index(st.session_state['alg_r']))

        with e2:

            limit_mode_y = st.selectbox("Yellow Constraint", options=['Depth', 'Time', 'Both'], index=['Depth', 'Time', 'Both'].index(st.session_state['limit_mode_y']))
            limit_mode_r = st.selectbox("Red Constraint", options=['Depth', 'Time', 'Both'], index=['Depth', 'Time', 'Both'].index(st.session_state['limit_mode_r']))

        with e3:

            depth_y = st.number_input("Yellow Depth Limit", min_value=1, max_value=20, value=st.session_state['depth_y'], disabled=(limit_mode_y == 'Time'))
            depth_r = st.number_input("Red Depth Limit", min_value=1, max_value=20, value=st.session_state['depth_r'], disabled=(limit_mode_r == 'Time'))

        with e4:

            time_y = st.number_input("Yellow Time Limit (s)", min_value=0.1, max_value=60.0, value=float(st.session_state['time_y']), step=0.1, disabled=(limit_mode_y == 'Depth'))
            time_r = st.number_input("Red Time Limit (s)", min_value=0.1, max_value=60.0, value=float(st.session_state['time_r']), step=0.1, disabled=(limit_mode_r == 'Depth'))

    st.write("")

    if st.button(
        
        "Reset/Confirm Settings", 
        type='primary', 
        use_container_width=True

        ):
        
            st.session_state['VS'] = curr_VS
            st.session_state['RC'] = [int(max_rows), int(max_cols)]
            st.session_state['WC'] = WC
            st.session_state['max_hist'] = MH
            st.session_state['delay'] = ED

            st.session_state['alg'] = alg
            st.session_state['limit_mode'] = limit_mode
            st.session_state['depth_limit'] = depth_limit
            st.session_state['time_limit'] = time_limit
            st.session_state['play_first'] = FP_bool
            st.session_state['user_move'] = FP_bool if curr_VS == 'PvE' else True

            st.session_state['alg_y'] = alg_y
            st.session_state['limit_mode_y'] = limit_mode_y
            st.session_state['depth_y'] = depth_y
            st.session_state['time_y'] = time_y

            st.session_state['alg_r'] = alg_r
            st.session_state['limit_mode_r'] = limit_mode_r
            st.session_state['depth_r'] = depth_r
            st.session_state['time_r'] = time_r

            st.session_state['prev_move'] = []
            st.session_state['board'] = [['E' for _ in range(int(max_cols))] for _ in range(int(max_rows))]
            st.session_state['col_heights'] = [int(max_rows) - 1] * int(max_cols)
            st.session_state['curr_player'] = 'Y'
            st.session_state['history'] = []
            st.session_state['hist_idx'] = 0
            st.session_state['paused'] = True
            st.rerun()

    SC = (

        max_rows != st.session_state['RC'][0] or 
        max_cols != st.session_state['RC'][1] or 
        curr_VS != st.session_state['VS'] or 
        WC != st.session_state['WC'] or 
        MH != st.session_state['max_hist'] or 
        ED != st.session_state['delay'] or 
        alg != st.session_state['alg'] or 
        limit_mode != st.session_state['limit_mode'] or 
        depth_limit != st.session_state['depth_limit'] or 
        time_limit != st.session_state['time_limit'] or 
        FP_bool != st.session_state['play_first'] or 
        alg_y != st.session_state['alg_y'] or 
        limit_mode_y != st.session_state['limit_mode_y'] or 
        depth_y != st.session_state['depth_y'] or 
        time_y != st.session_state['time_y'] or 
        alg_r != st.session_state['alg_r'] or 
        limit_mode_r != st.session_state['limit_mode_r'] or 
        depth_r != st.session_state['depth_r'] or 
        time_r != st.session_state['time_r']
    
    )

    if SC:

        st.caption(":orange[:material/warning: Settings were modified. Confirm to reset.]")

#==================================================================================

st.title(

    ":red[Connect] :blue[4] :yellow[Engine]", 
    text_alignment='center'
    
)

@st.fragment
def RenderGameArea():

    won = WR.WINCHECKn(st.session_state['board'], st.session_state['prev_move'], st.session_state['WC'])

    status_placeholder = st.empty()
    disable_all_input = False

    if won != 'Continue':

        disable_all_input = True

        if st.session_state['VS'] == 'EvE':

            st.session_state['paused'] = True

        if won == 'Draw':

            status_placeholder.subheader(f"Game Over! :blue[Draw]")

        else:

            color = 'yellow' if won == 'Y' else 'red'
            status_placeholder.subheader(f"Game Over! :{color}[{color}] wins", text_alignment='center') 

    else:

        if (st.session_state['VS'] == 'PvE' and not st.session_state['user_move']) or st.session_state['VS'] == 'EvE':

            disable_all_input = True

    cols = st.columns(st.session_state['RC'][1])

    for c_idx, col in enumerate(cols):

        col_is_full = (st.session_state['col_heights'][c_idx] < 0)

        with col:

            st.button(

                f"DROP_COL_{c_idx}", 
                key=f"hidden_btn_{c_idx}", 
                disabled=(col_is_full or disable_all_input),
                on_click=ProcessMove, 
                args=(c_idx,)

            )

    cols_count = st.session_state['RC'][1]
    hover_bg = "rgba(255, 209, 102, 0.25)" if st.session_state['curr_player'] == 'Y' else "rgba(255, 75, 75, 0.25)"

    board_html = f"<div class='board-wrapper' style='--cols-count: {cols_count}; --hover-bg: {hover_bg};'><div class='board-scaler'><div class='board-container'>"

    for r in range(st.session_state['RC'][0]):

        for c in range(st.session_state['RC'][1]):

            val = st.session_state['board'][r][c]
            cell_class = "p1" if val == 'R' else ("p2" if val == 'Y' else "empty")

            if st.session_state['prev_move'] == [r, c]:

                cell_class += " last-move"

            board_html += f"<div class='cell {cell_class}'></div>"

    board_html += "</div><div class='click-overlays'>"

    for c in range(st.session_state['RC'][1]):

        col_is_full = (st.session_state['col_heights'][c] < 0)
        overlay_class = "col-overlay disabled" if (col_is_full or disable_all_input) else "col-overlay"
        board_html += f"<div class='{overlay_class}' data-col='{c}'></div>"

    board_html += "</div></div></div>"

    st.markdown(board_html, unsafe_allow_html=True)

    st.write("")

    undo_step = 2 if (st.session_state['VS'] == 'PvE' and st.session_state['user_move']) else 1
    remaining_redo = len(st.session_state['history']) - st.session_state['hist_idx']
    redo_step = min(undo_step, remaining_redo) if remaining_redo > 0 else undo_step
    max_undo_steps = st.session_state['max_hist'] * undo_step
    earliest_allowed_idx = max(0, len(st.session_state['history']) - max_undo_steps)

    can_undo = (st.session_state['max_hist'] > 0) and (st.session_state['hist_idx'] - undo_step >= earliest_allowed_idx)
    can_redo = (st.session_state['max_hist'] > 0) and (remaining_redo > 0)

    if st.session_state['VS'] == 'EvE':

        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

        with col_ctrl1:

            if st.button(
                
                "Undo Move", 
                use_container_width=True, 
                disabled=(not can_undo)
                
                ):
                
                    st.session_state['paused'] = True
                    ApplyHistoryStep(-undo_step)
                    st.rerun(scope="fragment")

        with col_ctrl2:

            if st.button(
                
                "Redo Move", 
                use_container_width=True, 
                disabled=(not can_redo)
                
                ):
                    
                    st.session_state['paused'] = True
                    ApplyHistoryStep(redo_step)
                    st.rerun(scope="fragment")

        with col_ctrl3:

            btn_label = ":material/play_arrow: Status: Paused (Click to Play)" if st.session_state['paused'] else ":material/pause: Status: Playing (Click to Pause)"

            if st.button(
                
                btn_label, 
                use_container_width=True, 
                type='primary' if st.session_state['paused'] else 'secondary'
                
                ):

                    st.session_state['paused'] = not st.session_state['paused']
                    st.rerun(scope="fragment")

    else:

        col_ctrl1, col_ctrl2 = st.columns(2)

        with col_ctrl1:

            if st.button(
                
                "Undo Move", 
                use_container_width=True, 
                disabled=(not can_undo)
                
                ):
                
                    ApplyHistoryStep(-undo_step)
                    st.rerun(scope="fragment")

        with col_ctrl2:

            if st.button(
                
                "Redo Move", 
                use_container_width=True, 
                disabled=(not can_redo)
                
                ):
                    
                    ApplyHistoryStep(redo_step)
                    st.rerun(scope="fragment")

    if won == 'Continue':

        if st.session_state['VS'] == 'PvE' and not st.session_state['user_move']:

            with status_placeholder.container():

                with st.spinner("Engine is thinking..."):

                    start_t = te.perf_counter()
                    EngineMove()
                    rem_delay = st.session_state['delay'] - (te.perf_counter() - start_t)

                    if rem_delay > 0:

                        te.sleep(rem_delay)

            st.rerun(scope="fragment")
            
        elif st.session_state['VS'] == 'EvE' and not st.session_state['paused']:

            with status_placeholder.container():

                with st.spinner(f"Player {st.session_state['curr_player']} Engine is thinking..."):
                    
                    start_t = te.perf_counter()
                    EngineMove()
                    rem_delay = st.session_state['delay'] - (te.perf_counter() - start_t)

                    if rem_delay > 0:

                        te.sleep(rem_delay)

            st.rerun(scope="fragment")

RenderGameArea()