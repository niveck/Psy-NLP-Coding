# TODO: after commit, move all of this code to prompts.py and rename to prompting.py

import time
import pandas as pd
from together import Together
from huggingface_hub import InferenceClient
from streamlit_gsheets import GSheetsConnection

from constants import *
from prompts import get_system_prompt

together_client = Together(api_key=st.secrets["TOGETHER_API_KEY"])
hf_client = InferenceClient(provider="hf-inference", api_key=st.secrets["HF_API_KEY"])


def get_model_config_parameters():
    model_config = validate_model_config()
    service = model_config[MODEL_SERVICE]
    client = hf_client if service == PRIVATE_SERVICE else together_client
    base_llm = model_config[BASE_LLM]
    coding_task = model_config[CODING_TASK]
    return client, service, base_llm, coding_task


def get_generation_log(service, base_llm, coding_task, messages,
                       generation_kwargs, output, task=DIRECT_CODING_TASK):
    return {
        TIMESTAMP_COLUMN: time.strftime("%x %X"),
        USERNAME_COLUMN: st.session_state.get("user", "error"),
        SERVICE_COLUMN: service,
        BASE_LLM_COLUMN: base_llm,
        CODING_TASK_COLUMN: coding_task,
        INPUT_COLUMN: str(messages),
        GEN_KWARGS_COLUMN: str(generation_kwargs),
        OUTPUT_COLUMN: output,
        TASK_COLUMN: task
    }


def save_generation_log(single_generation_log: dict[str, str] = None,
                        multiple_generation_logs: list[dict[str]] = None):
    conn = st.connection("gsheets", type=GSheetsConnection)  # TODO: check if conn already exists
    df = conn.read(ttl=0)
    if single_generation_log:
        df.loc[len(df)] = single_generation_log
    if multiple_generation_logs:
        df = pd.concat([df, pd.DataFrame(multiple_generation_logs)], ignore_index=True)
    conn.update(data=df)


def code_text(new_message: str, message_history: list[dict[str, str]] = None,
              temperature: float = 0):
    if message_history is None:
        messages = [{"role": "system", "content": get_system_prompt()}]
    else:
        messages = message_history.copy()
    messages.append({"role": "user", "content": new_message})
    client, service, base_llm, coding_task = get_model_config_parameters()
    generation_kwargs = dict(temperature=temperature)
    output = raw_generation(client, base_llm, messages, generation_kwargs)
    # messages.append({"role": "assistant", "content": output})
    return output, messages, get_generation_log(service, base_llm, coding_task, messages,
                                                generation_kwargs, output)


def raw_generation(client, base_llm, messages, generation_kwargs):
    response = client.chat.completions.create(model=base_llm, messages=messages,
                                              **generation_kwargs)
    output = response.choices[0].message.content
    return output


def generate_for_chat(messages: list[dict[str, str]], temperature: float = 0):
    client, service, base_llm, coding_task = get_model_config_parameters()
    generation_kwargs = dict(temperature=temperature)
    output = raw_generation(client, base_llm, messages, generation_kwargs)
    log = get_generation_log(service, base_llm, coding_task, messages, generation_kwargs, output, CHAT_TASK)
    messages.append({"role": "assistant", "content": output})  # first add to show user  # TODO: maybe st.rerun()?
    save_generation_log(single_generation_log=log)  # then save log


def debug_main():
    EXAMPLE_INPUT = """I had an essay due the same day as my presentation so I thought I could do the presentation without preparing so I just did all my slides and for some reason I didn't save it that night so I had to do it and the class was in the afternoon so I did it in the morning and then cause I had class in the morning so I did it in a real rush kind of way so it was pretty screwed up. By the time I got to the class for some reason I was the first one up. I couldn't have any time to prepare for it so I just went up and talked about my presentation. It was about some Catholic like thing. That's all I remember. Cause they were in Catholic - I'm not really religious or anything like that so I don't know some of the terms or some of the stuff so by the time I finished my presentation I was like, everything was kind of screwed up cause I knew I didn't get the terms right. There were some religious stuff that I messed up and then it was like a final presentation so I knew it would cost a lot of marks in my final grade. By the time I finished it the teacher was shaking his head a bit like that and then ya so I sat down and ya I was pretty angry at myself. That was about it."""
    answer, message_history, log = code_text(EXAMPLE_INPUT)
    print("Answer:")
    print(answer)
    print("Message history:")
    print(message_history)


if __name__ == "__main__":
    print("stop")
    debug_main()
