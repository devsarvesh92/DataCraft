import logging

import pandas as pd
import streamlit as st


def process_user_query(input_string: str):
    logging.log(logging.INFO, f"Processing user query: {input_string}")
    return "I am a bot"


def identify_schema():
    # using model identify schema
    pass


def build_query(text_input: str):
    # using chatgpt, build query
    pass


def execute_query(query: str) -> pd.DataFrame:
    # execute query on aws athena
    pass


st.set_page_config(
    page_title="DataCraft",
    layout="wide"
)
st.title("DataCraft")

if 'user_messages' not in st.session_state:
    st.session_state['user_messages'] = []

if 'bot_messages' not in st.session_state:
    st.session_state['bot_messages'] = []

user_input = st.chat_input(placeholder='How can I help you?')

if user_input:
    st.session_state['user_messages'].append(user_input)

    bot_response = process_user_query(input_string=user_input)
    st.session_state['bot_messages'].append(bot_response)

for user_message, bot_message in zip(st.session_state.user_messages, st.session_state.bot_messages):
    with st.chat_message("user"):
        st.write(f"{user_message}")

    with st.chat_message("bot"):
        st.write(f"{bot_message}")
