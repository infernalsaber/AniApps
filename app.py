import streamlit as st
import asyncio

from aniplots import main_plots
from ani3x3 import main3x3


app_mode = st.sidebar.selectbox('Select Application',['Plot','Anilist 3x3'])

if app_mode=='Plot':    
    asyncio.run(main_plots())
elif app_mode == 'Anilist 3x3':
    asyncio.run(main3x3())