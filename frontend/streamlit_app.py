"""Streamlit frontend for FinWise-AI."""

import streamlit as st
import requests
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="FinWise-AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖💰 FinWise-AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multimodal RAG-Enhanced AI Assistant for Financial Document Analysis</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio(
        "Go to",
        ["🏠 Home", "📄 Upload Documents", "🔍 Query Documents", "💻 Generate Code", "📊 Analysis", "📈 Dashboard"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    FinWise-AI uses cutting-edge AI to:
    - 📄 Process financial documents
    - 🔍 Answer questions using RAG
    - 💻 Generate analysis code
    - 📊 Categorize & forecast expenses
    - 🔒 Detect PII and anomalies
    """)
    
    st.markdown("---")
    # Check API health
    try:
        response = requests.get(f"{API_URL.replace('/api/v1', '')}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.error("❌ API Error")
    except:
        st.warning("⚠️ API Offline")

# Home Page
if page == "🏠 Home":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents Processed", "0", "0")
    with col2:
        st.metric("Queries Answered", "0", "0")
    with col3:
        st.metric("Insights Generated", "0", "0")
    
    st.markdown("---")
    
    st.subheader("🚀 Quick Start")
    st.markdown("""
    1. **Upload Documents**: Go to the Upload page and add your financial PDFs
    2. **Query**: Ask questions about your documents in natural language
    3. **Analyze**: Get automated categorization and insights
    4. **Generate Code**: Create Python code for custom analysis
    """)
    
    st.subheader("✨ Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Document Processing**
        - PDF text extraction
        - OCR for images
        - Table detection
        - PII redaction
        """)
    
    with col2:
        st.markdown("""
        **AI Analysis**
        - RAG-powered Q&A
        - Expense categorization
        - Anomaly detection
        - Trend forecasting
        """)

# Upload Documents Page
elif page == "📄 Upload Documents":
    st.header("📄 Upload Financial Documents")
    
    st.info("Supported formats: PDF, PNG, JPG, JPEG, DOCX")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "png", "jpg", "jpeg", "docx"],
        help="Upload financial documents like bank statements, invoices, or reports"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
            st.write(f"**Type:** {uploaded_file.type}")
        
        with col2:
            if st.button("📤 Upload and Process", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_URL}/documents/upload", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                            
                            # Display results
                            st.json(result)
                            
                            # Store document ID in session state
                            if 'document_ids' not in st.session_state:
                                st.session_state.document_ids = []
                            st.session_state.document_ids.append(result['document_id'])
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Query Documents Page
elif page == "🔍 Query Documents":
    st.header("🔍 Query Your Documents")
    
    query = st.text_input(
        "Ask a question about your documents:",
        placeholder="e.g., What's the total expenses in Q3?",
        help="Enter a natural language question"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"])
    with col2:
        max_results = st.number_input("Max Results", 1, 10, 5)
    
    if st.button("🔍 Search", type="primary"):
        if query:
            with st.spinner("Searching..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        json={"query": query, "model": model, "max_results": max_results}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("### 💡 Answer")
                        st.markdown(result["answer"])
                        
                        st.markdown(f"**Processing Time:** {result['processing_time']:.2f}s")
                        st.markdown(f"**Model Used:** {result['model_used']}")
                        
                        if result.get("sources"):
                            st.markdown("### 📚 Sources")
                            for i, source in enumerate(result["sources"], 1):
                                with st.expander(f"Source {i}"):
                                    st.write(source)
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question")

# Generate Code Page
elif page == "💻 Generate Code":
    st.header("💻 Generate Analysis Code")
    
    task = st.text_area(
        "Describe what you want to analyze:",
        placeholder="e.g., Create a bar chart showing monthly expenses by category",
        height=100
    )
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Language", ["python", "r", "sql"])
    with col2:
        doc_id = st.text_input("Document ID (optional)")
    
    if st.button("🚀 Generate", type="primary"):
        if task:
            with st.spinner("Generating code..."):
                try:
                    response = requests.post(
                        f"{API_URL}/generate-code",
                        json={"task": task, "language": language, "document_id": doc_id or None}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("### 📝 Generated Code")
                        st.code(result["code"], language=language)
                        
                        st.markdown("### 💡 Explanation")
                        st.write(result["explanation"])
                        
                        if result.get("dependencies"):
                            st.markdown("### 📦 Dependencies")
                            st.write(", ".join(result["dependencies"]))
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please describe the task")

# Analysis Page
elif page == "📊 Analysis":
    st.header("📊 Financial Analysis")
    
    doc_id = st.text_input("Document ID:", help="Enter the document ID from upload")
    
    analysis_type = st.selectbox(
        "Analysis Type",
        ["categorization", "forecasting", "summary", "anomaly_detection"]
    )
    
    if st.button("🔬 Analyze", type="primary"):
        if doc_id:
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/analyze",
                        json={"document_id": doc_id, "analysis_type": analysis_type}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("### 📊 Results")
                        st.json(result["results"])
                        
                        if result.get("insights"):
                            st.markdown("### 💡 Insights")
                            for insight in result["insights"]:
                                st.write(f"- {insight}")
                    else:
                        st.error(f"❌ Error: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a document ID")

# Dashboard Page
elif page == "📈 Dashboard":
    st.header("📈 Analytics Dashboard")
    
    # Sample data for visualization
    st.subheader("Expense Categories")
    sample_data = pd.DataFrame({
        'Category': ['Food', 'Transport', 'Housing', 'Utilities', 'Other'],
        'Amount': [1200, 450, 2000, 300, 500]
    })
    
    fig = px.pie(sample_data, values='Amount', names='Category', title='Expense Distribution')
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Trend")
        trend_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Expenses': [4200, 3800, 4500, 4100, 4300, 4450]
        })
        fig2 = px.line(trend_data, x='Month', y='Expenses', markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.subheader("Top Merchants")
        merchant_data = pd.DataFrame({
            'Merchant': ['Amazon', 'Walmart', 'Shell', 'Starbucks', 'Target'],
            'Total': [850, 620, 340, 180, 290]
        })
        fig3 = px.bar(merchant_data, x='Merchant', y='Total')
        st.plotly_chart(fig3, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>Built with ❤️ using FastAPI, LangChain, and Streamlit | "
    "<a href='http://localhost:8000/api/docs' target='_blank'>API Docs</a></div>",
    unsafe_allow_html=True
)