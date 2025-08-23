import streamlit as st

flex = st.container(horizontal=True,)

for card in range(3):
    flex.button(f"Button {card + 1}")
    


col1, col2, col3 = st.columns(3)

with col1:
    card1 = st.container(border=True, key=None, width="stretch", height="content", horizontal=True, horizontal_alignment="center", vertical_alignment="top", gap="small")
    card1.write("This is a card with a border.")
    
with col2:
    card2 = st.container(border=True, key=None, width="stretch", height="content", horizontal=True, horizontal_alignment="center", vertical_alignment="top", gap="small")
    card2.write("This is a card with a border.")
    
with col3:
    card3 = st.container(border=True, key=None, width="stretch", height="content", horizontal=True, horizontal_alignment="center", vertical_alignment="top", gap="small")
    card3.write("This is a card with a border.")
    

