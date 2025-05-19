# Step 1: Import Libraries
import streamlit as st

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ProText AI Summarizer",
    layout="wide",
    page_icon="✍️",
    initial_sidebar_state="expanded"
)

from transformers import pipeline
from PyPDF2 import PdfReader
import docx
import io
import time
from datetime import datetime

# Step 2: Load the Pre-trained Summarization Model
@st.cache_resource
def load_summarizer():
    try:
        return pipeline("summarization", model="facebook/bart-large-cnn")
    except Exception as e:
        st.error(f"Failed to load summarization model: {str(e)}")
        return None

summarizer = load_summarizer()

# Step 3: Define a Function to Split Long Text into Chunks
def split_text(text, max_chunk=500):
    text = text.replace('\n', ' ')
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    chunks.append(current_chunk.strip())
    return chunks

# Step 4: Define a Function to Summarize the Text Chunks
def summarize_text(text, max_length=100, min_length=30):
    if not text.strip():
        return ""
    
    chunks = split_text(text)
    summary = ''
    
    for chunk in chunks:
        chunk_length = len(chunk.split())
        # Dynamically adjust max_length based on input length
        adjusted_max = min(max_length, max(min_length, chunk_length // 2))
        try:
            summarized = summarizer(
                chunk, 
                max_length=adjusted_max, 
                min_length=min_length, 
                do_sample=False
            )
            summary += summarized[0]['summary_text'] + ' '
        except Exception as e:
            st.warning(f"Error summarizing a chunk: {str(e)}")
            continue
            
    return summary.strip()

# Step 5: File Processing Functions
def extract_text_from_pdf(uploaded_file):
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(uploaded_file):
    try:
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
    except Exception as e:
        st.error(f"Failed to extract text from Word document: {str(e)}")
        return ""

# Custom CSS for beautiful styling
st.markdown("""
<style>
    :root {
        --primary: #4a6fa5;
        --secondary: #166088;
        --accent: #4fc3f7;
        --background: #f8f9fa;
        --text: #333333;
        --card: #ffffff;
    }
    
    .stApp {
        background-color: var(--background);
    }
    
    .stTextArea textarea {
        min-height: 300px;
        border-radius: 10px;
        border: 1px solid #ced4da;
        padding: 15px;
    }
    
    .stButton>button {
        border-radius: 8px;
        border: none;
        background-color: var(--primary);
        color: white;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .stDownloadButton>button {
        border-radius: 8px;
        border: none;
        background-color: var(--accent);
        color: white;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stDownloadButton>button:hover {
        background-color: #039be5;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .summary-box {
        background-color: var(--card);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 4px solid var(--primary);
        color: black;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        transition: all 0.3s;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }
    
    .metric-box {
        background-color: var(--card);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        color: black;
    }
    
    .file-info {
        background-color: var(--card);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    h1, h2, h3 {
        color: var(--secondary) !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #166088; font-size: 2.5rem;">✍️ ProText AI Summarizer</h1>
    <p style="font-size: 1.1rem; color: #4a6fa5;">
        Transform lengthy documents into concise summaries with state-of-the-art AI technology
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.markdown("""
    <div style="background-color: #166088; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <h3 style="color: white; margin: 0;">⚙️ Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    
    max_length = st.slider("Maximum summary length (words)", 30, 300, 100)
    min_length = st.slider("Minimum summary length (words)", 10, 100, 30)
    
    st.markdown("---")
    
    st.markdown("""
    <div style="background-color: #f0f0f0; padding: 15px; border-radius: 10px;">
        <h3 style="color: black; margin: 0;">ℹ️ About</h3
    </div>
      <p style="font-size: 0.9rem; color: black;">
        This powerful tool uses state-of-the-art AI models to generate human-like summaries in multiple languages.
        It automatically processes long documents by splitting them into manageable chunks.
    </p>
    """, unsafe_allow_html=True)

# Main content
tab1, tab2 = st.tabs(["📝 Text Input", "📂 File Upload"])

with tab1:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3>Paste your text below</h3>
        <p>Enter any text you want to summarize, from articles to reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_input = st.text_area("", height=300, key="text_input", placeholder="Paste your text here...", label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        summarize_btn = st.button("✨ Generate Summary", key="summarize_text")
    with col2:
        clear_btn = st.button("🗑️ Clear Text", key="clear_text")
    
    if clear_btn:
        user_input = ""
        st.experimental_rerun()
    
    if summarize_btn and summarizer:
        if not user_input.strip():
            st.warning("Please enter some text to summarize.")
        else:
            with st.spinner("🔍 Analyzing and generating summary..."):
                start_time = time.time()
                summary = summarize_text(user_input, max_length, min_length)
                end_time = time.time()
                
                if summary and summary.strip():  # Double-check we have a non-empty summary
                    st.markdown("""
                    <div style="margin-top: 30px;">
                        <h3>📋 Summary</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display summary in a styled box
                    st.markdown(f"""
                    <div class="summary-box">
                        {summary}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Summary metrics
                    original_length = len(user_input.split())
                    summary_length = len(summary.split())
                    reduction = int((1 - (summary_length / original_length))) * 100
                    processing_time = round(end_time - start_time, 2)
                    
                    st.markdown(f"""
                    <div class="metric-box">
                        <h4>📊 Summary Metrics</h4>
                        <p><strong>Original length:</strong> {original_length} words</p>
                        <p><strong>Summary length:</strong> {summary_length} words ({reduction}% reduction)</p>
                        <p><strong>Processing time:</strong> {processing_time} seconds</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download button
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="💾 Download Summary",
                        data=summary,
                        file_name=f"summary_{timestamp}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Failed to generate a meaningful summary. Please try with different text.")

with tab2:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3>Upload your document</h3>
        <p>Supported formats: PDF and Word documents (.docx)</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["pdf", "docx"], label_visibility="collapsed")
    
    if uploaded_file is not None and summarizer:
        st.markdown(f"""
        <div class="file-info">
            <h4>📄 File Information</h4>
            <p><strong>Filename:</strong> {uploaded_file.name}</p>
            <p><strong>File size:</strong> {uploaded_file.size / 1024:.2f} KB</p>
            <p><strong>File type:</strong> {uploaded_file.type.split('/')[-1].upper()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Summarize Document", key="summarize_file"):
            with st.spinner("📂 Extracting text and generating summary..."):
                try:
                    text = ""
                    if uploaded_file.type == "application/pdf":
                        text = extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = extract_text_from_docx(uploaded_file)
                    
                    if not text.strip():
                        st.error("No text could be extracted from the document.")
                    else:
                        start_time = time.time()
                        summary = summarize_text(text, max_length, min_length)
                        end_time = time.time()
                        
                        if summary and summary.strip():  # Double-check we have a non-empty summary
                            st.markdown("""
                            <div style="margin-top: 20px;">
                                <h3>📋 Document Summary</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display summary in a styled box
                            st.markdown(f"""
                            <div class="summary-box">
                                {summary}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Summary metrics
                            original_length = len(text.split())
                            summary_length = len(summary.split())
                            reduction = int((1 - (summary_length / original_length)) )* 100
                            processing_time = round(end_time - start_time, 2)
                            
                            st.markdown(f"""
                            <div class="metric-box">
                                <h4>📊 Summary Metrics</h4>
                                <p><strong>Original length:</strong> {original_length} words</p>
                                <p><strong>Summary length:</strong> {summary_length} words ({reduction}% reduction)</p>
                                <p><strong>Processing time:</strong> {processing_time} seconds</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                st.download_button(
                                    label="💾 Download Summary",
                                    data=summary,
                                    file_name=f"summary_{timestamp}.txt",
                                    mime="text/plain"
                                )
                            with col2:
                                st.download_button(
                                    label="📥 Download Extracted Text",
                                    data=text,
                                    file_name=f"extracted_text_{timestamp}.txt",
                                    mime="text/plain"
                                )
                        else:
                            st.error("Failed to generate a meaningful summary from the document.")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; color: #666; font-size: 0.9rem;">
    <p>AI Text Summarizer Pro • Powered by BART Transformers • Streamlit</p>
</div>
""", unsafe_allow_html=True)