# How to run this application
1. Get the OpenAI API key from [OpenAI](https://platform.openai.com/)
2. Create ChatGPT Assistant and Vector Store on OpenAI
3. Define these environment variables in `.env` file by replacing `XXXX` with the actual values
    ```bash
    OPENAI_API_KEY=XXXX
    OPENAI_ASST_ID=XXXX
    OPENAI_VECTOR_STORE_ID=XXXX
    ```
4. Create Python virtual environment
    ```bash
    python3 -m venv knowledgenv
    ```
5. Activate the virtual environment
    1. On Windows
        ```bash
        .\knowledgenv\Scripts\activate
        ```
    2. On Linux
        ```bash
        source knowledgenv/bin/activate
        ```
6. Install requirements
    ```bash
    pip install -r .\requirements.txt
    ```
7. Run the application
    ```bash
    streamlit run main.py 
    ```