import json
import streamlit as st
from openai import OpenAI


def stream_response(client, model, messages_dict, answer_element, temperature, max_tokens, top_p, repetition_penalty):
	stream = client.chat.completions.create(
		model=model,
		messages=[
			{"role": m["role"], "content": m["content"]}
			for m in messages_dict
		],
        frequency_penalty=repetition_penalty,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
		stream=True
		)
	answer = ""
	for chunk in stream:
		chunk_content = chunk.choices[0].delta.content
		if chunk_content:
			answer += chunk_content 
			answer_element.markdown(answer)
	st.session_state.chat_history.append({"role": "assistant", "content": answer})


with open("config.json", "r") as f:
    config = json.load(f)
services = config.keys()

st.set_page_config(page_title="Simple ChatUI")
st.title("Simple ChatUI")
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Sidebar
st.sidebar.title("Settings")
service = st.sidebar.selectbox("Select API provider", services)
models = config[service]["models"]
model = st.sidebar.selectbox("Select LLM", models)

# Model settings
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=2.0, step=0.01, value=0.5)
max_tokens = st.sidebar.number_input("Max tokens", value=1024)
top_p = st.sidebar.slider("Top p", min_value=0.0, max_value=1.0, step=0.01, value=1.0)
repetition_penalty = st.sidebar.slider("Repetition penalty", min_value=0.0, max_value=2.0, step=0.01, value=1.05)
if st.sidebar.button("New chat"):
    st.session_state["chat_history"] = []

api_key = config[service]["api_key"]
url = config[service]["completions_endpoint"]
client = OpenAI(base_url=url, api_key=api_key)

# Chat section
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message LLM"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        answer_box = st.empty()
    stream_response(client, model, st.session_state.chat_history, answer_box, temperature, max_tokens, top_p, repetition_penalty)
