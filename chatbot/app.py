import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from predibase import Predibase
import os
from dotenv import load_dotenv
load_dotenv()

st.title('Chatbot')
st.write("Please select your course")
course = st.selectbox('Course', ['Database System', 'Jeju Island'])

pb = Predibase(api_token=os.getenv("PREDIBASE_API_KEY"))
lorax_client = pb.deployments.client("solar-1-mini-chat-240612")

if course == 'Database System':
    adapter_id = 'news-database_system-model/3'


def  get_response(user_input, chat_history):
    message_content = ""
    for message in chat_history:
        if isinstance(message, HumanMessage):
            message_content += f"<|im_start|>user\n {message.content} <|im_end|>\n"
        elif isinstance(message, AIMessage):
            message_content += f"<|im_start|>assistant\n {message.content} <|im_end|>\n"
        
    input_prompt = f"""{message_content} <|im_start|>user\n {user_input} <|im_end|>\n<|im_start|>assistant\n"""
    
    for response in lorax_client.generate_stream(input_prompt, adapter_id=adapter_id, max_new_tokens=1000):
        res = response.token.text
        if res != '<|im_end|>' and res != '<|im_start|>':
            yield res

# Streamlit chat
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)



# Chat input
user_input = st.chat_input("Your message")
if user_input is not None and user_input != "":

    with st.chat_message("Human"):
        st.markdown(user_input)

    with st.chat_message("AI"):
        response = st.write_stream(get_response(user_input, st.session_state.chat_history))
    
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    st.session_state.chat_history.append(AIMessage(content=response))
