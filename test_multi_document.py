#!/usr/bin/env python3
"""
Test script cho hệ thống RAG chatbot multi-document
"""

from llm_rag import create_qa_chain
from pre_doc import (
    get_available_documents,
    process_single_document,
    process_all_documents,
    get_default_vector_store
)
import os
import sys
from dotenv import load_dotenv

# Thêm đường dẫn current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv('config.env')


def test_document_management():
    """Test các chức năng quản lý tài liệu"""
    print("🔍 Testing Document Management...")

    # 1. Kiểm tra danh sách tài liệu
    documents = get_available_documents()
    print(f"📊 Tìm thấy {len(documents)} tài liệu:")

    for doc in documents:
        print(f"  📄 {doc['filename']}")
        print(f"     Size: {doc['size_mb']} MB")
        print(f"     Hash: {doc['hash']}")
        print(f"     Vector Store: {'✅' if doc['has_vector_store'] else '❌'}")
        print()

    return documents


def test_vector_store_creation():
    """Test tạo vector store cho các tài liệu"""
    print("🔧 Testing Vector Store Creation...")

    documents = get_available_documents()

    for doc in documents:
        if not doc['has_vector_store']:
            print(f"📄 Processing {doc['filename']}...")
            try:
                vector_store = process_single_document(doc['path'])
                if vector_store:
                    print(
                        f"✅ Successfully created vector store for {doc['filename']}")
                else:
                    print(
                        f"❌ Failed to create vector store for {doc['filename']}")
            except Exception as e:
                print(f"❌ Error processing {doc['filename']}: {e}")
        else:
            print(f"✅ {doc['filename']} already has vector store")


def test_combined_search():
    """Test tìm kiếm trên nhiều tài liệu"""
    print("🔍 Testing Multi-Document Search...")

    try:
        # Tạo qa_chain
        qa_chain = create_qa_chain("gemini")

        # Test queries
        test_queries = [
            "Tài liệu này nói về gì?",
            "Có những chủ đề chính nào được đề cập?",
            "Giải thích về cơ sở dữ liệu",
            "Thông tin về hệ thống quản lý"
        ]

        for query in test_queries:
            print(f"\n❓ Query: {query}")
            try:
                result = qa_chain.invoke({"query": query})
                response = result.get('result', 'Không có kết quả')
                source_docs = result.get('source_documents', [])

                print(f"✅ Response: {response[:200]}...")

                # Hiển thị nguồn
                if source_docs:
                    sources = {}
                    for doc in source_docs[:3]:
                        source_file = doc.metadata.get(
                            'source_file', 'Unknown')
                        if source_file not in sources:
                            sources[source_file] = 0
                        sources[source_file] += 1

                    print(f"📚 Sources: {dict(sources)}")
                else:
                    print("📚 No source documents found")

            except Exception as e:
                print(f"❌ Error in query: {e}")

    except Exception as e:
        print(f"❌ Error creating QA chain: {e}")


def test_system_statistics():
    """Test thống kê hệ thống"""
    print("📊 System Statistics...")

    documents = get_available_documents()
    processed_count = len([d for d in documents if d['has_vector_store']])
    total_size = sum([d['size_mb'] for d in documents])

    print(f"📄 Total documents: {len(documents)}")
    print(f"✅ Processed documents: {processed_count}")
    print(f"💾 Total size: {total_size:.2f} MB")

    if processed_count > 0:
        print(
            f"📈 Processing rate: {(processed_count/len(documents)*100):.1f}%")


def main():
    """Main test function"""
    print("🚀 Starting Multi-Document RAG System Tests\n")

    try:
        # Test 1: Document Management
        documents = test_document_management()

        # Test 2: Vector Store Creation
        test_vector_store_creation()

        # Test 3: System Statistics
        test_system_statistics()

        # Test 4: Multi-Document Search
        test_combined_search()

        print("\n✅ All tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
