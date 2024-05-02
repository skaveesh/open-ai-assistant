import os
from dotenv import load_dotenv
import openai
import pickler
import time
import streamlit as st

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-turbo"

# == Hardcoded ids to be used once the first code run is done and the assistant was created
asst_id = os.getenv("OPENAI_ASST_ID")
vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")
thread_id = ""  # This will be set when the chat starts

# Initialize all the session
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list = []

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# Set up our front end page
st.set_page_config(page_title="ALM GPT - Chat and Learn", page_icon=":books:")


# ==== Function definitions etc =====
def upload_to_openai(filepath):
    with open(filepath, "rb") as file:
        response = client.files.create(file=file, purpose="assistants", )

    return response.id


# === Sidebar - where users can upload files
file_uploaded = st.sidebar.file_uploader(
    "Upload a file to be transformed into embeddings", key="file_upload"
)

# List down files in Vector Store
vector_store_files = client.beta.vector_stores.files.list(vector_store_id=vector_store_id)
st.sidebar.write("Existing Files:")
for vs_file in vector_store_files:
    file_name = pickler.get_file_name(vs_file.id)
    if file_name != "not found":
        st.sidebar.write(file_name)

# Upload file button - store the file ID
if st.sidebar.button("Upload File") and file_uploaded:
    with open(f"{file_uploaded.name}", "wb") as f:
        f.write(file_uploaded.getbuffer())
    another_file_id = upload_to_openai(f"{file_uploaded.name}")
    st.session_state.file_id_list.append(another_file_id)
    st.sidebar.write(f"File ID:: {another_file_id}")
    # Store in picker
    pickler.add_item(another_file_id, file_uploaded.name)

# Display those file ids
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded File IDs:")

    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id)

        # Create vector store file
        vector_store_file = client.beta.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id
        )

# Button to initiate the chat session
if st.sidebar.button("Start Chatting..."):
    st.session_state.start_chat = True
    # Create a new thread for this chat session
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id
    st.write("Thread ID:", chat_thread.id)


# Define the function to process messages with citations
def process_response_with_citations(response):
    message_content = response.content[0].text
    annotations = message_content.annotations
    citations = []
    for index, annotation in enumerate(annotations):
        message_content.value = message_content.value.replace(
            annotation.text, f"[{index}]"
        )
        if file_citation := getattr(annotation, "file_citation", None):
            cited_file = client.files.retrieve(file_citation.file_id)
            citations.append(f"[{index}] {cited_file.filename}")

    response_with_citation = message_content.value + "\n\n" + "\n".join(citations)
    return response_with_citation


# the main interface ...
st.image('alm_gpt_bg_blk.png', caption='Powered by OpenAI gpt-4-turbo')
st.write("Learn fast by chatting with your documents")


# Check sessions
if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = model
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show existing messages if any...
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat input for the user
    if prompt := st.chat_input("What's new?"):
        # Add user message to the state and display on the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id, role="user", content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=asst_id,
            instructions="""Please answer the questions using the knowledge provided in the files.
            when adding additional information, make sure to distinguish it with bold or underlined text.""",
        )

        # Show a spinner while the assistant is thinking...
        with st.spinner("Wait... Generating response..."):
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id, run_id=run.id
                )
            # Retrieve messages added by the assistant
            messages = client.beta.threads.messages.list(
                thread_id=st.session_state.thread_id
            )
            # Process and display asst messages
            assistant_messages_for_run = [
                message
                for message in messages
                if message.run_id == run.id and message.role == "assistant"
            ]

            for message in assistant_messages_for_run:
                full_response = process_response_with_citations(response=message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)

    else:
        # Prompt users to start chat
        st.write(
            "Please upload at least a file to get started by clicking on the 'Start Chat' button"
        )
