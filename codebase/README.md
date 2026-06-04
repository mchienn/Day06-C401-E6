# Codebase — Smart Food Finder Chatbot 🍜

## Mô tả

AI Chatbot gợi ý món ăn dựa trên mô tả tự nhiên của người dùng. Hệ thống sử dụng LLM qua OpenRouter để hiểu intent, sau đó gọi tool lọc dataset nội bộ (hard filter khoảng cách ≤3km + dị ứng + ngân sách) và trả về top 3 món phù hợp nhất.

## Cách chạy prototype

### 1. Cài đặt

```bash
cd codebase
pip install -r requirements.txt
```

### 2. Cấu hình API key

Copy `.env.example` thành `.env` và điền API key:

```bash
cp .env.example .env
# Điền OPENROUTER_API_KEY vào file .env
```

### 3. Chạy chatbot (CLI)

```bash
python chat.py --provider openrouter --version v0
```

### 4. Chạy chatbot (Streamlit Web UI)

```bash
streamlit run app.py
```

## Công cụ và API đã dùng

| Công cụ | Mục đích |
|---------|----------|
| **OpenRouter API** | LLM để hiểu intent người dùng, gọi tool, sinh câu trả lời |
| **Python** | Ngôn ngữ lập trình chính |
| **Streamlit** | Giao diện web chatbot |
| **PyYAML** | Đọc khai báo tools |

## Kiến trúc

```
codebase/
├── app.py              ← Streamlit chatbot UI
├── chat.py             ← CLI chatbot
├── agent.py            ← Agent core (model + tool loop)
├── env_loader.py       ← Load .env
├── versioning.py       ← Artifact versioning
├── artifacts/
│   ├── system_prompt.md ← System prompt cho AI
│   └── tools.yaml       ← Khai báo tools cho model
├── data/
│   └── dataset_food.json ← Dataset 15 món ăn
├── providers/           ← Adapter cho các LLM providers
└── tools/
    ├── clarify/         ← Tool hỏi lại user
    └── food_recommendation/ ← Tool lọc & gợi ý món ăn
```

## Phân công code

| Thành viên | Phần phụ trách |
|-----------|---------------|
| Nguyễn Thái Học | Research / evidence |
| Nguyễn Quang Minh | SPEC sản phẩm |
| Phạm Đức Liêm | Dataset + prototype |
| Nguyễn Tuấn Dũng | Prompt flow + logic |
| Nguyễn Đình Tiến Mạnh | Test / failure path |
| Nguyễn Minh Chiến | Demo script / repo |
