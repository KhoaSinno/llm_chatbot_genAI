import streamlit as st
import sys
import os

# Thêm đường dẫn hiện tại vào sys.path để import được các module local
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from llm_rag import qa_chain, create_qa_chain
except ImportError as e:
    st.error(f"Lỗi import: {e}")
    st.stop()

st.set_page_config(
    page_title="Chatbot Tra cứu Thông tin",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Chatbot Tra cứu Thông tin")
st.markdown("---")

# Sidebar để chọn model
with st.sidebar:
    st.header("⚙️ Cấu hình Model")

    model_choice = st.selectbox(
        "Chọn AI Model:",
        ["gemini", "openai"],
        index=0,
        help="OpenAI GPT hoặc Google Gemini"
    )

    if model_choice == "openai":
        st.info("🤖 OpenAI GPT - Chất lượng cao")
        st.caption("💰 Chi phí: ~$0.002/1000 tokens")
    else:
        st.info("🤖 Google Gemini - Hiệu suất tốt")
        st.caption("💰 Chi phí: Miễn phí với quota giới hạn")

    st.markdown("---")
    st.markdown("**📊 API Status:**")

    # Kiểm tra API keys
    import os
    from dotenv import load_dotenv
    load_dotenv('config.env')

    openai_key = os.getenv('OPENAI_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')

    if openai_key and openai_key != 'your_openai_api_key_here':
        st.success("✅ OpenAI API Key OK")
    else:
        st.error("❌ OpenAI API Key Missing")

    if gemini_key and gemini_key != 'your_gemini_api_key_here':
        st.success("✅ Gemini API Key OK")
    else:
        st.error("❌ Gemini API Key Missing")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_input(
        "💬 Nhập câu hỏi của bạn:",
        placeholder="VD: Tài liệu nói về gì?",
        help="Hãy đặt câu hỏi liên quan đến nội dung tài liệu PDF"
    )

with col2:
    search_button = st.button("🔍 Tìm kiếm", type="primary")

if query and (search_button or st.session_state.get('auto_search', True)):
    try:
        # Tạo lại qa_chain nếu người dùng thay đổi model
        if 'current_model' not in st.session_state or st.session_state.current_model != model_choice:
            with st.spinner("Đang khởi tạo model..."):
                qa_chain = create_qa_chain(model_choice)
                st.session_state.current_model = model_choice

        # Thực hiện truy vấn
        with st.spinner("Đang tìm kiếm thông tin..."):
            if hasattr(qa_chain, 'invoke'):
                result = qa_chain.invoke({"query": query})
                response = result.get(
                    'result', 'Không tìm thấy thông tin phù hợp.')
                source_docs = result.get('source_documents', [])
            else:
                # Fallback cho phiên bản cũ
                response = qa_chain.run(query)
                source_docs = []

        # Hiển thị kết quả
        st.markdown("### 💡 **Câu trả lời:**")
        st.success(response)

        # Hiển thị nguồn tham khảo nếu có
        if source_docs:
            with st.expander("📚 Nguồn tham khảo"):
                # Hiển thị tối đa 3 nguồn
                for i, doc in enumerate(source_docs[:10]):
                    st.markdown(f"**Nguồn {i+1}:**")
                    st.text(doc.page_content[:200] + "...")
                    st.markdown("---")

    except Exception as e:
        st.error(f"❌ Có lỗi xảy ra: {str(e)}")
        st.info("💡 Hãy kiểm tra lại cấu hình API key hoặc thử sử dụng Hugging Face")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p><small>🚀 Hệ thống Chatbot RAG - Developed with ❤️</small></p>
    </div>
    """,
    unsafe_allow_html=True
)
