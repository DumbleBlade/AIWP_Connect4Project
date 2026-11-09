import streamlit as st
import random

def MM():

    grid = st.session_state['board']

    valid_cols = [c for c in range(len(grid[0])) if grid[0][c] == "E"]
  
    return random.choice(valid_cols)