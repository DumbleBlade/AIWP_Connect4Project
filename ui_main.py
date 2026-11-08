import streamlit as st
import time
import copy
from ALPHABETA import AB
from MINMAX import MM
from AC3 import AC
from WINCHECKER import WINCHECK

st.set_page_config( page_title = "Connect 4 AI", layout = "centered" )

st.html(
    """
    <style>

        [data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }

        header[data-testid="stHeader"] {
            display: none !important;
        }

        div[data-testid="stMainBlockContainer"] {
            padding-left: 0.2rem;
            padding-right: 0.2rem;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
    """
)

st.markdown( 

    f"""
    <style>
        .board-container {{
            display: grid;
            grid-template-columns: repeat({st.session_state.get('cols', 7)}, 1fr);
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
        .p1 {{ background-color: #ff4b4b; box-shadow: inset 0 -3px 6px rgba(0,0,0,0.3); }} 
        .p2 {{ background-color: #ffd166; box-shadow: inset 0 -3px 6px rgba(0,0,0,0.3); }} 
        
        div[data-testid="column"] button {{
            width: 100%;
            border-radius: 8px;
            font-size: 1.2rem;
        }}
    </style>
    """, 
    unsafe_allow_html = True 

)


def init_game():
    
    st.session_state.board = [ [ "E" ] * st.session_state.cols for _ in range( st.session_state.rows ) ]
    st.session_state.history = []
    st.session_state.current_player = 1
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.eve_paused = True 


if 'board' not in st.session_state:
    
    st.session_state.rows = 6
    st.session_state.cols = 7
    st.session_state.win_length = 4
    init_game()


def make_move( row, col, player ):
    
    st.session_state.history.append( {
        "board": copy.deepcopy( st.session_state.board ),
        "player": st.session_state.current_player
    } )
    
    st.session_state.board[ row ][ col ] = player
    
    status = WINCHECK( st.session_state.board )
    
    if status == 1:
        
        st.session_state.game_over = True
        st.session_state.winner = player
        
    elif status == 0:
        
        st.session_state.game_over = True
        st.session_state.winner = 0
        
    else:
        
        st.session_state.current_player = 3 - player


def undo_move( steps = 1 ):
    
    for _ in range( steps ):
        
        if st.session_state.history:
            
            last_state = st.session_state.history.pop()
            st.session_state.board = last_state[ "board" ]
            st.session_state.current_player = last_state[ "player" ]
            st.session_state.game_over = False
            st.session_state.winner = None


def get_lowest_empty_row( col ):
    
    for r in range( st.session_state.rows - 1, - 1, - 1 ):
        
        if st.session_state.board[ r ][ col ] == "E":
            
            return r
            
    return - 1


def execute_engine_move( algo_name ):
    
    algo_map = { "Alpha Beta Minimax": AB, "Minimax": MM, "AC3": AC }
    
    engine_func = algo_map[ algo_name ]
    
    engine_r, c = engine_func( st.session_state.board, st.session_state.current_player )
    
    actual_r = get_lowest_empty_row( c )
    
    if actual_r != - 1:
        
        make_move( actual_r, c, st.session_state.current_player )
        
    else:
        
        st.error( f"Engine tried to play in column {c}, but it is full!" )
        st.session_state.eve_paused = True


st.title( "Connect 4 Engine" )


with st.expander( "Game Settings", expanded = False ):
    
    c1, c2, c3 = st.columns( 3 )
    
    new_rows = c1.number_input( "Rows", min_value = 4, max_value = 12, value = st.session_state.rows )
    new_cols = c2.number_input( "Columns", min_value = 4, max_value = 12, value = st.session_state.cols )
    new_win = c3.number_input( "Win Connection Length", min_value = 3, max_value = max(new_rows, new_cols), value = st.session_state.win_length )
    
    c4, c5 = st.columns( 2 )
    
    mode = c4.selectbox( "Game Mode", [ "Player vs Player", "Engine vs Player", "Engine vs Engine" ] )
    algo = c5.selectbox( "Engine Algorithm", [ "Alpha Beta Minimax", "Minimax", "AC3" ] )
    
    if st.button( "Restart / Apply Settings", use_container_width = True ):
        
        st.session_state.rows = new_rows
        st.session_state.cols = new_cols
        st.session_state.win_length = new_win
        init_game()
        st.rerun()


ctrl_col1, ctrl_col2, ctrl_col3 = st.columns( 3 )


if mode == "Engine vs Engine":
    
    with ctrl_col1:
        
        btn_label = "Resume" if st.session_state.eve_paused else "Pause"
        
        if st.button( btn_label, key = "pause_resume_btn", use_container_width = True ):
            
            st.session_state.eve_paused = not st.session_state.eve_paused
            st.rerun()
            
    with ctrl_col2:
        
        if st.button( "Next Move", disabled = not st.session_state.eve_paused or st.session_state.game_over, use_container_width = True ):
            
            execute_engine_move( algo )
            st.rerun()
            
    with ctrl_col3:
        
        if st.button( "Prev Move", disabled = len( st.session_state.history ) == 0, use_container_width = True ):
            
            undo_move( 1 )
            st.session_state.eve_paused = True 
            st.rerun()


elif mode == "Engine vs Player":
    
    with ctrl_col1:
        
        can_undo = len( st.session_state.history ) >= 2 or ( len( st.session_state.history ) == 1 and st.session_state.current_player == 2 )
        
        if st.button( "Go Back Move", disabled = not can_undo, use_container_width = True ):
            
            steps_to_undo = 2 if st.session_state.current_player == 1 and len( st.session_state.history ) >= 2 else 1
            undo_move( steps_to_undo )
            st.rerun()


st.write( "" ) 


is_human_turn = not st.session_state.game_over and ( mode == "Player vs Player" or ( mode == "Engine vs Player" and st.session_state.current_player == 1 ) )


if is_human_turn:
    
    drop_cols = st.columns( st.session_state.cols, gap = "small" )
    
    for c in range( st.session_state.cols ):
        
        with drop_cols[ c ]:
            
            col_full = st.session_state.board[ 0 ][ c ] != "E"
            
            if st.button( "Drop", key = f"drop_{c}", disabled = col_full, use_container_width = True ):
                
                r = get_lowest_empty_row( c )
                
                if r != - 1:
                    
                    make_move( r, c, st.session_state.current_player )
                    st.rerun()
                    
else:
    
    st.markdown( "<div style='height: 48px;'></div>", unsafe_allow_html = True )


board_html = "<div class='board-container'>"

for r in range( st.session_state.rows ):
    
    for c in range( st.session_state.cols ):
        
        val = st.session_state.board[ r ][ c ]
        cell_class = "empty"
        
        if val == 1 or val == "1":
            
            cell_class = "p1"
            
        elif val == 2 or val == "2":
            
            cell_class = "p2"
            
        board_html += f"<div class='cell {cell_class}'></div>"
        
board_html += "</div>"


st.markdown( board_html, unsafe_allow_html = True )


st.write( "---" )


if st.session_state.game_over:
    
    if st.session_state.winner == 0:
        
        st.info( "It's a Draw!" )
        
    else:
        
        color = "Red" if st.session_state.winner == 1 else "Yellow"
        st.success( f"Player {st.session_state.winner} ({color}) Wins!" )
        
else:
    
    color = "Red" if st.session_state.current_player == 1 else "Yellow"
    st.markdown( f"**Current Turn:** Player {st.session_state.current_player} ({color})" )


if not st.session_state.game_over:
    
    if mode == "Engine vs Engine" and not st.session_state.eve_paused:
        
        time.sleep( 0.5 ) 
        execute_engine_move( algo )
        st.rerun()
        
    elif mode == "Engine vs Player" and st.session_state.current_player == 2:
        
        with st.spinner( "Engine is thinking..." ):
            
            time.sleep( 0.2 )
            execute_engine_move( algo )
            st.rerun()