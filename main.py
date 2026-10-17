## Imports
import json
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageOps

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
        color = "#9CA3AF"
        return color

    ## Calculate the total number of correct and incorrect attempts
    correct = skills[subject][concept]["correct"]
    incorrect = skills[subject][concept]["incorrect"]
    total = correct + incorrect

    ## If the total number of correct/incorrect attemptss is less than 3, return yellow color
    if total < 3:
        color = "#FACC15"
        return color

    ## Calculate score when there are enough attempts
    score = correct / total

    if score < 0.8 and score >= 0.5:
        color = "#FB923C"
    elif score < 0.5:
        color = "#EF4444"
    else:
        color = "#22C55E"
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
        color = ""
        return color
    total_score = correct / total
    if total < 3:
        color = ""
        return color
    if total_score > 0.5 and total_score < 0.8:
        color = ""
    elif total_score <= 0.5:
        color = ""
    else:
        color = ""

    return color

## Analyze image and prompt gemma
## Return gemma response
def analyze_image(image):

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

    graph = "digraph { \n"
    for subject, concepts in skills.items():
        subject_color = get_subject_color(skills, subject)
        graph += f'"{subject}"\n'
        graph += f'"{subject}" [style=filled, fillcolor = "{subject_color}"]\n'
        for concept in concepts:
            color = get_colors(skills, subject, concept)
            graph += f'"{subject}" -> "{concept}"\n'
            graph += f'"{concept}" [style=filled, fillcolor="{color}"]\n'
    graph += "}"
    st.graphviz_chart(graph)

# Streamlit GUI Interface

st.title(r"$\sqrt{\text{Square Root}}$")
st.subheader("Find the root of your math problems")

# Upload file button

uploaded_file = st.file_uploader(
    "Upload your handwritten math work",
    type = ["png", "jpg", "jpeg"]
)


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(uploaded_file.getvalue(), width=400)

    if st.button(label="Analyze"):
        with st.spinner("We're analyzing your math skills... Give us a second!"):
            response = analyze_image(image)
        result = json.loads(response)

        st.subheader("Our Analysis")
        st.write(result["summary"])

    st.subheader("Your Math Tree")
    display_tree(result["skills"])

