import time
import streamlit as st
from together import Together

from prompts import SYSTEM_PROMPT, EXAMPLE_INPUT

LLAMA_3_3_70B_INSTRUCT_TURBO_FREE = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"


client = Together(api_key=st.secrets["TOGETHER_API_KEY"])


def generate(new_message: str, message_history: list[dict[str, str]] = None, temperature: float = 0):
    if message_history is None:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    else:
        messages = message_history.copy()
    messages.append({"role": "user", "content": new_message})
    response = client.chat.completions.create(
        model=LLAMA_3_3_70B_INSTRUCT_TURBO_FREE,
        messages=messages,
        temperature=temperature,
    )
    output = response.choices[0].message.content
    messages.append({"role": "assistant", "content": output})
    return output, messages


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
    answer, message_history = generate(EXAMPLE_INPUT)
    print("Answer:")
    print(answer)
    print("Message history:")
    print(message_history)


if __name__ == "__main__":
    print("stop")
    debug_main()
