import os
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    # Fallback cho phiên bản cũ
    from langchain.document_loaders import PyPDFLoader
    from langchain.vectorstores import FAISS
    from langchain.embeddings import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_and_process_documents(pdf_path="doan3.pdf"):
    """
    Load và xử lý tài liệu PDF
    """
    try:
        # Kiểm tra file PDF có tồn tại không
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")

        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            raise ValueError(f"Không thể đọc nội dung từ file: {pdf_path}")

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        docs = text_splitter.split_documents(documents)

        # Tạo embeddings và vector store
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        vector_store = FAISS.from_documents(docs, embeddings)

        # Lưu vector store để tái sử dụng
        vector_store.save_local("faiss_index")

        print(
            f"✅ Đã xử lý thành công {len(documents)} trang, tạo {len(docs)} chunks")
        return vector_store

    except Exception as e:
        print(f"❌ Lỗi xử lý tài liệu: {e}")
        return None


def load_existing_vector_store():
    """
    Load vector store đã có (nếu có)
    """
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        vector_store = FAISS.load_local(
            "faiss_index", embeddings, allow_dangerous_deserialization=True)
        print("✅ Đã load vector store từ cache")
        return vector_store
    except:
        return None


# Khởi tạo vector store
print("Đang khởi tạo vector store...")
vector_store = load_existing_vector_store()

if vector_store is None:
    print("Tạo vector store mới...")
    vector_store = load_and_process_documents()

if vector_store is None:
    print("❌ Không thể khởi tạo vector store")
else:
    print("✅ Vector store sẵn sàng")
