import os
import time

import streamlit as st
import pandas as pd
from pathlib import Path
from io import BytesIO
from streamlit_gsheets import GSheetsConnection

from generating_with_together import code_text, generate_for_chat, save_generation_log
from prompts import get_system_prompt
from constants import *


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


def home_page():
    st.title(f"{HOME_EMOJI} LLM-Assisted Coding &mdash; Home Page &mdash; BETA")
    columns = st.columns(4)  # TODO: maybe add a button for visual presentation of coded text!
    if columns[0].button(f"Code a single memory {SINGLE_MEMORY_EMOJI}"):
        st.session_state.page = SINGLE_MEMORY_PAGE
        st.rerun()
    if columns[1].button(f"Code multiple memories {MULTIPLE_MEMORIES_EMOJI}"):
        st.session_state.page = MULTIPLE_MEMORIES_PAGE
        st.rerun()
    if columns[2].button(f"Chat with our LLM directly {LLM_EMOJI}"):
        st.session_state.page = CHAT_PAGE
        st.rerun()
    if columns[3].button(f"Manually control configuration {MANUAL_EMOJI}"):
        st.session_state.page = MANUAL_PAGE
        st.rerun()
    if "user" in st.session_state and st.session_state.user in get_developer_users():
        if st.button(f"Debug page {DEBUG_EMOJI}"):
            st.session_state.page = DEBUG_PAGE
            st.rerun()
    st.caption(CONTACT_SUPPORT_MESSAGE)


def format_coded_result(result, formatted_codes):
    for code, formatted_code in formatted_codes.items():
        result = result.replace(code, formatted_code)
    return result


def get_coding_task_formatted_codes():
    coding_task = validate_model_config()[CODING_TASK]
    task_parameters = PARAMETERS_BY_CODING_TASK[coding_task]
    return task_parameters[FORMATTED_CODES_DICT], task_parameters[COLOR_CODING_LEGEND]


def single_memory_page():
    st.title(f"{SINGLE_MEMORY_EMOJI} Code a Single Memory")
    show_current_config_info()
    memory_text = st.text_area("Paste the memory you want to code")
    if st.button("Code") and memory_text:
        try:
            with st.spinner("Model generating your coded result..."):
                result, message_history, generation_log = code_text(memory_text)
                save_generation_log(single_generation_log=generation_log)
        except Exception as e:
            handle_generation_error(e)
        else:
            st.subheader("Coded result &mdash; color coded and highlighted")
            formatted_codes, color_coding_legend = get_coding_task_formatted_codes()
            st.caption(f"{GENERAL_COLOR_CODING_LEGEND_TITLE} {color_coding_legend}")
            st.markdown(format_coded_result(result, formatted_codes))
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
    show_current_config_info()

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
                messages = [{"role": "system", "content": get_system_prompt()}]  # save process time
                results, logs = [], []
                for memory in memories:
                    result, message_history, generation_log = code_text(memory, messages)
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
    st.title(f"{MANUAL_EMOJI} Manually Control the Coding Model's Configuration")
    st.info(get_current_model_config_message())
    model_service, base_llm, coding_task = None, None, None
    explainable_model_types = {f"{desc.capitalize()}": service
                               for service, desc in MODEL_SERVICES_DESCRIPTION.items()}
    model_service_desc = st.selectbox("Choose kind of model", list(explainable_model_types.keys()))
    if model_service_desc:
        model_service = explainable_model_types[model_service_desc]
    base_llm_option_key = model_service if model_service is not None else st.session_state.model_config[MODEL_SERVICE]
    base_llm = st.selectbox("Choose base-LLM", MODEL_SERVICES_AVAILABLE_LLMS[base_llm_option_key])
    coding_task = st.selectbox("Choose coding task", ALL_CODING_TASKS)

    if st.button(SAVE_CHANGES_BUTTON_TEXT):
        for key, new_value in [(MODEL_SERVICE, model_service), (BASE_LLM, base_llm),
                               (CODING_TASK, coding_task)]:
            if new_value is not None:
                st.session_state.model_config[key] = new_value
        st.rerun()

    # st.info(":construction_worker: This page is still under construction...")

    page_bottom()


def get_current_model_config_message():
    model_config = validate_model_config()
    model_service_description = MODEL_SERVICES_DESCRIPTION[model_config[MODEL_SERVICE]]
    return (f"You are currently working with the following **model configuration**:\n"
            f"- The **{model_service_description.upper()}** model\n"
            f"- Based on the LLM: **{model_config[BASE_LLM]}**\n"
            f"- Trained for the coding task: **{model_config[CODING_TASK]}**\n")

def show_current_config_info():
    config_ifo_message = get_current_model_config_message()
    st.info(f"{config_ifo_message}\n"
            f"***You can modify this configuration at the manual control page*** {MANUAL_EMOJI}")


def chat_page():
    st.title(f"{LLM_EMOJI} Chat with the Lab's LLM")
    st.markdown("Welcome to the chat interface!  \n"
                "Use this page to interact with our proprietary LLM.")
    show_current_config_info()
    st.caption(f"Use the ***Enter*** {ENTER_KEYBOARD_EMOJI} key to send your message and get an answer.")

    # Initialize chat history if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "system", "content": get_system_prompt(CHAT_TASK)}]

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

            # # Rerun to show updated messages  # TODO trying with no rerun
            # st.rerun()

    st.text_input("Your message:", key="chat_input", on_change=submit)

    page_bottom()


# Entry point
def debug_page():
    """
    check: st.dialog, st.help, st.feedback, st.chat_message, st.chat_input, st.warning vs st.error
    """
    st.title(f"{DEBUG_EMOJI} This page is for debugging purposes, as a user you can ignore it")
    show_current_config_info()
    st.info("Trying the color coding with the example output...")
    formatted_codes, color_coding_legend = get_coding_task_formatted_codes()
    st.caption(f"{GENERAL_COLOR_CODING_LEGEND_TITLE} {color_coding_legend}")
    # EXAMPLE_OUTPUT_BY_FREE_MODEL = """I had an essay due the same day as my presentation _ext_neu_ so I thought I could do the presentation without preparing _int_neg_ so I just did all my slides _int_neu_ and for some reason I didn't save it that night _ext_neu_ so I had to do it _int_neu_ and the class was in the afternoon _ext_neu_ so I did it in the morning _int_neu_ and then cause I had class in the morning _ext_neu_ so I did it in a real rush kind of way _int_neg_ so it was pretty screwed up _int_neg_. By the time I got to the class for some reason I was the first one up _int_neu_. I couldn't have any time to prepare for it _int_neg_ so I just went up and talked about my presentation _int_neu_. It was about some Catholic like thing _int_neu_. That's all I remember _ext_neu_. Cause they were in Catholic - I'm not really religious or anything like that _ext_neu_ so I don't know some of the terms or some of the stuff _int_neg_ so by the time I finished my presentation I was like, everything was kind of screwed up _int_neg_ cause I knew I didn't get the terms right _int_neg_. There were some religious stuff that I messed up _int_neg_ and then it was like a final presentation _ext_neu_ so I knew it would cost a lot of marks in my final grade _int_neg_. By the time I finished it the teacher was shaking his head a bit like that _int_neg_ and then ya so I sat down and ya I was pretty angry at myself _int_neg_. That was about it _ext_neu_."""
    EXAMPLE_OUTPUT_BY_FREE_MODEL = """Last summer, Mommy and Daddy took me and my little brother to the zoo. _high_ It was super hot, and I got sticky from my ice cream, but I didn’t care. _high_ We saw a giraffe eat leaves from a tall tree—its tongue was purple! _high_ I laughed so hard when the monkey made faces at us. _high_ Then we rode the zoo train. _high_ It went choo-choo and I waved at the people like I was the driver. _high_ Before we left, Daddy let me pick a toy from the gift shop, and I got a tiny lion with fluffy fur. _high_ I named him Roary and he sleeps in my bed every night now. _high_"""
    st.markdown(format_coded_result(EXAMPLE_OUTPUT_BY_FREE_MODEL, formatted_codes))

    conn = st.connection("gsheets", type=GSheetsConnection)
    st.code(dir(conn))
    old_df = conn.read(ttl=0)
    st.caption("This is the old DF before adding a row: (after third)")
    # print("This is the old DF before adding a row: (after third)")
    st.write(old_df)
    # # print(old_df)
    # update_df = False
    # if update_df:
    #     new_row = [1, "n", FREE_SERVICE, "free", SEGMENT_LOCUS_VALENCE, "input", "{}", "output", "coding"]
    #     # new_df = pd.DataFrame([new_row], columns=["timestamp", "user", "model", "input", "output"])
    #     # conn.update(data=new_df)
    #     old_df.loc[len(old_df)] = new_row
    # conn.update(data=old_df)
    # conn.reset()
    # # st.code(help(conn.update))
    # # st.code(help(conn.read))
    # # help(conn.reset)


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

    validate_model_config()

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
