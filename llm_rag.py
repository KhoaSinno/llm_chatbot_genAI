import os
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("⚠️ langchain-google-genai not installed. Install with: pip install langchain-google-genai")
    ChatGoogleGenerativeAI = None

from pre_doc import vector_store

# Load environment variables
load_dotenv('config.env')


def create_qa_chain(model_type="openai"):
    """
    Tạo QA chain với các API model khác nhau
    model_type: "openai", "gemini"
    """

    if model_type == "openai":
        # Sử dụng OpenAI API
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            raise ValueError(
                "Vui lòng cấu hình OPENAI_API_KEY trong file config.env")

        llm = OpenAI(
            temperature=0.7,
            openai_api_key=api_key,
            max_tokens=500
        )
        print("🤖 Sử dụng OpenAI GPT API")

    elif model_type == "gemini":
        # Sử dụng Gemini API
        if ChatGoogleGenerativeAI is None:
            raise ImportError(
                "Cần cài đặt: pip install langchain-google-genai")

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            raise ValueError(
                "Vui lòng cấu hình GEMINI_API_KEY trong file config.env")

        # Thử các model Gemini theo thứ tự ưu tiên
        gemini_models = [
            "gemini-2.0-flash-exp",  # Model mới nhất
            "gemini-1.5-flash",      # Backup option
            "gemini-1.5-pro",        # Fallback
            "gemini-pro"             # Legacy (có thể không hoạt động)
        ]

        llm = None
        last_error = None

        for model_name in gemini_models:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.7,
                    convert_system_message_to_human=True
                )
                print(f"🤖 Sử dụng Google Gemini API: {model_name}")
                break
            except Exception as e:
                last_error = e
                print(f"⚠️ Model {model_name} không khả dụng: {e}")
                continue

        if llm is None:
            raise ValueError(
                f"❌ Không thể khởi tạo bất kỳ model Gemini nào. Lỗi cuối: {last_error}")

    else:
        raise ValueError(
            f"Model type '{model_type}' không được hỗ trợ. Chọn: 'openai' hoặc 'gemini'")

    # Tạo QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 10}),
        return_source_documents=True
    )

    return qa_chain


def initialize_default_chain():
    """Khởi tạo chain mặc định, thử OpenAI trước, nếu không có thì Gemini"""

    # Thử Gemini trước (vì có API key và free)
    try:
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            return create_qa_chain("gemini")
    except Exception as e:
        print(f"⚠️ Gemini không khả dụng: {e}")

    # Thử OpenAI
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != 'your_openai_api_key_here':
            return create_qa_chain("openai")
    except Exception as e:
        print(f"⚠️ OpenAI không khả dụng: {e}")

    raise ValueError(
        "❌ Không có API key hợp lệ. Vui lòng cấu hình OPENAI_API_KEY hoặc GEMINI_API_KEY")


# Khởi tạo qa_chain mặc định
try:
    qa_chain = initialize_default_chain()
    print("✅ Đã khởi tạo chatbot thành công")
except Exception as e:
    print(f"❌ Lỗi khởi tạo: {e}")
    qa_chain = None
