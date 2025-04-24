import time
import pandas as pd
import streamlit as st
from together import Together
from streamlit_gsheets import GSheetsConnection

from prompts import SYSTEM_PROMPT, EXAMPLE_INPUT

TIMESTAMP_COLUMN = "timestamp"
USERNAME_COLUMN = "user"
MODEL_COLUMN = "model"
INPUT_COLUMN = "input"
GEN_KWARGS_COLUMN = "generation_kwargs"
OUTPUT_COLUMN = "output"
TASK_COLUMN = "task"
GENERATION_LOG_COLUMNS = [TIMESTAMP_COLUMN, USERNAME_COLUMN, MODEL_COLUMN, INPUT_COLUMN,
                          GEN_KWARGS_COLUMN, OUTPUT_COLUMN, TASK_COLUMN]
LLAMA_3_3_70B_INSTRUCT_TURBO_FREE = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
CODING_TASK = "coding"
CHAT_TASK = "chat"


client = Together(api_key=st.secrets["TOGETHER_API_KEY"])


def get_generation_log(model, messages, generation_kwargs, output, task=CODING_TASK):
    return {
        TIMESTAMP_COLUMN: time.strftime("%x %X"),
        USERNAME_COLUMN: st.session_state.get("user", "error"),
        MODEL_COLUMN: model,
        INPUT_COLUMN: str(messages),
        GEN_KWARGS_COLUMN: str(generation_kwargs),
        OUTPUT_COLUMN: output,
        TASK_COLUMN: task
    }


def save_generation_log(single_generation_log: dict[str, str] = None,
                        multiple_generation_logs: list[dict[str]] = None, ):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    if single_generation_log:
        df.loc[len(df)] = single_generation_log
    if multiple_generation_logs:
        df = pd.concat([df, pd.DataFrame(multiple_generation_logs)], ignore_index=True)
    conn.update(data=df)


def code_text(new_message: str, message_history: list[dict[str, str]] = None,
              model: str = LLAMA_3_3_70B_INSTRUCT_TURBO_FREE, temperature: float = 0):
    if message_history is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    else:
        messages = message_history.copy()
    messages.append({"role": "user", "content": new_message})
    generation_kwargs = dict(temperature=temperature)
    output = raw_generation(model, messages, generation_kwargs)
    # messages.append({"role": "assistant", "content": output})
    return output, messages, get_generation_log(model, messages, generation_kwargs, output)


def raw_generation(model, messages, generation_kwargs):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **generation_kwargs
    )
    output = response.choices[0].message.content
    return output


def generate_for_chat(messages: list[dict[str, str]],
                      model: str = LLAMA_3_3_70B_INSTRUCT_TURBO_FREE, temperature: float = 0):
    generation_kwargs = dict(temperature=temperature)
    output = raw_generation(model, messages, generation_kwargs)
    log = get_generation_log(model, messages, generation_kwargs, output, CHAT_TASK)
    messages.append({"role": "assistant", "content": output})  # first add to show user
    save_generation_log(single_generation_log=log)  # then save log


def debug_main():
    answer, message_history, log = code_text(EXAMPLE_INPUT)
    print("Answer:")
    print(answer)
    print("Message history:")
    print(message_history)


if __name__ == "__main__":
    print("stop")
    debug_main()
