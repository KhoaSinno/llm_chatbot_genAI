#!/bin/bash

echo "🚀 Thiết lập Chatbot RAG System"
echo "================================"

# Kiểm tra Python
if ! command -v python &> /dev/null; then
    echo "❌ Python không được cài đặt. Vui lòng cài đặt Python 3.8+"
    exit 1
fi

echo "✅ Python đã được cài đặt"

# Tạo virtual environment
echo "📦 Tạo virtual environment..."
python -m venv venv

# Kích hoạt virtual environment
echo "🔧 Kích hoạt virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Cài đặt dependencies
echo "📚 Cài đặt dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Thiết lập hoàn tất!"
echo ""
echo "📋 Hướng dẫn sử dụng:"
echo "1. Đặt file PDF vào thư mục và đặt tên là 'doan3.pdf'"
echo "2. (Tùy chọn) Thêm OpenAI API key vào file config.env"
echo "3. Chạy: streamlit run app.py"
echo ""
echo "💡 Mẹo: Hệ thống sẽ tự động sử dụng Hugging Face (miễn phí) nếu không có OpenAI key"
