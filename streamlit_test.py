# streamlit_test.py
import streamlit as st
import requests
import json
import io
import base64
from typing import Dict, Any

# FastAPI backend URL
BASE_URL = "http://localhost:8001"  # Change if your backend runs on different port

def main():
    st.set_page_config(page_title="Exam Generator Test", page_icon="📝", layout="wide")
    
    st.title("🎓 Exam Generator Testing Dashboard")
    st.markdown("Test your FastAPI backend through Streamlit")
    
    # Sidebar for API status
    with st.sidebar:
        st.header("API Status")
        if st.button("Check API Status"):
            check_api_status()
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 Generate Paper", 
        "📊 Service Status", 
        "🔍 Test Endpoints",
        "📋 Saved Papers"
    ])
    
    with tab1:
        test_paper_generation()
    
    with tab2:
        test_service_status()
    
    with tab3:
        test_other_endpoints()
    
    with tab4:
        view_saved_papers()

def check_api_status():
    """Check if FastAPI backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            st.sidebar.success("✅ Backend is running!")
        else:
            st.sidebar.error(f"❌ Backend returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.sidebar.error("❌ Cannot connect to backend. Make sure it's running on port 8000")

def test_paper_generation():
    """Test the paper generation endpoint"""
    st.header("📄 Generate Exam Paper")
    
    with st.form("paper_generation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            paper_heading = st.text_input("Paper Heading", "Computer Science Exam")
            total_marks = st.number_input("Total Marks", min_value=10, max_value=200, value=30)
            
            st.subheader("Question Counts")
            mcq_count = st.number_input("MCQ Count", min_value=0, max_value=20, value=5)
            saq_count = st.number_input("Short Answer Count", min_value=0, max_value=10, value=3)
            laq_count = st.number_input("Long Answer Count", min_value=0, max_value=5, value=2)
        
        with col2:
            st.subheader("Difficulty Levels")
            mcq_difficulty = st.selectbox("MCQ Difficulty", ["easy", "medium", "hard"], index=1)
            saq_difficulty = st.selectbox("Short Answer Difficulty", ["easy", "medium", "hard"], index=1)
            laq_difficulty = st.selectbox("Long Answer Difficulty", ["easy", "medium", "hard"], index=1)
            
            st.subheader("Student Info")
            include_roll = st.checkbox("Include Roll Number", value=True)
            include_name = st.checkbox("Include Name", value=True)
            include_class = st.checkbox("Include Class/Section", value=True)
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload PDF Files", 
            type=["pdf"], 
            accept_multiple_files=True,
            help="Upload one or more PDF files for content extraction"
        )
        
        submitted = st.form_submit_button("🚀 Generate Exam Paper")
        
        if submitted:
            if not uploaded_files:
                st.error("Please upload at least one PDF file")
                return
            
            generate_paper(
                paper_heading, total_marks,
                include_roll, include_name, include_class,
                mcq_count, saq_count, laq_count,
                mcq_difficulty, saq_difficulty, laq_difficulty,
                uploaded_files
            )

def generate_paper(paper_heading, total_marks, include_roll, include_name, include_class,
                  mcq_count, saq_count, laq_count, mcq_difficulty, saq_difficulty, laq_difficulty,
                  uploaded_files):
    """Call the paper generation API"""
    
    with st.spinner("🔄 Generating exam paper..."):
        try:
            # Prepare files and form data
            files = []
            for uploaded_file in uploaded_files:
                files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")))
            
            data = {
                "paperHeading": paper_heading,
                "totalMarks": total_marks,
                "includeRollNumber": str(include_roll).lower(),
                "includeName": str(include_name).lower(),
                "includeClassSection": str(include_class).lower(),
                "mcqCount": mcq_count,
                "mcqDifficulty": mcq_difficulty,
                "saqCount": saq_count,
                "saqDifficulty": saq_difficulty,
                "laqCount": laq_count,
                "laqDifficulty": laq_difficulty
            }
            
            # Make API call
            response = requests.post(
                f"{BASE_URL}/api/generate-paper",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Paper generated successfully!")
                
                # Display results
                display_generation_results(result)
                
                # Show download option
                if st.button("📥 Download Generated Paper"):
                    download_generated_paper()
                    
            else:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error generating paper: {str(e)}")

def display_generation_results(result):
    """Display the paper generation results"""
    st.subheader("Generation Results")
    
    # Paper info
    if "paper" in result:
        paper_info = result["paper"]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Content Based", "Yes" if paper_info.get("content_based") else "No")
        with col2:
            st.metric("Service Used", "Yes" if paper_info.get("service_used") else "No")
        with col3:
            st.metric("Files Processed", paper_info.get("extracted_content_files", 0))
    
    # Show latest paper
    try:
        paper_response = requests.get(f"{BASE_URL}/api/latest-paper")
        if paper_response.status_code == 200:
            latest_paper = paper_response.json()
            
            st.subheader("Generated Paper Preview")
            st.text_area("Questions", latest_paper.get("questions", "No questions generated"), height=300)
            
            # Paper metadata
            with st.expander("Paper Metadata"):
                st.json(latest_paper)
                
    except Exception as e:
        st.warning(f"Could not fetch latest paper: {str(e)}")

def download_generated_paper():
    """Download the generated paper as PDF"""
    try:
        # Get latest paper data
        paper_response = requests.get(f"{BASE_URL}/api/latest-paper")
        if paper_response.status_code == 200:
            paper_data = paper_response.json()
            
            # Call download endpoint
            download_response = requests.post(
                f"{BASE_URL}/api/download-paper",
                json=paper_data
            )
            
            if download_response.status_code == 200:
                # Create download link
                pdf_data = download_response.content
                b64_pdf = base64.b64encode(pdf_data).decode()
                
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="generated_paper.pdf">📥 Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
            else:
                st.error("❌ Failed to generate PDF download")
                
    except Exception as e:
        st.error(f"❌ Error downloading paper: {str(e)}")

def test_service_status():
    """Test various service status endpoints"""
    st.header("📊 Service Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Check Exam Service"):
            check_exam_service()
    
    with col2:
        if st.button("Check Gemini Status"):
            check_gemini_status()
    
    with col3:
        if st.button("System Health"):
            check_system_health()

def check_exam_service():
    """Check exam service status"""
    try:
        response = requests.get(f"{BASE_URL}/api/exam-service-status")
        if response.status_code == 200:
            status_data = response.json()
            st.write("**Exam Service Status:**")
            st.json(status_data)
        else:
            st.error(f"Failed to get status: {response.status_code}")
    except Exception as e:
        st.error(f"Error checking exam service: {str(e)}")

def check_gemini_status():
    """Check Gemini AI status"""
    try:
        # You might need to create this endpoint in your FastAPI
        response = requests.get(f"{BASE_URL}/api/gemini-status")
        if response.status_code == 200:
            st.write("**Gemini AI Status:**")
            st.json(response.json())
        else:
            st.info("Gemini status endpoint not available")
    except:
        st.info("Gemini status check not implemented")

def check_system_health():
    """Check overall system health"""
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            st.success("✅ Backend server is running")
        else:
            st.error("❌ Backend server issues")
    except:
        st.error("❌ Cannot connect to backend")

def test_other_endpoints():
    """Test other API endpoints"""
    st.header("🔍 Test Other Endpoints")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Test PDF Upload"):
            test_pdf_upload()
        
        if st.button("Test Question Generation"):
            test_question_generation()
    
    with col2:
        if st.button("List All Endpoints"):
            list_endpoints()
        
        if st.button("Clear Test Data"):
            clear_test_data()

def test_pdf_upload():
    """Test PDF upload functionality"""
    st.info("PDF upload is tested in the main paper generation form")

def test_question_generation():
    """Test direct question generation"""
    try:
        response = requests.post(f"{BASE_URL}/api/test-exam-generation")
        if response.status_code == 200:
            result = response.json()
            st.write("**Test Generation Results:**")
            st.json(result)
        else:
            st.error(f"Test failed: {response.status_code}")
    except Exception as e:
        st.error(f"Error testing question generation: {str(e)}")

def list_endpoints():
    """List available API endpoints"""
    try:
        response = requests.get(f"{BASE_URL}/")
        st.write("**Available Endpoints:**")
        st.code(response.text)
    except Exception as e:
        st.error(f"Error listing endpoints: {str(e)}")

def clear_test_data():
    """Clear test data"""
    try:
        # You might want to implement this in your backend
        st.info("Clear functionality would be implemented here")
    except Exception as e:
        st.error(f"Error clearing data: {str(e)}")

def view_saved_papers():
    """View saved papers"""
    st.header("📋 Saved Papers")
    
    try:
        response = requests.get(f"{BASE_URL}/api/saved-papers")
        if response.status_code == 200:
            papers = response.json()
            
            if papers:
                st.write(f"Found {len(papers)} saved papers:")
                
                for paper in papers:
                    with st.expander(f"📄 {paper.get('title', 'Untitled')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**ID:** {paper.get('id')}")
                            st.write(f"**Level:** {paper.get('level')}")
                            st.write(f"**Date:** {paper.get('date')}")
                            st.write(f"**Marks:** {paper.get('total_marks', 'N/A')}")
                        
                        with col2:
                            if st.button(f"View", key=f"view_{paper.get('id')}"):
                                st.text_area("Questions", paper.get('questions', ''), height=200)
                            
                            if st.button(f"Delete", key=f"delete_{paper.get('id')}"):
                                delete_paper(paper.get('id'))
            else:
                st.info("No saved papers found")
        else:
            st.error(f"Failed to fetch papers: {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching saved papers: {str(e)}")

def delete_paper(paper_id):
    """Delete a paper"""
    try:
        response = requests.delete(f"{BASE_URL}/api/paper/{paper_id}")
        if response.status_code == 200:
            st.success("✅ Paper deleted successfully")
            st.rerun()
        else:
            st.error(f"Failed to delete paper: {response.status_code}")
    except Exception as e:
        st.error(f"Error deleting paper: {str(e)}")

if __name__ == "__main__":
    main()