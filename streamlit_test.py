import streamlit as st
import requests
import json
import random
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Exam Paper Generator AI",
    page_icon="📝",
    layout="wide"
)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'generated_papers' not in st.session_state:
    st.session_state.generated_papers = []

# Mock paper generation function
def mock_generate_paper(parameters):
    """Generate demo paper without backend"""
    subject = parameters.get('subject', 'Mathematics')
    difficulty = parameters.get('difficulty', 'Medium')
    num_questions = parameters.get('num_questions', 10)
    exam_type = parameters.get('exam_type', 'Mixed')
    
    questions = []
    for i in range(num_questions):
        question_types = []
        if exam_type == "Multiple Choice" or exam_type == "Mixed":
            question_types.append("MCQ")
        if exam_type == "Short Answer" or exam_type == "Mixed":
            question_types.append("Short Answer")
        if exam_type == "Essay" or exam_type == "Mixed":
            question_types.append("Essay")
            
        q_type = random.choice(question_types)
        
        if q_type == "MCQ":
            question = {
                "id": i + 1,
                "question": f"{difficulty} level {subject} MCQ question #{i+1}",
                "type": "MCQ",
                "marks": 1,
                "options": {
                    "A": f"Option A for question {i+1}",
                    "B": f"Option B for question {i+1}",
                    "C": f"Option C for question {i+1}",
                    "D": f"Option D for question {i+1}"
                },
                "correct_answer": random.choice(["A", "B", "C", "D"])
            }
        elif q_type == "Short Answer":
            question = {
                "id": i + 1,
                "question": f"Explain the concept related to {subject} in brief - Question {i+1}",
                "type": "Short Answer",
                "marks": 2 if difficulty == "Easy" else 3,
                "answer_hint": f"Sample answer hint for {subject} question"
            }
        else:  # Essay
            question = {
                "id": i + 1,
                "question": f"Write a detailed essay on {subject} topic - Question {i+1}",
                "type": "Essay",
                "marks": 5 if difficulty == "Easy" else 8,
                "word_limit": "300-500 words"
            }
        
        questions.append(question)
    
    paper_data = {
        "paper": {
            "title": f"{subject} {difficulty} Level Examination",
            "subject": subject,
            "difficulty": difficulty,
            "exam_type": exam_type,
            "total_questions": num_questions,
            "total_marks": sum(q['marks'] for q in questions),
            "time_duration": parameters.get('time_duration', '1 hour'),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "instructions": [
                "Answer all questions",
                "Write your answers in the space provided",
                "Show all necessary working",
                "Mobile phones are not allowed"
            ],
            "questions": questions
        },
        "message": "Paper generated successfully in demo mode! 🎉"
    }
    
    return paper_data, 200

def generate_paper_smart(parameters):
    """Smart function that works with or without backend"""
    try:
        # Try actual backend if available (for future use)
        BACKEND_URL = "http://localhost:8001"  # This will fail on Streamlit Cloud
        
        response = requests.post(
            f"{BACKEND_URL}/api/generate-paper",
            json=parameters,
            timeout=3  # Short timeout to fail quickly
        )
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            # Fallback to mock
            return mock_generate_paper(parameters)
            
    except requests.exceptions.RequestException:
        # Use mock data when backend is not available
        return mock_generate_paper(parameters)

# Mock authentication functions
def mock_signup(username, email, password):
    return {"message": "Account created successfully! ✅"}, 200

def mock_signin(email, password):
    st.session_state.user = email
    return {"message": f"Welcome back! Signed in as {email}"}, 200

def main():
    st.title("📝 AI-Powered Exam Paper Generator")
    st.markdown("---")
    
    # Demo mode notification
    st.info("🔧 **Demo Mode**: Using mock data for paper generation. Backend integration coming soon!")
    
    if st.session_state.user:
        show_main_app()
    else:
        show_auth_section()

def show_auth_section():
    """Authentication section with mock functions"""
    tab1, tab2 = st.tabs(["🔐 Sign In", "🚀 Sign Up"])
    
    with tab1:
        st.header("Welcome Back!")
        with st.form("signin_form"):
            email = st.text_input("📧 Email Address", placeholder="your@email.com")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if email and password:
                    result, status = mock_signin(email, password)
                    if status == 200:
                        st.success(result['message'])
                        st.rerun()
                else:
                    st.warning("Please fill all fields")
    
    with tab2:
        st.header("Create New Account")
        with st.form("signup_form"):
            username = st.text_input("👤 Username", placeholder="Choose a username")
            email = st.text_input("📧 Email Address", placeholder="your@email.com")
            password = st.text_input("🔑 Password", type="password", placeholder="Create a password")
            submit = st.form_submit_button("Create Account")
            
            if submit:
                if username and email and password:
                    result, status = mock_signup(username, email, password)
                    st.success(result['message'])
                    st.info("You can now sign in with your credentials!")
                else:
                    st.warning("Please fill all fields")

def show_main_app():
    """Main application after login"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header(f"Welcome, {st.session_state.user}! 👋")
    
    with col2:
        if st.button("🚪 Sign Out"):
            st.session_state.user = None
            st.rerun()
    
    # Paper Generation Section
    st.markdown("---")
    st.header("📄 Generate Exam Paper")
    
    with st.form("paper_generation"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox("📚 Subject", ["Mathematics", "Science", "English", "History", "Computer Science"])
            difficulty = st.select_slider("🎯 Difficulty Level", ["Easy", "Medium", "Hard"])
            num_questions = st.slider("❓ Number of Questions", 5, 20, 10)
        
        with col2:
            exam_type = st.selectbox("🏫 Exam Type", ["Multiple Choice", "Short Answer", "Essay", "Mixed"])
            time_duration = st.selectbox("⏱️ Time Duration", ["30 minutes", "1 hour", "2 hours", "3 hours"])
            marks = st.number_input("📊 Total Marks", min_value=10, max_value=100, value=30)
        
        topics = st.text_area("📖 Specific Topics", placeholder="Enter specific topics (comma separated)\nExample: Algebra, Geometry, Calculus")
        
        generate = st.form_submit_button("🎯 Generate Paper")
        
        if generate:
            with st.spinner("🤖 Generating your exam paper..."):
                paper_params = {
                    "subject": subject,
                    "difficulty": difficulty,
                    "num_questions": num_questions,
                    "exam_type": exam_type,
                    "time_duration": time_duration,
                    "total_marks": marks,
                    "topics": [topic.strip() for topic in topics.split(",")] if topics else []
                }
                
                result, status = generate_paper_smart(paper_params)
                
                if status == 200:
                    st.success("✅ Exam paper generated successfully!")
                    display_generated_paper(result)
                    
                    # Save to session state
                    st.session_state.generated_papers.append(result)
                    
                    # Download button
                    download_paper(result, subject, difficulty)
                    
                else:
                    st.error(f"❌ Error: {result.get('detail', 'Unknown error')}")

def display_generated_paper(result):
    """Display the generated paper"""
    st.markdown("---")
    st.header("📝 Generated Exam Paper")
    
    paper = result['paper']
    
    # Paper header
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(paper['title'])
        st.write(f"**Subject:** {paper['subject']}")
        st.write(f"**Difficulty:** {paper['difficulty']}")
    
    with col2:
        st.write(f"**Time:** {paper['time_duration']}")
        st.write(f"**Total Marks:** {paper['total_marks']}")
        st.write(f"**Generated:** {paper['generated_at']}")
    
    # Instructions
    st.markdown("### 📋 Instructions")
    for instruction in paper.get('instructions', []):
        st.write(f"• {instruction}")
    
    # Questions
    st.markdown("### 📝 Questions")
    for question in paper['questions']:
        st.markdown(f"**{question['id']}. {question['question']}**")
        st.write(f"*Type: {question['type']} | Marks: {question['marks']}*")
        
        if question['type'] == 'MCQ' and 'options' in question:
            for opt, value in question['options'].items():
                st.write(f"   {opt}. {value}")
        
        st.write("")

def download_paper(result, subject, difficulty):
    """Download paper as JSON"""
    json_str = json.dumps(result, indent=2)
    
    st.download_button(
        label="📥 Download Paper as JSON",
        data=json_str,
        file_name=f"{subject}_{difficulty}_paper.json",
        mime="application/json"
    )

if __name__ == "__main__":
    main()