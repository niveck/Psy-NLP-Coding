import streamlit as st
from streamlit_gsheets import GSheetsConnection

# page names
WELCOME_PAGE = "welcome"
HOME_PAGE = "home"
CHAT_PAGE = "chat"
SINGLE_MEMORY_PAGE = "single"
MULTIPLE_MEMORIES_PAGE = "multiple"
MANUAL_PAGE = "manual"
DEBUG_PAGE = "debug"
HIGHLIGHT_PAGE = "highlight"

# visuals
# emojis shortcuts link: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
HOME_EMOJI = "🏠"  # ":house:"
HOME_BUTTON_TEXT = f"{HOME_EMOJI} Back Home"
LLM_EMOJI = "🤖"  # ":robot_face:"
LLM_BACKUP_EMOJI = "🤖︎"  # because of a bug with the streamlit display
ENTER_KEYBOARD_EMOJI = "↩️"  # ":leftwards_arrow_with_hook:"  # :keyboard:
SINGLE_MEMORY_EMOJI = "📗"  # ":green_book:"
MULTIPLE_MEMORIES_EMOJI = "📚"  # ":books:"
MANUAL_EMOJI = "🦾"  # ":mechanical_arm:"
CLEAR_HISTORY_EMOJI = "🚮"  # ":put_litter_in_its_place:"  # ":recycle:", ":wastebasket:", ":broom:", ":x:"
DEBUG_EMOJI = "🛠️"  # ":hammer_and_wrench:"
SAVE_EMOJI = "💾"  # ":floppy_disk:"
SAVE_CHANGES_BUTTON_TEXT = f"{SAVE_EMOJI} Save Changes"
PALETTE_EMOJI = "🎨"  # ":art:"

GENERAL_COLOR_CODING_LEGEND_TITLE = "**Color coding legend:**"
CONTACT_SUPPORT_MESSAGE = "For additional support you can email: niv.eckhaus@mail.huji.ac.il"
MODIFY_CONFIG_INSTRUCTION = f"***You can modify this configuration at the manual control page*** {MANUAL_EMOJI}"

# coding tasks
SEGMENT_LOCUS_VALENCE = "Segment-Locus-Valence"
NARRATIVE_COHERENCE = "Narrative-Coherence"  # TODO: change this name to the right scheme name
ALL_CODING_TASKS = [SEGMENT_LOCUS_VALENCE, NARRATIVE_COHERENCE]
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

# Narrative-Coherence (`coh`) coding
COH_LEVELS_AND_COLORS = {"0": "red", "1": "orange", "2": "green", "3": "blue"}
COH_FORMATTED_CODES = {f": {score}\n": f": :{score_color}[**{score}**]\\\n"  # format for the 3 dims
                       for score, score_color in COH_LEVELS_AND_COLORS.items()}
COH_FORMATTED_CODES["Context"] = ":gray-background[**Context**]"
COH_FORMATTED_CODES["Chronology"] = ":gray-background[**Chronology**]"
COH_FORMATTED_CODES["Theme"] = ":gray-background[**Theme**]"
COH_FORMATTED_CODES["Total"] = ":violet-background[**Total**]"
COH_COLOR_CODING_LEGEND = ", ".join([f":{lvl_color}[{lvl}]"
                                     for lvl, lvl_color in COH_LEVELS_AND_COLORS.items()])
COH_TASK_DEFINITION = """Each memory should be coded by Narrative Coherence Coding Scheme (NaCCS), which includes scoring 3 coherence-dimensions from 0 to 3, and sum them together for a final score (in the range of 0 to 9).
The 3 dimensions are: Context, Chronology, Theme. Here is a descriptive guide for scoring each one:
Dimension #1 - Context: Orienting the narrative in time and space;
Score 0 - No information about time or location is provided. Example: "I got cavities." - explanation for this example's score: No mention of time or location is provided. 
Score 1 - Partial information is provided; there is mention of time or location at any level of specificity. Example: "When I first found out that I had more serious asthma...." - explanation for this example's score: Mention of time or place at any level of specificity, in this case it is general time.
Score 2 - Both time and place are mentioned but no more than one dimension is specific. Example: "I was a small child about age 5. I was held by my parents on a famous bridge." - explanation for this example's score: Both time and place are mentioned but no more than one dimension is specific, age 5 is a specific time and a famous bridge is a general bridge.
Score 3 - Both time and place are mentioned and both are specific. Example: "I remember when my mom had my brother. I was 2 years and 8 months when she brought him home." - explanation for this example's score: Both time and place are mentioned and both are specific (home is the specific place).
Dimension #2 - Chronology: Relating components along timeline;
Score 0 - Narrative consists of a list of actions with minimal or no information about temporal order. Example: "A gorilla. A tiger. An elephant. A giraffe. Balloon." - explanation for this example's score: List of actions with minimal or no information about temporal order.
Score 1 - Naive listener can place some but not most of the events on a timeline. Fewer than half of the temporally relevant actions can be ordered on a timeline with confidence. Example: "I ate all my frosting out of my bowl. We went to the grocery store and got 'em. And we had to wait until the gingerbread houses were ready." - explanation for this example's score: Fewer than half of the temporally relevant actions can be ordered on a timeline.
Score 2 - Naive listener can place between 50-75% of the relevant actions on a timeline but cannot reliably order the entire story from start to finish with confidence. Example: "I found a giraffe but the giraffe was sick. And then we looked under a blanket, you know what we found? The baby elephant. I saw fishes. Goldfish. A zebra eating. And then I saw a tiger when doing his (unintelligible) dance. And then I saw the koala jumping around the tree. After the banana he burps." - explanation for this example's score: Can place between 50-75% of the relevant actions on a timeline.
Score 3 - Naive listener can order almost all (> 75%) of the temporally relevant actions. This includes cases in which the speaker marks deviations from temporal order or repairs a violated timeline. Example: "We won 2-1 and it wasn't - it was sort of our best game, because usually all through the main season we didn't do very well in the games, and then when we went in the tournament we did pretty well. And our team, well on our team, no one really got hurt at the game, so we and the other team didn't get hurt. And lots of times - the one time that the ball went in, the player just went right past the defense and got it in, just like right into the corner. And one of ours was like that, and the other - I can't remember what the other one was like." - explanation for this example's score: Can place more than 75% of the relevant actions on a timeline.
Dimension #3 - Theme: Maintaining and elaborating on topic;
Score 0 - The narrative is substantially off topic and/or characterized by multiple digressions that make the topic difficult to identify. No attempt to repair digressions. Example: "I got a dress. Me and Shelley got a dress. And Jessie's gonna get on her computer and send it to us. We're gonna buy it. And buy the shoes with flowers on the side. I got the shoes with the flowers on the side." - explanation for this example's score: The narrative is substantially off topic and/or characterized by multiple digressions that make the topic difficult to identify.
Score 1 - A topic is identifiable and most of the statements relate to it. The narrative may include minimal development of the topic through causal linkages, or personal evaluations and reactions, or elaborations of actions. Example: "I was a small child about age 5. I was held by my parents on a famous bridge. It was in winter and I was wearing a hat. Then I took off my hat, and threw it outside the bridge, mimicking some sound of the plane." - explanation for this example's score: A topic is identifiable and most of the statements relate to the topic in a consistent manner. However, there is no substantial development.
Score 2 - The narrative substantially develops the topic. Several instances of causal linkages, and/or interpretations, and/or elaborations of previously reported actions are included. Example: "I was kind of scared because they might have to put that trache in, and I didn't know what it would affect to my asthma, on my lungs. I just didn't know because I was kind of crying and I was kind of scared. And I just didn't like the sound of it. I thought it was going to do something to me like not let me breathe anymore or something. And I just didn't really like it and it just hurt me really bad." - explanation for this example's score: The narrative substantially develops the topic. However, there is no resolution, links to other autobiographical experiences, or self-concept; only a wrap-up statement.
Score 3 - Narrative includes all the above and a resolution to the story, or links to other autobiographical experiences including future occurrences, or self-concept or identity. Resolution brings closure and provides new information. Example: "It wasn't really the fact of getting into medical school that was thrilling even though it was a good thing but just what I had gone through to get there and all the hard work and the struggle had paid off. And that's because I basically had, for the last four years, I saw myself through school. I've had to like work between two to four jobs and at the same time I'm getting four degrees and two minors and I remember times I'd work like third shift from 11 pm to 7 am and then have to go to chemistry class at 8 am and go through rush hour traffic in the morning and all that, so it just made it all worth it like, when I saw the first letter I just felt good that all the hard work was not in vain. It paid off and it just shows that if you are willing to work hard you can succeed." - explanation for this example's score: The narrative substantially develops the topic. In addition, there is a link to other autobiographical experiences ("because ... I saw myself through school") and self-concept ("when I saw the first letter I just felt good that all the hard work was not in vain")."""

# examples keywords (for few-shots)
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
    NARRATIVE_COHERENCE: {
        TASK_DEFINITION: COH_TASK_DEFINITION,
        INPUT_FORMAT_INSTRUCTION: "You will be given as input text written by a patient, describing a memory.",
        OUTPUT_FORMAT_INSTRUCTION: "For each input you get, you will only output a score for each dimension and their sum in the following format:\n"
                                   "Context: X\nChronology: Y\nTheme: Z\nTotal: SUM\n"
                                   "Where X, Y and Z are a score between 0 and 3, and SUM is their total sum. DON'T OUTPUT ANYTHING ELSE! An example for such output can be:\n"
                                   "Context: 2\nChronology: 0\nTheme: 3\nTotal: 5",
        # TODO: PUBLIC_CORRECT_EXAMPLES - needed from Bat Sheva
        PUBLIC_CORRECT_EXAMPLES: [],
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
                                 PRIVATE_SERVICE: [
                                     "meta-llama/Llama-3.3-70B-Instruct",
                                     # "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",  # uses </think>
                                     "microsoft/phi-4"
                                 ]}
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


def get_gsheets_connection():
    if "gsheets_connection" not in st.session_state:
        st.session_state.gsheets_connection = st.connection("gsheets", type=GSheetsConnection)
    return st.session_state.gsheets_connection
