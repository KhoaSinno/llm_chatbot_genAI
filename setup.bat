@echo off
echo 🚀 Thiết lập Chatbot RAG System
echo ================================

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được cài đặt. Vui lòng cài đặt Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python đã được cài đặt

REM Tạo virtual environment
echo 📦 Tạo virtual environment...
python -m venv venv

REM Kích hoạt virtual environment
echo 🔧 Kích hoạt virtual environment...
call venv\Scripts\activate.bat

REM Cài đặt dependencies
echo 📚 Cài đặt dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Thiết lập hoàn tất!
echo.
echo 📋 Hướng dẫn sử dụng:
echo 1. Đặt file PDF vào thư mục và đặt tên là 'doan3.pdf'
echo 2. (Tùy chọn) Thêm OpenAI API key vào file config.env
echo 3. Chạy: streamlit run app.py
echo.
echo 💡 Mẹo: Hệ thống sẽ tự động sử dụng Hugging Face (miễn phí) nếu không có OpenAI key

pause
