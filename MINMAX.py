import streamlit as st
import random

def MM(grid, player):

    valid_cols = [c for c in range(len(grid[0])) if grid[0][c] == "E"]
    
    if not valid_cols:
        return 0, 0  
        
    return 0, random.choice(valid_cols)