#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test after cache rebuild
"""


def test_system():
    """Test hệ thống sau khi rebuild cache"""

    print("🚀 TESTING SYSTEM AFTER CACHE REBUILD")
    print("=" * 50)

    # Test 1: Vector store
    try:
        from pre_doc import vector_store
        print("✅ Vector store loaded successfully")
        print(f"   Type: {type(vector_store)}")
    except Exception as e:
        print(f"❌ Vector store error: {e}")
        return

    # Test 2: QA Chain
    try:
        from llm_rag import qa_chain
        print("✅ QA chain loaded successfully")
    except Exception as e:
        print(f"❌ QA chain error: {e}")
        return

    # Test 3: Basic retrieval
    try:
        query = "Safe News"
        retriever = vector_store.as_retriever(search_kwargs={"k": 2})
        docs = retriever.invoke(query)
        print(f"✅ Retrieval test: Found {len(docs)} docs for '{query}'")

        if docs:
            content = docs[0].page_content[:100]
            print(f"   Sample: {content}...")
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return

    # Test 4: Basic QA
    try:
        test_query = "Safe News là gì?"
        result = qa_chain.invoke({"query": test_query})
        answer = result.get('result', 'No answer')
        print(f"✅ QA test successful")
        print(f"   Query: {test_query}")
        print(f"   Answer: {answer[:100]}...")
    except Exception as e:
        print(f"❌ QA error: {e}")
        return

    print("\n🎉 ALL TESTS PASSED - SYSTEM READY!")


if __name__ == "__main__":
    test_system()
