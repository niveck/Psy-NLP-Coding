import os
import time

import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

from generating_with_together import code_text, generate_for_chat, save_generation_log
from prompts import EXAMPLE_OUTPUT_BY_FREE_MODEL, CHAT_SYSTEM_PROMPT

# page names
WELCOME_PAGE = "welcome"
HOME_PAGE = "home"
CHAT_PAGE = "chat"
SINGLE_MEMORY_PAGE = "single"
MULTIPLE_MEMORIES_PAGE = "multiple"
MANUAL_PAGE = "manual"
DEBUG_PAGE = "debug"

# visuals
# emojis shortcuts link: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
HOME_EMOJI = ":house:"
HOME_BUTTON_TEXT = f"{HOME_EMOJI} Back Home"
LLM_EMOJI = ":robot_face:"
ENTER_KEYBOARD_EMOJI = ":leftwards_arrow_with_hook:"  # :keyboard:
SINGLE_MEMORY_EMOJI = ":green_book:"
MULTIPLE_MEMORIES_EMOJI = ":books:"
MANUAL_EMOJI = ":mechanical_arm:"
CLEAR_HISTORY_EMOJI = ":put_litter_in_its_place:"  # ":recycle:", ":wastebasket:", ":broom:", ":x:"
DEBUG_EMOJI = ":hammer_and_wrench:"
CLASS_COLORS = {"int": "blue", "ext": "gray"}
VALENCE_COLORS = {"neg": "red", "neu": "orange", "posit": "green"}
FORMATTED_CODES = {f"_{cls}_{vln}_":
                       f":{cls_color}-background[:{vln_color}[***\\_{cls}\\_{vln}\\_***]]"
                   for cls, cls_color in CLASS_COLORS.items()
                   for vln, vln_color in VALENCE_COLORS.items()}
COLOR_CODING_LEGEND = ("**Color coding legend:** "
                       + ", ".join([f":{cls_color}-background[{cls}]"
                                    for cls, cls_color in CLASS_COLORS.items()]
                                   + [f":{vln_color}[{vln}]"
                                      for vln, vln_color in VALENCE_COLORS.items()]))

CONTACT_SUPPORT_MESSAGE = f"For additional support you can email: niv.eckhaus@mail.huji.ac.il"


def get_api_key():
    try:
        api_key = st.secrets["TOGETHER_API_KEY"]
    except KeyError:
        try:
            api_key = os.environ["TOGETHER_API_KEY"]
        except KeyError:
            raise KeyError("An API key is required to run this app.")
    return api_key


def get_list_of_lines_from_file(file_name):
    return Path(file_name).read_text().splitlines()  # strips whitespaces


def load_users():
    return get_list_of_lines_from_file("authorized_users.txt")


def get_developer_users():
    return get_list_of_lines_from_file("developer_users.txt")


def page_bottom():
    """
    Create the Home button and the message about contacting support
    """
    if st.button(HOME_BUTTON_TEXT):
        st.session_state.page = HOME_PAGE
        st.rerun()
    st.caption(CONTACT_SUPPORT_MESSAGE)


def welcome_page():
    st.title("Welcome to the Memory Coder &mdash; BETA")
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

    st.caption(CONTACT_SUPPORT_MESSAGE)

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
    st.title(f"{HOME_EMOJI} LLM-Assisted Coding &mdash; Home Page &mdash; BETA")
    columns = st.columns(4)
    if columns[0].button(f"Code a single memory {SINGLE_MEMORY_EMOJI}"):
        st.session_state.page = SINGLE_MEMORY_PAGE
        st.rerun()
    if columns[1].button(f"Code multiple memories {MULTIPLE_MEMORIES_EMOJI}"):
        st.session_state.page = MULTIPLE_MEMORIES_PAGE
        st.rerun()
    if columns[2].button(f"Chat with our LLM directly {LLM_EMOJI}"):
        st.session_state.page = CHAT_PAGE
        st.rerun()
    if columns[3].button(f"Manually control parameters {MANUAL_EMOJI}"):
        st.session_state.page = MANUAL_PAGE
        st.rerun()
    if "user" in st.session_state and st.session_state.user in get_developer_users():
        if st.button(f"Debug page {DEBUG_EMOJI}"):
            st.session_state.page = DEBUG_PAGE
            st.rerun()
    st.caption(CONTACT_SUPPORT_MESSAGE)


def format_coded_result(result):
    for code, formatted_code in FORMATTED_CODES.items():
        result = result.replace(code, formatted_code)
    return result


def single_memory_page():
    st.title(f"{SINGLE_MEMORY_EMOJI} Code a Single Memory")
    memory_text = st.text_area("Paste the memory you want to code")
    if st.button("Code") and memory_text:  # TODO this and might be problematic
        try:
            with st.spinner("Model generating your coded result..."):
                result, message_history, generation_log = code_text(memory_text)
                save_generation_log(single_generation_log=generation_log)
        except Exception as e:
            handle_generation_error(e)
        else:
            st.subheader("Coded result &mdash; color coded and highlighted")
            st.caption(COLOR_CODING_LEGEND)
            st.markdown(format_coded_result(result))
            st.subheader("Coded result &mdash; as plain text with copy button")
            st.code(result, language=None)  # using st.code to have a built-in copy button
    page_bottom()


def handle_generation_error(error):
    st.info("Connection to the model has crashed...")
    st.warning("You can send us the following error message: "
               "**(and then refresh the page)**")
    st.error(error)


def multiple_memories_page():
    st.title(f"{MULTIPLE_MEMORIES_EMOJI} Code Multiple Memories")

    input_mode = st.radio("Choose input method", ["Paste text", "Upload file"])
    memories = []

    if input_mode == "Paste text":
        multi_text = st.text_area("Paste multiple memories, separated by line breaks")
        if multi_text:
            memories = [line.strip() for line in multi_text.splitlines() if line.strip()]
        input_format = "Plain text"
    else:  # input_mode == "Upload file":
        uploaded_file = st.file_uploader("Upload a TXT, CSV, or XLSX file",
                                         type=["txt", "csv", "xlsx"])
        if uploaded_file:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                memories = df.iloc[:, 0].dropna().astype(str).tolist()
                input_format = "CSV"
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
                memories = df.iloc[:, 0].dropna().astype(str).tolist()
                input_format = "XLSX"
            else:  # ends with ".txt"
                content = uploaded_file.read().decode("utf-8")
                memories = [line.strip() for line in content.splitlines() if line.strip()]
                input_format = "TXT"

    output_format = st.radio("Choose output format",
                             ["Same as input", "Plain text", "TXT", "CSV", "XLSX"], index=0)

    if st.button("Code Memories") and memories:
        try:
            with st.spinner("Model generating your coded results..."):
                results, logs = [], []
                for memory in memories:
                    result, message_history, generation_log = code_text(memory)
                    results.append(result)
                    logs.append(generation_log)
                save_generation_log(multiple_generation_logs=logs)
        except Exception as e:
            handle_generation_error(e)
        else:
            if output_format == "Same as input":
                output_format = input_format
            if output_format == "Plain text":
                st.subheader("Results")
                displayed_results = "\n".join([f"{result}" for result in results])
                st.code(displayed_results, language=None)  # same reason for st.code from previous
            else:
                df = pd.DataFrame({"Input": memories, "Parsed Result": results})
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

    page_bottom()


def manual_page():
    st.title(f"{MANUAL_EMOJI} Manually Control the Coding Parameters")
    st.info(":construction_worker: This page is still under construction...")
    page_bottom()

def chat_with_llm(user_message, history=None):
    # Placeholder LLM call (replace with your real HuggingChat/LLM call)
    return f"You said '{user_message}', and I’m responding intelligently."


def chat_page():
    st.title(f"{LLM_EMOJI} Chat with the Lab's LLM")
    st.markdown("Welcome to the chat interface!  \n"
                "Use this page to interact with our proprietary LLM.")
    st.caption(f"Use the ***Enter*** {ENTER_KEYBOARD_EMOJI} key to send your message and get an answer.")

    # Initialize chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]

    # Display chat history
    for message in st.session_state.chat_history:
        content = message["content"].replace("_", "\\_")
        if message["role"] == "user":
            st.markdown(f":blue-background[**You:**] {content}")
        elif message["role"] == "assistant":
            st.markdown(f":violet-background[**LLM:**] {content}")
        else:  # message["role"] == "system"
            continue

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
            try:
                with st.spinner("Model generating an answer for you..."):
                    generate_for_chat(st.session_state.chat_history)
            except Exception as e:
                st.info("Connection to the model has crashed...\n"
                        "You should refresh the page, "
                        "but maybe **first save a copy of the conversation so far**")
                st.error(e)

            # TODO: remove this if real LLM chat works!
            # # Call LLM and append its response
            # llm_response = chat_with_llm(user_input, history=st.session_state.chat_history)
            # st.session_state.chat_history.append({"role": "assistant", "content": llm_response})

            # # Clear input field  # TODO maybe remove?
            # st.session_state.chat_input = ""

            # # Rerun to show updated messages  # TODO trying with no rerun
            # st.rerun()

    # user_input = st.text_input("Your message:", key="chat_input", on_change=submit) # TODO maybe remove?
    st.text_input("Your message:", key="chat_input", on_change=submit)
    # if st.button("Send"):  # TODO: trying with no button
    #     submit()

    # if st.session_state.chat_history:
    #     if st.button("Clear chat history ::"):

    # TODO: in the following section there used to be clearing of chat_history...

    # if st.button(HOME_BUTTON_TEXT):
    #     st.session_state.page = HOME_PAGE
    #     st.session_state.chat_history = []  # Optional: clear chat on exit
    #     st.rerun()

    page_bottom()


# Entry point
def debug_page():
    """
    check: st.dialog, st.help, st.feedback, st.chat_message, st.chat_input, st.warning vs st.error
    """
    st.title(f"{DEBUG_EMOJI} This page is for debugging purposes, as a user you can ignore it")
    st.info("Trying the color coding with the example output...")
    st.caption(COLOR_CODING_LEGEND)
    st.markdown(format_coded_result(EXAMPLE_OUTPUT_BY_FREE_MODEL))

    conn = st.connection("gsheets", type=GSheetsConnection)
    st.code(dir(conn))
    old_df = conn.read(ttl=0)
    st.caption("This is the old DF before adding a row: (after third)")
    # print("This is the old DF before adding a row: (after third)")
    st.write(old_df)
    # print(old_df)
    # new_row = [1, "n", "free", "first input", "YAY!"]
    new_row = [2, "n", "free", "second input", "PRAYYYY"]
    # new_row = [3, "n", "free", "third input", "PLEASE READ IT!"]
    # new_row = [4, "n", "free", "forth input", "4444"]
    # new_df = pd.DataFrame([new_row], columns=["timestamp", "user", "model", "input", "output"])
    # conn.update(data=new_df)
    old_df.loc[len(old_df)] = new_row
    conn.update(data=old_df)
    conn.reset()
    # st.code(help(conn.update))
    # st.code(help(conn.read))
    # help(conn.reset)


    # # TODO: this is claude's suggestion:
    # conn = st.connection("gsheets", type=GSheetsConnection)
    # old_df = conn.read(ttl=0)
    # st.caption("This is the DF after changing to wait_timestamp")
    # st.write(old_df)
    #
    # # # Create new row
    # # new_row = [3, "n", "free", "third input", "PLEASE READ IT!"]
    # # new_df = pd.DataFrame([new_row], columns=["timestamp", "user", "model", "input", "output"])
    # #
    # # # Append the new row to the existing data
    # # combined_df = pd.concat([old_df, new_df], ignore_index=True)
    # #
    # # # Update with the combined data
    # # conn.update(data=combined_df)
    # conn.reset()

    page_bottom()


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
    elif page == SINGLE_MEMORY_PAGE:
        single_memory_page()
    elif page == MULTIPLE_MEMORIES_PAGE:
        multiple_memories_page()
    elif page == MANUAL_PAGE:
        manual_page()
    elif page == DEBUG_PAGE:
        debug_page()


if __name__ == "__main__":
    main()
