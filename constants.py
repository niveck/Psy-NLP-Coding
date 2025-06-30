import streamlit as st

# page names
WELCOME_PAGE = "welcome"
HOME_PAGE = "home"
CHAT_PAGE = "chat"
SINGLE_MEMORY_PAGE = "single"
MULTIPLE_MEMORIES_PAGE = "multiple"
MANUAL_PAGE = "manual"
DEBUG_PAGE = "debug"

CONTACT_SUPPORT_MESSAGE = f"For additional support you can email: niv.eckhaus@mail.huji.ac.il"

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
SAVE_EMOJI = ":floppy_disk:"
SAVE_CHANGES_BUTTON_TEXT = f"{SAVE_EMOJI} Save Changes"

GENERAL_COLOR_CODING_LEGEND_TITLE = "**Color coding legend:**"

# coding tasks
SEGMENT_LOCUS_VALENCE = "Segment-Locus-Valence"
SENTENCE_COHERENCE = "Sentence-Coherence"
ALL_CODING_TASKS = [SEGMENT_LOCUS_VALENCE, SENTENCE_COHERENCE]
DEFAULT_CODING_TASK = ALL_CODING_TASKS[0]
# parameters defining each task (their values should be defined for each task)
TASK_DEFINITION = "task_definition"
INPUT_FORMAT_INSTRUCTION = "input_format_instruction"
OUTPUT_FORMAT_INSTRUCTION = "output_format_instruction"
PUBLIC_CORRECT_EXAMPLES = "public_correct_examples"
PUBLIC_INCORRECT_EXAMPLES = "public_incorrect_examples"
PRIVATE_CORRECT_EXAMPLES_SHEET = "private_correct_examples_sheet"  # inside the shared G-Sheet
PRIVATE_INCORRECT_EXAMPLES_SHEET = "private_incorrect_examples_sheet"  # inside the shared G-Sheet
FORMATTED_CODES_DICT = "formatted_codes_dict"
COLOR_CODING_LEGEND = "color_coding_legend"
ALL_CODING_TASK_PARAMETERS = [TASK_DEFINITION, INPUT_FORMAT_INSTRUCTION, OUTPUT_FORMAT_INSTRUCTION,
                              PUBLIC_CORRECT_EXAMPLES, PUBLIC_INCORRECT_EXAMPLES,
                              PRIVATE_CORRECT_EXAMPLES_SHEET, PRIVATE_INCORRECT_EXAMPLES_SHEET,
                              FORMATTED_CODES_DICT, COLOR_CODING_LEGEND]

# Segment-Locus-Valence (`slv`) coding
SLV_CLASS_COLORS = {"int": "blue", "ext": "gray"}
SLV_VALENCE_COLORS = {"neg": "red", "neu": "orange", "posit": "green"}
SLV_FORMATTED_CODES = {f"_{cls}_{vln}_":
                       f":{cls_color}-background[:{vln_color}[***\\_{cls}\\_{vln}\\_***]]"
                       for cls, cls_color in SLV_CLASS_COLORS.items()
                       for vln, vln_color in SLV_VALENCE_COLORS.items()}
SLV_COLOR_CODING_LEGEND = (", ".join([f":{cls_color}-background[{cls}]"
                                      for cls, cls_color in SLV_CLASS_COLORS.items()]
                                     + [f":{vln_color}[{vln}]"
                                        for vln, vln_color in SLV_VALENCE_COLORS.items()]))

# Segment-Coherence (`coh`) coding
COH_LEVELS_AND_COLORS = {"low": "red", "mid": "orange", "high": "green"}
COH_FORMATTED_CODES = {f"_{lvl}_": f":gray-background[:{lvl_color}[***\\_{lvl}\\_***]]"
                       for lvl, lvl_color in COH_LEVELS_AND_COLORS.items()}
COH_COLOR_CODING_LEGEND = ", ".join([f":{lvl_color}[{lvl}]"
                                     for lvl, lvl_color in COH_LEVELS_AND_COLORS.items()])

# examples keywords
INPUT = "INPUT"
OUTPUT = "OUTPUT"
EXPLANATION = "EXPLANATION"

# coding tasks parameters (definitions)
PARAMETERS_BY_CODING_TASK = {
    SEGMENT_LOCUS_VALENCE: {
        TASK_DEFINITION: "Each memory should be divided to segments, and each segment should be coded to its locus, which can be internal (meaning it pertains directly to the main event of the memory) or external (meaning it is not part of the main event of the memory), and to its valence, which can be positive, neutral or negative.",
        INPUT_FORMAT_INSTRUCTION: "You will be given as input text written by a patient, describing a memory.",
        OUTPUT_FORMAT_INSTRUCTION: "For each input you get, you will only output the same input, with additional coding of the locus and valence for each segment of the memory. A segment is an information bit; it is a unique occurrence, observation, fact, statement, or thought. This will usually be a grammatical clause, a part of a sentence that independently conveys information. The codings are in the pattern of _locus_valence_, coming right after the corresponding segment. The locus part can be either int (for internal) or ext (for external). The valence part can be one of the following: posit (for positive), neu (for neutral) or neg (for negative).",
        PUBLIC_CORRECT_EXAMPLES: [{INPUT: "I'm on stage and I start speaking my speech of any topic and I do start babbling and messing up on words. It was right after lunch. I even sound nervous and then people's reactions are giving off a kind of what is this guy doing he can't even give a speech right? It was similar to what happened to the principal last year. As I go on people start even leaving or just don't even enjoy it. They start yawning, etc. and I don't break down though. I just continue all the way till the end but at the same time I have that same distressed feeling the whole way.",
                                   OUTPUT: "I'm on stage _int_neu_ and I start speaking my speech of any topic _int_neu_ and I do start babbling _int_neg_ and messing up on words. _int_neg_ It was right after lunch. _ext_neu_ I even sound nervous _int_neg_ and then people's reactions are giving off a kind of what is this guy doing he can't even give a speech right? _int_neg_ It was similar to what happened to the principal last year. _ext_neu_ As I go on people start even leaving _int_neg_ or just don't even enjoy it. _int_neg_ They start yawning, etc. _int_neg_ and I don't break down though. _int_posit_ I just continue all the way till the end _int_posit_ but at the same time I have that same distressed feeling the whole way. _int_neg_",
                                   EXPLANATION: "The main event of the memory is messing up a speech on stage"}],
        PUBLIC_INCORRECT_EXAMPLES: [{INPUT: "When I was at the beach it was lovely, sunny and beautiful. But then something terrible happened, I was attacked. It was bad. I am someone who is very afraid.",
                                     OUTPUT: "When I was at the beach _ext_neu_ it was lovely, sunny and beautiful. _ext_posit_ But then something terrible happened, _int_neg_ I was attacked. _int_neg_ It was bad. _int_neg_ I am someone who is very afraid. _int_neg_",
                                     EXPLANATION: "The first two segments are coded correctly as external, since they don't discuss the main event (the attack) directly, and the next three segments are coded correctly as internal, since they do. However, the last segment, 'I am someone who is very afraid.', doesn't discuss the attack, but describes the patient in general. Therefore it should be coded as external rather than internal, so it should be: _ext_neg_ .",}],
        PRIVATE_CORRECT_EXAMPLES_SHEET: None,
        PRIVATE_INCORRECT_EXAMPLES_SHEET: None,
        FORMATTED_CODES_DICT: SLV_FORMATTED_CODES,
        COLOR_CODING_LEGEND: SLV_COLOR_CODING_LEGEND
    },
    SENTENCE_COHERENCE: {
        TASK_DEFINITION: "Each memory should be divided to sentences, and each sentence should be coded to its coherence, which can be high, low or mediocre.",
        INPUT_FORMAT_INSTRUCTION: "You will be given as input text written by a patient, describing a memory.",
        OUTPUT_FORMAT_INSTRUCTION: "For each input you get, you will only output the same input, with additional coding of the coherence for each sentence of the memory. The codings are in the pattern of _coherence_, coming right after the corresponding sentence, where the coherence part can be one of the following: high, low or mid (for mediocre).",
        PUBLIC_CORRECT_EXAMPLES: [{INPUT: "It was in the middle of the summer. I think it might have been the middle of July, but frankly I'm not quite sure... It happened really fast. Suddenly, I'm not sure how, since it happened without my awareness, but I swear to god (and you have to believe me!), he just came...",
                                   OUTPUT: "It was in the middle of the summer. _high_ I think it might have been the middle of July, but frankly I'm not quite sure... _mid_ It happened really fast. _high_ Suddenly, I'm not sure how, since it happened without my awareness, but I swear to god (and you have to believe me!), he just came... _low_"}],
        PUBLIC_INCORRECT_EXAMPLES: [],
        PRIVATE_CORRECT_EXAMPLES_SHEET: None,
        PRIVATE_INCORRECT_EXAMPLES_SHEET: None,
        FORMATTED_CODES_DICT: COH_FORMATTED_CODES,
        COLOR_CODING_LEGEND: COH_COLOR_CODING_LEGEND
    }
}

for task in ALL_CODING_TASKS:
    assert task in PARAMETERS_BY_CODING_TASK, f"{task} missing from task parameter dict"
    for param in ALL_CODING_TASK_PARAMETERS:
        assert param in PARAMETERS_BY_CODING_TASK[task], f"{param} missing from {task} parameters"


# model config
FREE_SERVICE = "TogetherAI"
PRIVATE_SERVICE = "HuggingFaceHub"
MODEL_SERVICES_DESCRIPTION = {FREE_SERVICE: "free", PRIVATE_SERVICE: "private"}
MODEL_SERVICES_AVAILABLE_LLMS = {FREE_SERVICE: ["meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"],
                                 PRIVATE_SERVICE: ["", ""]}
MODEL_SERVICE, BASE_LLM, CODING_TASK = "model_service", "base_llm", "coding_task"
MODEL_CONFIG_KEYS = [MODEL_SERVICE, BASE_LLM, CODING_TASK]
DEFAULT_MODEL_CONFIG = {MODEL_SERVICE: FREE_SERVICE,
                        BASE_LLM: MODEL_SERVICES_AVAILABLE_LLMS[FREE_SERVICE][0],
                        CODING_TASK: DEFAULT_CODING_TASK}

# generation log
TIMESTAMP_COLUMN = "timestamp"
USERNAME_COLUMN = "user"
SERVICE_COLUMN = "service"
BASE_LLM_COLUMN = "base_llm"
CODING_TASK_COLUMN = "coding_task"
INPUT_COLUMN = "input"
GEN_KWARGS_COLUMN = "generation_kwargs"
OUTPUT_COLUMN = "output"
TASK_COLUMN = "task"  # direct/chat, in contrast to the type of coding (like valence/coherence/etc.)
GENERATION_LOG_COLUMNS = [TIMESTAMP_COLUMN, USERNAME_COLUMN, SERVICE_COLUMN, BASE_LLM_COLUMN,
                          CODING_TASK_COLUMN, INPUT_COLUMN, GEN_KWARGS_COLUMN, OUTPUT_COLUMN,
                          TASK_COLUMN]

DIRECT_CODING_TASK = "direct_coding"
CHAT_TASK = "chat"

# prompts
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

STRICT_OUTPUT_FORMAT_REMINDER = "IMPORTANT! Remember to ONLY output the coded text according to this format, and to NOT add any other notes or explanations!"


def validate_model_config():
    if "model_config" not in st.session_state:
        st.session_state.model_config = {key: value for key, value in DEFAULT_MODEL_CONFIG.items()}
    return st.session_state.model_config
