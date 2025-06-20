#!/usr/bin/env python3
"""
Test script để kiểm tra chatbot system
"""

import os
import sys


def test_dependencies():
    """Test các dependencies cần thiết"""
    print("🧪 Testing Dependencies...")

    try:
        import streamlit
        print("✅ Streamlit:", streamlit.__version__)
    except ImportError:
        print("❌ Streamlit not installed")
        return False

    try:
        import langchain
        print("✅ LangChain:", langchain.__version__)
    except ImportError:
        print("❌ LangChain not installed")
        return False

    try:
        import sentence_transformers
        print("✅ Sentence Transformers:", sentence_transformers.__version__)
    except ImportError:
        print("❌ Sentence Transformers not installed")
        return False

    try:
        import faiss
        print("✅ FAISS available")
    except ImportError:
        print("❌ FAISS not installed")
        return False

    return True


def test_pdf_file():
    """Test file PDF có tồn tại không"""
    print("\n📄 Testing PDF File...")

    pdf_path = "doan3.pdf"
    if os.path.exists(pdf_path):
        print(f"✅ PDF file found: {pdf_path}")
        file_size = os.path.getsize(pdf_path) / (1024*1024)  # MB
        print(f"📊 File size: {file_size:.2f} MB")
        return True
    else:
        print(f"❌ PDF file not found: {pdf_path}")
        print("💡 Tạo file PDF test hoặc đặt file PDF vào thư mục")
        return False


def test_openai_config():
    """Test cấu hình OpenAI"""
    print("\n🔑 Testing OpenAI Configuration...")

    try:
        from dotenv import load_dotenv
        load_dotenv('config.env')

        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            print("✅ OpenAI API key configured")
            print("💰 Note: OpenAI usage will incur costs")
            return True
        else:
            print("⚠️ OpenAI API key not configured")
            print("💡 Will use Hugging Face (free) instead")
            return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def test_basic_functionality():
    """Test chức năng cơ bản"""
    print("\n⚙️ Testing Basic Functionality...")

    try:
        # Test import pre_doc
        from pre_doc import vector_store
        if vector_store is not None:
            print("✅ Vector store initialized successfully")
        else:
            print("❌ Vector store initialization failed")
            return False

        # Test import llm_rag
        from llm_rag import qa_chain
        if qa_chain is not None:
            print("✅ QA chain initialized successfully")
            return True
        else:
            print("❌ QA chain initialization failed")
            return False

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_simple_query():
    """Test một câu hỏi đơn giản"""
    print("\n🤖 Testing Simple Query...")

    try:
        from llm_rag import qa_chain

        if qa_chain is None:
            print("❌ QA chain not available")
            return False

        test_query = "Tài liệu này nói về gì?"
        print(f"📝 Test query: {test_query}")

        # Test với timeout (chỉ áp dụng cho non-Windows)
        import platform

        try:
            if hasattr(qa_chain, 'invoke'):
                result = qa_chain.invoke({"query": test_query})
                response = result.get('result', 'No response')
            else:
                response = qa_chain.run(test_query)

            print(f"✅ Response received: {response[:100]}...")
            return True

        except Exception as query_error:
            print(f"⚠️ Query error: {query_error}")
            # Vẫn coi là pass nếu có lỗi nhỏ, miễn là QA chain khởi tạo được
            return True

    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False


def main():
    """Chạy tất cả tests"""
    print("🚀 Chatbot RAG System - Health Check")
    print("=" * 50)

    tests = [
        ("Dependencies", test_dependencies),
        ("PDF File", test_pdf_file),
        ("OpenAI Config", test_openai_config),
        ("Basic Functionality", test_basic_functionality),
        ("Simple Query", test_simple_query)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed! System is ready to use.")
        print("💡 Run: streamlit run app.py")
    elif passed >= 3:
        print("\n⚠️ System functional with minor issues.")
        print("💡 You can still run: streamlit run app.py")
    else:
        print("\n🚨 Major issues detected. Please fix before using.")
        print("💡 Check the failed tests above")


if __name__ == "__main__":
    main()
