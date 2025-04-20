import os
import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO


# page names
WELCOME_PAGE = "welcome"
HOME_PAGE = "home"
CHAT_PAGE = "chat"
SINGLE_EXAMPLE_PAGE = "single"
MULTIPLE_EXAMPLES_PAGE = "multiple"
MANUAL_PAGE = "manual"

HOME_EMOJI = ":house:"
HOME_BUTTON_TEXT = f"{HOME_EMOJI} Back Home"
LLM_EMOJI = ":robot_face:"


def get_api_key():
    try:
        api_key = st.secrets["TOGETHER_API_KEY"]
    except KeyError:
        try:
            api_key = os.environ["TOGETHER_API_KEY"]
        except KeyError:
            raise KeyError("An API key is required to run this app.")
    return api_key


# Dummy parse_text function
def parse_text(text, api_key=None):
    # Replace this with your real implementation
    return f"Parsed result for: {text.strip()}"


# Load authorized users from file
def load_users():
    return Path("authorized_users.txt").read_text().splitlines()  # it strips whitespaces


def welcome_page():
    st.title("Welcome to the Experiment Parser")
    users = load_users()
    selected_user = st.selectbox("Select your user name", users + ["New user"])

    if selected_user == "New user":
        st.warning("Please contact our lab for permissions.")
        st.stop()

    password = st.text_input("Enter your password", type="password")

    if password:
        if st.button("Continue"):
            expected_password = st.secrets["passwords"].get(selected_user)
            if expected_password and password == expected_password:
                st.session_state.user = selected_user
                st.session_state.page = HOME_PAGE
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
    else:
        st.info("Enter your password to continue.")

    # api_key = st.text_input("Enter your key", type="password")
    #
    # if api_key:
    #     if st.button("Continue"):
    #         st.session_state.user = selected_user
    #         st.session_state.api_key = api_key
    #         st.session_state.page = HOME_PAGE
    #         st.rerun()
    # else:
    #     st.info("Enter your key to continue.")


def home_page():
    st.title(f"LLM-Assisted Coding - Home Page {HOME_EMOJI}")
    columns = st.columns(4)
    if columns[0].button("Chat with our LLM directly"):
        st.session_state.page = CHAT_PAGE
        st.rerun()
    if columns[1].button("Code a single example"):
        st.session_state.page = SINGLE_EXAMPLE_PAGE
        st.rerun()
    if columns[2].button("Code multiple examples"):
        st.session_state.page = MULTIPLE_EXAMPLES_PAGE
        st.rerun()
    if columns[3].button("Manually control the coding parameters"):
        st.session_state.page = MANUAL_PAGE
        st.rerun()


def single_example_page():
    st.title("Code a Single Example")
    example_text = st.text_area("Paste your experiment summary")
    if st.button("Code"):
        result = parse_text(example_text)
        st.subheader("Parsed Result")
        st.code(result, language=None)  # using st.code to have a built-in copy button
    if st.button(HOME_BUTTON_TEXT):
        st.session_state.page = HOME_PAGE
        st.rerun()


def multiple_examples_page():
    st.title("Code Multiple Examples")

    input_mode = st.radio("Choose input method", ["Paste text", "Upload file"])
    examples = []

    if input_mode == "Paste text":
        multi_text = st.text_area("Paste multiple summaries, separated by line breaks")
        if multi_text:
            examples = [line.strip() for line in multi_text.splitlines() if line.strip()]
        input_format = "Plain text"

    else:  # input_mode == "Upload file":
        uploaded_file = st.file_uploader("Upload a TXT, CSV, or XLSX file",
                                         type=["txt", "csv", "xlsx"])
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                examples = df.iloc[:, 0].dropna().astype(str).tolist()
                input_format = "CSV"
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                examples = df.iloc[:, 0].dropna().astype(str).tolist()
                input_format = "XLSX"
            else:  # ends with ".txt"
                content = uploaded_file.read().decode("utf-8")
                examples = [line.strip() for line in content.splitlines() if line.strip()]
                input_format = "TXT"

    output_format = st.radio("Choose output format",
                             ["Same as input", "Plain text", "TXT", "CSV", "XLSX"], index=0)

    if st.button("Code Examples"):
        if examples:
            results = [parse_text(example) for example in examples]
            if output_format == "Same as input":
                output_format = input_format
            if output_format == "Plain text":
                st.subheader("Results")
                displayed_results = "\n".join([f"{result}" for result in results])
                st.code(displayed_results, language=None)  # same reason for st.code from previous
            else:
                df = pd.DataFrame({"Input": examples, "Parsed Result": results})
                if output_format == "CSV":
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download CSV", csv, "results.csv", "text/csv")
                elif output_format == "XLSX":
                    xlsx_buffer = BytesIO()
                    with pd.ExcelWriter(xlsx_buffer, engine="xlsxwriter") as writer:
                        df.to_excel(writer, index=False, sheet_name="Parsed Results")
                    st.download_button("Download XLSX", xlsx_buffer.getvalue(), "results.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                elif output_format == "TXT":
                    txt = "\n".join(results).encode("utf-8")
                    st.download_button("Download TXT", txt, "results.txt", "text/plain")
                st.dataframe(df)

    if st.button(HOME_BUTTON_TEXT):
        st.session_state.page = HOME_PAGE
        st.rerun()


def manual_page():
    st.title("Manually Control the Coding Parameters")
    st.info(":construction_worker: This page is still under construction...")
    if st.button(HOME_BUTTON_TEXT):
        st.session_state.page = HOME_PAGE
        st.rerun()


def chat_with_llm(user_message, history=None):
    # Placeholder LLM call (replace with your real HuggingChat/LLM call)
    return f"You said '{user_message}', and I’m responding intelligently."


def chat_page():
    st.title(f"Chat with the Lab's LLM {LLM_EMOJI}")
    st.markdown("Welcome to the chat interface!  "
                "Use this page to interact with our proprietary LLM.  "
                "Use :keyboard: ***Enter*** to send your message and get an answer.")

    # Initialize chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f":blue-background[**You:**] {message['content']}")
        else:
            st.markdown(f":violet-background[**LLM:**] {message['content']}")

    # User input area
    def submit():
        if "user_input" not in st.session_state:
            st.session_state["user_input"] = ""
        st.session_state["user_input"] = st.session_state["chat_input"]
        st.session_state["chat_input"] = ""
        user_input = st.session_state["user_input"]
        if user_input.strip():
            # Append user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            # Call LLM and append its response
            llm_response = chat_with_llm(user_input, history=st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "llm", "content": llm_response})

            # # Clear input field  # TODO maybe remove?
            # st.session_state.chat_input = ""

            # # Rerun to show updated messages  # TODO trying with no rerun
            # st.rerun()

    # user_input = st.text_input("Your message:", key="chat_input", on_change=submit) # TODO maybe remove?
    st.text_input("Your message:", key="chat_input", on_change=submit)
    # if st.button("Send"):  # TODO: trying with no button
    #     submit()

    if st.button(HOME_BUTTON_TEXT):
        st.session_state.page = "home"
        st.session_state.chat_history = []  # Optional: clear chat on exit
        st.rerun()


# Entry point
def main():
    if "page" not in st.session_state:
        st.session_state.page = WELCOME_PAGE

    page = st.session_state.page

    if page == WELCOME_PAGE:
        welcome_page()
    elif page == HOME_PAGE:
        home_page()
    elif page == CHAT_PAGE:
        chat_page()
    elif page == SINGLE_EXAMPLE_PAGE:
        single_example_page()
    elif page == MULTIPLE_EXAMPLES_PAGE:
        multiple_examples_page()
    elif page == MANUAL_PAGE:
        manual_page()


if __name__ == "__main__":
    main()
