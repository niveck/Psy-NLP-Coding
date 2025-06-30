# TODO: rename to prompting.py
import time
import pandas as pd
from together import Together
from huggingface_hub import InferenceClient
from streamlit_gsheets import GSheetsConnection
from constants import *


def parse_example_for_system_prompt(example):
    if type(example) is str:
        return "\n" + example
    parsed = ""
    if INPUT in example:
        parsed += f"\n{INPUT}: {example[INPUT]}"
    if OUTPUT in example:
        parsed += f"\n{OUTPUT}: {example[OUTPUT]}"
    if EXPLANATION in example:
        parsed += f"\n{EXPLANATION}: {example[EXPLANATION]}"
    return parsed


def get_private_examples(sheet):
    if not sheet:
        return []
    return []  # TODO: needs implementation!


def get_system_prompt(prompt_type_task=DIRECT_CODING_TASK):
    coding_task = validate_model_config()[CODING_TASK]
    parameters = PARAMETERS_BY_CODING_TASK[coding_task]
    task_instruction = parameters[TASK_DEFINITION]
    input_format, output_format = parameters[INPUT_FORMAT_INSTRUCTION], parameters[OUTPUT_FORMAT_INSTRUCTION]
    system_prompt = f"{SYSTEM_INTRO}\n\nCODING SCHEME:\n{task_instruction}"
    if prompt_type_task == CHAT_TASK:
        system_prompt += f"\n\n{CHAT_INSTRUCTION_FORMAT.format(input_format, output_format)}"
    else:  # prompt_type_task == DIRECT_CODING_TASK
        system_prompt += f"\n\nINPUT FORMAT:\n{input_format}\n\nOUTPUT FORMAT:\n{output_format}"
    public_correct_examples, public_incorrect_examples = parameters[PUBLIC_CORRECT_EXAMPLES], parameters[PUBLIC_INCORRECT_EXAMPLES]
    private_correct_examples = get_private_examples(parameters[PRIVATE_CORRECT_EXAMPLES_SHEET])
    private_incorrect_examples = get_private_examples(parameters[PRIVATE_INCORRECT_EXAMPLES_SHEET])
    for examples, title in [(public_correct_examples + private_correct_examples, "EXAMPLES FOR CORRECT CODINGS"),
                            (public_incorrect_examples + private_incorrect_examples, "EXAMPLES FOR INCORRECT CODINGS")]:
        if examples:
            system_prompt += f"\n\n{title}:"
            for example in public_correct_examples:
                system_prompt += parse_example_for_system_prompt(example)
    return system_prompt


# TODO: add a check in st.state so they can be defined only once!
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
