import streamlit as st
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import json
import os
import time

# Initialize LangChain model with groq api
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Ensure the API key is loaded properly
if not api_key:
    st.error("GROQ API key is missing! Please check your .env file.")
    st.stop()

llm = ChatGroq(temperature=0, model_name="llama3-8b-8192", api_key=api_key)

# Function to parse JSON response from Groq API
def parse_response_to_json(response):
    try:
        output_parser = JsonOutputParser()
        return output_parser.parse(response)
    except json.JSONDecodeError:
        st.error("Failed to parse response into JSON. Please try again.")
        return []

# Define a function to generate unique MCQs
def generate_mcqs(subject, topic, difficulty):
    prompt = PromptTemplate(
        template=(
            "Generate 20 unique multiple-choice questions on the topic '{topic}' in the subject '{subject}' "
            "at a '{difficulty}' difficulty level. Ensure that each question is different from previous ones. "
            "Provide four options for each question, clearly mark the correct option, and return the output in "
            "JSON format like this:\n"
            "[{{'question': '...', 'options': ['a', 'b', 'c', 'd'], 'correct_option': '...'}}, ...]"
        ),
        input_variables=["subject", "topic", "difficulty"],
    )

    formatted_prompt = prompt.format(subject=subject, topic=topic, difficulty=difficulty)
    try:
        response = llm.invoke(input=formatted_prompt).content
        questions = parse_response_to_json(response)
        return questions
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

# Streamlit interface
st.title("QuizCraft AI ")

# Step 1: Input the subject, topic, and difficulty level
subject = st.text_input("Enter the subject for the quiz:", placeholder="e.g., Python programming")
topic = st.text_input("Enter the topic for the quiz:", placeholder="e.g., Loops")
difficulty = st.selectbox("Select difficulty level:", ["Easy", "Medium", "Hard"])

if st.button("Generate Quiz"):
    if not subject or not topic:
        st.error("Please enter both subject and topic.")
    else:
        st.info(f"Generating quiz for {subject} on {topic} at {difficulty} difficulty...")
        questions = generate_mcqs(subject, topic, difficulty)

        if questions:
            st.session_state["questions"] = questions
            st.session_state["current_question"] = 0
            st.session_state["score"] = 0

# Display questions if available
if "questions" in st.session_state:
    questions = st.session_state["questions"]
    current_question = st.session_state["current_question"]

    if current_question < len(questions):
        question = questions[current_question]

        st.subheader(f"Question {current_question + 1}:")
        st.write(question["question"])

        options = question["options"]
        user_answer = st.radio("Select your answer:", options, key=f"question_{current_question}")

        # Display response and load the next question with a delay
        if st.button("Submit"):
            if user_answer:
                # Improved comparison: Strip spaces and compare case-insensitively
                correct_option = question["correct_option"].strip().lower()
                user_answer = user_answer.strip().lower()

                if user_answer == correct_option:
                    st.success("✅ Correct!")
                    st.session_state["score"] += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer is: {question['correct_option']}")

                # Delay before moving to the next question
                time.sleep(2)

                # Move to the next question
                st.session_state["current_question"] += 1
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
            else:
                st.warning("Please select an answer before submitting.")
    else:
        st.write("Quiz finished!")
        st.write(f"Your score: {st.session_state['score']} / {len(questions)}")

        # Option to reset
        if st.button("Restart Quiz"):
            del st.session_state["questions"]
            del st.session_state["current_question"]
            del st.session_state["score"]

# Add custom CSS for better visuals
st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f9f9f9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)