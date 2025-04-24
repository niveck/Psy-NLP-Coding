import time
import streamlit as st
from together import Together

from prompts import SYSTEM_PROMPT, EXAMPLE_INPUT

TIMESTAMP_COLUMN = "timestamp"
USERNAME_COLUMN = "user"
MODEL_COLUMN = "model"
INPUT_COLUMN = "input"
GEN_KWARGS_COLUMN = "generation_kwargs"
OUTPUT_COLUMN = "output"
GENERATION_LOG_COLUMNS = [TIMESTAMP_COLUMN, USERNAME_COLUMN, MODEL_COLUMN,
                          INPUT_COLUMN, GEN_KWARGS_COLUMN, OUTPUT_COLUMN]
LLAMA_3_3_70B_INSTRUCT_TURBO_FREE = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"


client = Together(api_key=st.secrets["TOGETHER_API_KEY"])



def get_generation_log(model, messages, generation_kwargs, output):
    return {
        TIMESTAMP_COLUMN: time.strftime("%x %X"),
        USERNAME_COLUMN: st.session_state.get("user", "error"),
        MODEL_COLUMN: model,
        INPUT_COLUMN: str(messages),
        GEN_KWARGS_COLUMN: str(generation_kwargs),
        OUTPUT_COLUMN: output
    }


def code_text(new_message: str, message_history: list[dict[str, str]] = None,
              model: str = LLAMA_3_3_70B_INSTRUCT_TURBO_FREE, temperature: float = 0):
    if message_history is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    else:
        messages = message_history.copy()
    messages.append({"role": "user", "content": new_message})
    generation_kwargs = dict(temperature=temperature)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **generation_kwargs
    )
    output = response.choices[0].message.content
    # messages.append({"role": "assistant", "content": output})
    return output, messages, get_generation_log(model, messages, generation_kwargs, output)


def generate_for_chat(messages: list[dict[str, str]], temperature: float = 0):
    response = client.chat.completions.create(
        model=LLAMA_3_3_70B_INSTRUCT_TURBO_FREE,
        messages=messages,
        temperature=temperature,
    )
    output = response.choices[0].message.content
    messages.append({"role": "assistant", "content": output})
    # # TODO remove temporary replacement!
    # time.sleep(3)
    # messages.append({"role": "assistant", "content": "HAHAHAHA THIS IS FAKE!"})


def debug_main():
    answer, message_history = code_text(EXAMPLE_INPUT)
    print("Answer:")
    print(answer)
    print("Message history:")
    print(message_history)


if __name__ == "__main__":
    print("stop")
    debug_main()
