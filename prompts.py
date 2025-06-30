from constants import *

SYSTEM_INTRO = "You are a useful assistant for a clinical psychology research, used to code memory segments of patients by a coding scheme, so they can be used for research."

# notice it uses format-string for input_format and output_format!
CHAT_INSTRUCTION_FORMAT = """INSTRUCTION:
You are used as a chat assistant. Your role is to provide guidance, answer questions, and assist through natural dialogue in a multi-turn conversation format.
Below are the ORIGINAL task format specifications (for reference only - these describe the task the researchers are working on, NOT how you should respond):
--- REFERENCE MATERIALS (DO NOT FOLLOW THESE FORMATS IN YOUR RESPONSES) ---
ORIGINAL INPUT FORMAT:
```
{0}
```
ORIGINAL OUTPUT FORMAT:
```
{1}
```
--- END REFERENCE MATERIALS ---
YOUR ACTUAL ROLE:
- Respond as a helpful chat assistant using natural conversation
- Answer questions about the coding task described above
- Provide guidance and support for the researchers
- Use normal chat responses unless explicitly asked to demonstrate the original formats
- Do NOT automatically format your responses according to the input/output specifications above
Always maintain a helpful, conversational tone while assisting with this coding task."""


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