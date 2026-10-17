## Imports
import json
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageOps

## Gemini client

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
def get_colors(subject, concept):

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

## Analyze image
def analyze_image(image):
    pass

## Generate practice problem
def generate_problem(concept):
    pass


## Node tree
def display_tree():
    pass

## Streamlit GUI

