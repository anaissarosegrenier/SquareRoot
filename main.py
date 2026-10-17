## Imports
import json
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageOps

from pyvis.network import Network
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Square Root",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

## Gemini client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

## Initialize skills with streamlit
if "skills" not in st.session_state:
    st.session_state.skills = {
    "Algebra" : {},
    "Trigonometry" : {},
    "Calculus" : {}
}
skills = st.session_state.skills

## Update Skills
def update_skill(subject, concept, correct):
    if concept not in skills[subject]:
        skills[subject][concept] = {
            "correct": 0,
            "incorrect": 0,}
    if correct:
        skills[subject][concept]["correct"] += 1
    else:
        skills[subject][concept]["incorrect"] += 1

## Set colors, get color function
def get_colors(skills, subject, concept):

    ## check if the concept exists in skills, if not return a gray color
    if concept not in skills[subject]:
        color = "#B8A9CA"
        return color

    ## Calculate the total number of correct and incorrect attempts
    correct = skills[subject][concept]["correct"]
    incorrect = skills[subject][concept]["incorrect"]
    total = correct + incorrect

    ## If the total number of correct/incorrect attemptss is less than 3, return yellow color
    if total < 3:
        color = "#E6BC68"
        return color

    ## Calculate score when there are enough attempts
    score = correct / total

    if score < 0.8 and score >= 0.5:
        color = "#D99563"
    elif score < 0.5:
        color = "#D46A81"
    else:
        color = "#65A994"
    return color

## Subject color method
def get_subject_color(skills, subject):
    color = ""
    correct = 0
    incorrect = 0

    for concept in skills[subject]:
        correct += skills[subject][concept]["correct"]
        incorrect += skills[subject][concept]["incorrect"]

    total = correct + incorrect


    if total == 0:
        color = "#9CA3AF"
        return color
    total_score = correct / total
    if total < 3:
        color = "#FACC15"
        return color
    if total_score >= 0.5 and total_score < 0.8:
        color = "#FB923C"
    elif total_score <= 0.5:
        color = "#EF4444"
    else:
        color = "#22C55E"

    return color

## Analyze image and prompt gemma
## Return gemma response
def analyze_image(image):

    ## Prompt sent to gemma to analyze the image
    prompt = ("""You are a math analyzer. Rather than simply giving the correct answer,"
              you are going to diagnose the user's problem area.
              You will receive an image containing a handwritten mathematics problem
              and the student's attempted solution.

              Your task is to analyze the student's mathematical reasoning, identify
              the concepts they demonstrate correctly or incorrectly, and locate
              the underlying cause of any mistakes.

              INSTRUCTIONS:

              1. Read the mathematical problem and the student's handwritten solution.
              Examine each visible step in order.

              2. Determine which mathematical concepts the student actually demonstrates.
              Focus on Algebra, Trigonometry, and Calculus.

              3. Identify which concepts were applied correctly and which were applied
              incorrectly.Do not assume the student understands a concept simply
              because the final answer is correct.

              4. Identify the FIRST mathematical error, if one exists.
              Distinguish between the underlying mistake and subsequent errors
              that result from it.

              5. Do not penalize a student repeatedly for errors that are simply
              consequences of an earlier mistake.

              6. Identify prerequisite knowledge gaps.
              For example, if a student correctly differentiates a trigonometric
              expression but incorrectly evaluates a trigonometric value, identify
              the issue as a trigonometry or unit-circle weakness rather than
              incorrectly marking differentiation as a weakness.

              7. Only evaluate concepts for which the student's work provides
              observable evidence.Do not invent steps, errors, or demonstrated skills.

              8. If a step is ambiguous or handwriting is unclear, mark the relevant
              assessment as "uncertain" rather than guessing.

              9. Use short, consistent names for mathematical concepts so the same
              concept can be tracked across multiple uploaded solutions.

              10. Assign each concept to one of these subjects:
              - Algebra
              - Trigonometry
              - Calculus

              11. For each observed concept, assign exactly one result:
              - "correct"
              - "incorrect"
              - "uncertain"

              12. If the image is unreadable or does not contain enough mathematical
              work to assess, return an empty skills list and explain why.
              13. Do not use LaTeX notation or backslashes anywhere in your JSON response.
              Write all mathematical expressions in plain text.
              For example, write "sin(x)", "pi/3", and "1/2".

                OUTPUT FORMAT:
                     Return ONLY valid JSON. Do not include Markdown formatting, code fences, or any text outside the JSON.

            Use this structure:
        
            {
                "summary": "Brief explanation of the student's overall work.",
                "first_error": "Description of the first mathematical error, or null.",
                "skills": [
                    {
                        "subject": "Calculus",
                        "concept": "Product Rule",
                        "result": "correct",
                        "evidence": "The student correctly differentiated the product."
                    },
                    {
                        "subject": "Algebra",
                        "concept": "Simplifying Expressions",
                        "result": "incorrect",
                        "evidence": "The student incorrectly combined two terms."
                    }
                ]
            }
        
            Be accurate, conservative, and specific. Your goal is to diagnose
            mathematical understanding, not merely determine whether the final
            answer is correct.
            """)

    ## response sent from gemma
    response = client.models.generate_content(
        model = "gemma-4-26b-a4b-it",
        contents = [prompt, image]
        )

    return response.text


## Generate practice problem
def generate_problem(concept):
    pass


## Node tree
def display_tree(skills):
    net = Network(
        height="600px",
        width="100%",
        bgcolor="rgba(0,0,0,0)",
        font_color="#30263D",
        directed=False
    )

    ## Styling
    net.set_options("""
    {
      "nodes": {
        "font": {
          "size": 18,
          "face": "Arial",
          "color": "#30263S"
        },
        "borderWidth": 2
      },
      "edges": {
        "color": "#C9BDD8",
        "width": 2,
        "smooth": {
          "enabled": true,
          "type": "continuous"
        }
      },
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -8000,
          "centralGravity": 0.15,
          "springLength": 180,
          "springConstant": 0.04,
          "damping": 0.2
        },
        "stabilization": {
          "enabled": true,
          "iterations": 200
        }
      },
      "interaction": {
        "hover": true,
        "dragNodes": true,
        "zoomView": true,
        "dragView": true
      }
    }
    """)

    ## Loop over subject and concepts to display on graph
    for subject, concepts in skills.items():
        subject_color = get_subject_color(skills, subject)

        net.add_node(
            subject,
            label=subject,
            color={
                "background": subject_color if skills[subject] else "rgba(0,0,0,0)",
                "border": subject_color if skills[subject] else "#7353AC"
            },
            borderWidth=3,
            size=35,
            shape="dot"
        )

        for concept in concepts:
            color = get_colors(skills, subject, concept)
            node_id = f"{subject}:{concept}"

            net.add_node(
                node_id,
                label=concept,
                color=color,
                size=20,
                shape="dot"
            )

            net.add_edge(subject, node_id)

    html = net.generate_html()

    # Make graph bg transparent
    html = html.replace(
        "</head>",
        """
        <style>
            html, body {
                background: transparent !important;
                margin: 0;
                padding: 0;
            }

            #mynetwork {
                background: transparent !important;
                border: none !important;
            }

            .card {
                background: transparent !important;
                border: none !important;
            }
        </style>
        </head>
        """
    )

    components.html(html, height=620, scrolling=False)


# Streamlit Interface

## Styling components (a little messy)
st.markdown("""
<style>
    /* Center the title */
    div[data-testid="stHeadingWithActionElements"] {
        justify-content: center;
    }

    h1 {
        text-align: center;
        color: #7353AC
        font-size: 3.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title(r"$\sqrt{\text{Square Root}}$")
st.markdown(
    """
    <p style="
        text-align: center;
        color: #776B88;
        font-size: 20px;
        margin-top: -10px;
        margin-bottom: 35px;
    ">
        Find the root of your math problems
    </p>
    """,
    unsafe_allow_html=True
)


st.markdown("""
<style>
    h1, h2, h3 {
        color: #7353AC !important;
    }

    p {
        color: #30263D;
    }
</style>
""", unsafe_allow_html=True)

# Upload file button

uploaded_file = st.file_uploader(
    "",
    type = ["png", "jpg", "jpeg"]
)

st.markdown("""
<style>
[data-testid="stFileUploaderDropzone"] {
    background: transparent 
    border: none 
    padding: 0 
    display: flex 
    justify-content: center 
}

[data-testid="stFileUploaderDropzone"] button {
    background: #7343AC;
    color: white;
    border: none ;
    border-radius: 12px ;
    padding: 0.65rem 1.5rem ;
    font-weight: 600;
    transition: background-color 0.2s ease;
}

[data-testid="stFileUploaderDropzone"] button:hover {
    background: #B9A0E5;
    color: white ;
}

div.stButton {
    max-width: 250px;
    margin-left: auto;
    margin-right: auto;
}
[data-testid="stFileUploaderDropzone"] {
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}

[data-testid="stFileUploader"] {
    display: flex;
    flex-direction: column;
    align-items: center;
}

</style>
""", unsafe_allow_html=True)
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    left, center, right = st.columns([1, 3, 1])

    with center:
        st.image(uploaded_file.getvalue(), use_container_width=True)

    if st.button("Analyze", use_container_width=True):
        message = st.empty()

        message.markdown(
            "<p style='text-align:center;'>We're analyzing your math skills... Give us a second!</p>",
            unsafe_allow_html=True
        )

        with st.spinner(""):
            response = analyze_image(image)

        message.empty()
        result = json.loads(response)

        st.markdown(
            "<h3 style='text-align: center; color: #7353AC;'>Our Analysis</h3>",
            unsafe_allow_html=True
        )
        st.write(result["summary"])

        for skill in result["skills"]:
            if skill["result"] in ("correct", "incorrect"):
                update_skill(
                    skill["subject"],
                    skill["concept"],
                    skill["result"] == "correct"
                )

st.markdown(
    "<h3 style='text-align: center; color: #7353AC;'>Your Math Tree</h3>",
    unsafe_allow_html=True
)
display_tree(skills)

