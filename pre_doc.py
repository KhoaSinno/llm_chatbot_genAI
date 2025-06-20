import os
import hashlib
import glob
from typing import List, Optional
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
from langchain.schema import Document

# Cấu hình thư mục
DOCUMENTS_DIR = "documents"
VECTOR_STORES_DIR = "vector_stores"


def create_directories():
    """Tạo các thư mục cần thiết"""
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    os.makedirs(VECTOR_STORES_DIR, exist_ok=True)


def get_file_hash(file_path: str) -> str:
    """Tạo hash để identify file duy nhất"""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    return file_hash[:8]  # Lấy 8 ký tự đầu


def get_available_documents() -> List[dict]:
    """Lấy danh sách tất cả documents có sẵn"""
    create_directories()
    documents = []

    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    for pdf_file in pdf_files:
        filename = os.path.basename(pdf_file)
        file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # MB
        file_hash = get_file_hash(pdf_file)

        # Kiểm tra xem có vector store không
        vector_store_path = os.path.join(
            VECTOR_STORES_DIR, f"{filename}_{file_hash}")
        has_vector_store = os.path.exists(vector_store_path)

        documents.append({
            'filename': filename,
            'path': pdf_file,
            'size_mb': round(file_size, 2),
            'hash': file_hash,
            'vector_store_path': vector_store_path,
            'has_vector_store': has_vector_store
        })

    return documents


def process_single_document(pdf_path: str) -> Optional[FAISS]:
    """
    Xử lý một document duy nhất
    """
    try:
        print(f"📄 Đang xử lý: {os.path.basename(pdf_path)}")

        # Load PDF
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        if not documents:
            raise ValueError(f"Không thể đọc nội dung từ file: {pdf_path}")

        # Enhanced text splitting với metadata
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # Giảm chunk size để tăng precision
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len,
        )
        docs = text_splitter.split_documents(documents)

        # Thêm metadata cho từng chunk
        enhanced_docs = []
        filename = os.path.basename(pdf_path)

        for i, doc in enumerate(docs):
            # Filter out empty or meaningless chunks
            if len(doc.page_content.strip()) < 50:
                continue

            # Enhance metadata
            doc.metadata.update({
                'source_file': filename,
                'chunk_id': i,
                'chunk_length': len(doc.page_content),
                'total_chunks': len(docs)
            })
            enhanced_docs.append(doc)

        print(
            f"📝 Tạo {len(enhanced_docs)} chunks chất lượng từ {len(docs)} chunks gốc")

        # Tạo embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Tạo vector store
        vector_store = FAISS.from_documents(enhanced_docs, embeddings)

        # Lưu với tên unique
        file_hash = get_file_hash(pdf_path)
        vector_store_path = os.path.join(
            VECTOR_STORES_DIR, f"{filename}_{file_hash}")
        vector_store.save_local(vector_store_path)

        print(
            f"✅ Đã xử lý thành công {len(documents)} trang, tạo {len(enhanced_docs)} chunks")
        print(f"💾 Lưu vector store tại: {vector_store_path}")

        return vector_store

    except Exception as e:
        print(f"❌ Lỗi xử lý tài liệu {pdf_path}: {e}")
        return None


def load_vector_store(vector_store_path: str) -> Optional[FAISS]:
    """Load một vector store cụ thể"""
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        vector_store = FAISS.load_local(
            vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print(f"✅ Đã load vector store từ: {vector_store_path}")
        return vector_store
    except Exception as e:
        print(f"⚠️ Không thể load vector store {vector_store_path}: {e}")
        return None


def combine_vector_stores(documents: List[dict]) -> Optional[FAISS]:
    """Kết hợp nhiều vector stores thành một"""
    try:
        combined_store = None
        total_docs = 0

        for doc_info in documents:
            if doc_info['has_vector_store']:
                store = load_vector_store(doc_info['vector_store_path'])
                if store:
                    if combined_store is None:
                        combined_store = store
                    else:
                        combined_store.merge_from(store)
                    total_docs += 1
                    print(
                        f"📚 Đã thêm {doc_info['filename']} vào combined store")

        if combined_store:
            print(
                f"✅ Đã kết hợp {total_docs} documents thành combined vector store")
            return combined_store
        else:
            print("❌ Không có vector store nào để kết hợp")
            return None

    except Exception as e:
        print(f"❌ Lỗi kết hợp vector stores: {e}")
        return None


def process_all_documents() -> Optional[FAISS]:
    """Xử lý tất cả documents trong thư mục"""
    documents = get_available_documents()

    if not documents:
        print("❌ Không tìm thấy document nào trong thư mục documents/")
        return None

    print(f"📋 Tìm thấy {len(documents)} documents:")
    for doc in documents:
        status = "✅ Processed" if doc['has_vector_store'] else "⚠️ Not processed"
        print(f"  - {doc['filename']} ({doc['size_mb']} MB) {status}")

    # Xử lý các documents chưa có vector store
    for doc in documents:
        if not doc['has_vector_store']:
            print(f"\n🔄 Xử lý {doc['filename']}...")
            process_single_document(doc['path'])

    # Cập nhật lại danh sách
    documents = get_available_documents()

    # Kết hợp tất cả vector stores
    return combine_vector_stores(documents)


def get_default_vector_store() -> Optional[FAISS]:
    """Lấy vector store mặc định (ưu tiên combined, fallback single)"""
    create_directories()

    # Thử load combined store trước
    documents = get_available_documents()

    if len(documents) > 1:
        # Nhiều documents - tạo combined store
        print("🔄 Có nhiều documents, tạo combined vector store...")
        return process_all_documents()
    elif len(documents) == 1:
        # Một document duy nhất
        doc = documents[0]
        if doc['has_vector_store']:
            print(f"📄 Sử dụng vector store của {doc['filename']}")
            return load_vector_store(doc['vector_store_path'])
        else:
            print(f"🔄 Xử lý document {doc['filename']}...")
            return process_single_document(doc['path'])
    else:
        # Không có document nào - check fallback
        fallback_path = os.path.join(VECTOR_STORES_DIR, "doan3_index")
        if os.path.exists(fallback_path):
            print("📄 Sử dụng vector store cũ (doan3)")
            return load_vector_store(fallback_path)
        else:
            print("❌ Không tìm thấy document nào")
            return None


# Khởi tạo vector store mặc định
print("🚀 Đang khởi tạo vector store system...")
vector_store = get_default_vector_store()

if vector_store is None:
    print("❌ Không thể khởi tạo vector store")
else:
    print("✅ Vector store system sẵn sàng")
