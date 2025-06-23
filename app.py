import streamlit as st
import sys
import os
import shutil

# Thêm đường dẫn hiện tại vào sys.path để import được các module local
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from llm_rag import qa_chain, create_qa_chain
    from pre_doc import (
        get_available_documents,
        process_single_document,
        get_default_vector_store,
        process_all_documents,
        DOCUMENTS_DIR
    )
except ImportError as e:
    st.error(f"Lỗi import: {e}")
    st.stop()

st.set_page_config(
    page_title="Chatbot RAG Multi-Document",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Chatbot RAG Multi-Document")
st.markdown("---")

# Sidebar để chọn model và quản lý tài liệu
with st.sidebar:
    st.header("⚙️ Cấu hình System")

    # Tab để chọn giữa cấu hình và quản lý file
    tab1, tab2 = st.tabs(["🔧 Model", "📚 Tài liệu"])
    
    with tab1:
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
    
    with tab2:
        st.subheader("📂 Quản lý Tài liệu")
        
        # Upload file mới
        uploaded_file = st.file_uploader(
            "📤 Upload PDF mới:",
            type=['pdf'],
            help="Chọn file PDF để thêm vào hệ thống"
        )
        
        if uploaded_file is not None:
            # Tạo thư mục documents nếu chưa có
            os.makedirs(DOCUMENTS_DIR, exist_ok=True)
            
            # Lưu file
            file_path = os.path.join(DOCUMENTS_DIR, uploaded_file.name)
            
            # Kiểm tra xem file đã tồn tại chưa
            if os.path.exists(file_path):
                st.warning(f"⚠️ File '{uploaded_file.name}' đã tồn tại!")
                if st.button("🔄 Ghi đè file", key="overwrite"):
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    st.success(f"✅ Đã cập nhật '{uploaded_file.name}'")
                    st.rerun()
            else:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                st.success(f"✅ Đã upload '{uploaded_file.name}'")
                
                # Tự động xử lý file mới
                with st.spinner("🔄 Đang xử lý file mới..."):
                    try:
                        vector_store = process_single_document(file_path)
                        if vector_store:
                            st.success("✅ Đã tạo vector store cho file mới!")
                            st.rerun()
                        else:
                            st.error("❌ Không thể xử lý file!")
                    except Exception as e:
                        st.error(f"❌ Lỗi xử lý file: {e}")

        st.markdown("---")
        
        # Hiển thị danh sách file hiện có
        st.subheader("📋 Tài liệu có sẵn")
        
        documents = get_available_documents()
        if documents:
            for doc in documents:
                with st.expander(f"📄 {doc['filename']} ({doc['size_mb']} MB)"):
                    st.write(f"**Hash:** {doc['hash']}")
                    st.write(f"**Vector Store:** {'✅ Sẵn sàng' if doc['has_vector_store'] else '❌ Chưa xử lý'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if not doc['has_vector_store']:
                            if st.button(f"🔄 Xử lý", key=f"process_{doc['hash']}"):
                                with st.spinner("🔄 Đang xử lý..."):
                                    try:
                                        vector_store = process_single_document(doc['path'])
                                        if vector_store:
                                            st.success("✅ Đã xử lý!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Lỗi xử lý!")
                                    except Exception as e:
                                        st.error(f"❌ Lỗi: {e}")
                    
                    with col2:
                        if st.button(f"🗑️ Xóa", key=f"delete_{doc['hash']}"):
                            try:
                                # Xóa file PDF
                                if os.path.exists(doc['path']):
                                    os.remove(doc['path'])
                                
                                # Xóa vector store
                                if os.path.exists(doc['vector_store_path']):
                                    shutil.rmtree(doc['vector_store_path'])
                                
                                st.success(f"✅ Đã xóa '{doc['filename']}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Lỗi xóa file: {e}")
            
            # Button để rebuild toàn bộ hệ thống
            st.markdown("---")
            if st.button("🔄 Rebuild toàn bộ Vector Store", key="rebuild_all"):
                with st.spinner("🔄 Đang rebuild toàn bộ hệ thống..."):
                    try:
                        combined_store = process_all_documents()
                        if combined_store:
                            st.success("✅ Đã rebuild toàn bộ hệ thống!")
                            # Reset qa_chain để dùng vector store mới
                            if 'current_model' in st.session_state:
                                del st.session_state.current_model
                        else:
                            st.error("❌ Không thể rebuild hệ thống!")
                    except Exception as e:
                        st.error(f"❌ Lỗi rebuild: {e}")
        else:
            st.info("📭 Chưa có tài liệu nào. Hãy upload file PDF!")
        
        # Hiển thị tổng số tài liệu
        processed_count = len([d for d in documents if d['has_vector_store']])
        st.markdown(f"**📊 Tổng quan:** {len(documents)} file, {processed_count} đã xử lý")

# Main interface
st.subheader("🤖 Tra cứu Thông tin")

# Hiển thị thông tin về tài liệu đang sử dụng
documents = get_available_documents()
processed_docs = [d for d in documents if d['has_vector_store']]

if processed_docs:
    doc_names = [d['filename'] for d in processed_docs]
    if len(doc_names) == 1:
        st.info(f"📖 Đang sử dụng: **{doc_names[0]}**")
    else:
        st.info(f"📚 Đang sử dụng: **{len(doc_names)} tài liệu** ({', '.join(doc_names[:3])}{'...' if len(doc_names) > 3 else ''})")
else:
    st.warning("⚠️ Chưa có tài liệu nào được xử lý. Hãy upload và xử lý file PDF trong sidebar!")
    st.stop()

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
                # Nhóm theo file nguồn
                sources_by_file = {}
                for doc in source_docs[:10]:
                    source_file = doc.metadata.get('source_file', 'Unknown')
                    if source_file not in sources_by_file:
                        sources_by_file[source_file] = []
                    sources_by_file[source_file].append(doc)
                
                # Hiển thị theo từng file
                for file_name, docs in sources_by_file.items():
                    st.markdown(f"**📄 {file_name}** ({len(docs)} đoạn)")
                    for i, doc in enumerate(docs[:3]):  # Hiển thị tối đa 3 đoạn mỗi file
                        page_num = doc.metadata.get('page', 'N/A')
                        st.markdown(f"*Trang {page_num}:*")
                        st.text(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                        if i < len(docs[:3]) - 1:
                            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Có lỗi xảy ra: {str(e)}")
        st.info("💡 Hãy kiểm tra lại cấu hình API key hoặc thử sử dụng model khác")

# Statistics và information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📄 Tổng tài liệu", 
        value=len(documents),
        help="Số lượng file PDF đã upload"
    )

with col2:
    st.metric(
        label="✅ Đã xử lý", 
        value=len(processed_docs),
        help="Số tài liệu đã được tạo vector store"
    )

with col3:
    total_size = sum([d['size_mb'] for d in documents])
    st.metric(
        label="💾 Tổng dung lượng", 
        value=f"{total_size:.1f} MB",
        help="Tổng dung lượng các file PDF"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p><small>🚀 Hệ thống Chatbot RAG Multi-Document - Developed with ❤️</small></p>
        <p><small>📁 Quản lý nhiều tài liệu | 🔍 Tìm kiếm thông minh | 📤 Upload dễ dàng</small></p>
    </div>
    """,
    unsafe_allow_html=True
)
