# RAG Система - Локальний Q&A для Документів

Локальна система Retrieval-Augmented Generation (RAG) для запитів до документів з використанням open-source LLM. Створена для швидкого прототипування та proof-of-concept розгортань.

## Огляд

Цей проєкт реалізує повний RAG pipeline, який:
- Конвертує документи (PDF, DOCX, TXT) у текст для пошуку
- Розбиває контент на семантичні chunks
- Генерує embeddings за допомогою локальних моделей
- Зберігає вектори в ChromaDB
- Відповідає на запитання використовуючи LLM через Ollama

Система працює повністю локально без зовнішніх API залежностей.

## Можливості

- **Обробка Документів**: Автоматична конвертація PDF, DOCX та TXT файлів
- **Семантичний Пошук**: Vector-based пошук з використанням sentence transformers
- **Локальний LLM**: Генерація відповідей через Ollama (llama3.2 за замовчуванням)
- **Streaming Відповіді**: Генерація відповідей в реальному часі
- **Мультимовність**: Підтримка запитів англійською, українською та російською
- **Веб-Інтерфейс**: UI на базі Gradio для швидкого тестування

## Архітектура

```
┌─────────────┐
│  Документи  │
│ (PDF/DOCX)  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│   Конвертація   │
│   (PyMuPDF)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Розбиття       │
│  (LangChain)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│   Embeddings    │◄─────┤ Запит        │
│ (all-MiniLM-L6) │      └──────────────┘
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   ChromaDB      │
│ (Vector Store)  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Пошук          │
│  Контексту      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  LLM (Ollama)   │
│  llama3.2       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Відповідь +    │
│  Джерела        │
└─────────────────┘
```

## Технологічний Стек

| Компонент | Технологія | Призначення |
|-----------|-----------|-------------|
| Парсинг Документів | PyMuPDF, python-docx | Витягування тексту з файлів |
| Обробка Тексту | LangChain | Розбиття документів з overlap |
| Embeddings | sentence-transformers | Генерація векторних представлень |
| Vector Database | ChromaDB | Зберігання та пошук embeddings |
| LLM Runtime | Ollama | Локальний inference моделей |
| Веб-Інтерфейс | Gradio | UI для швидкого прототипування |

## Вимоги

- Python 3.9+
- Ollama встановлений та запущений
- 4GB+ RAM (рекомендовано 8GB+)
- ~2GB дискового простору для моделей

## Швидкий Старт

### 1. Встановіть Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Завантажте модель
ollama pull llama3.2
```

### 2. Налаштуйте Python Середовище

```bash
# Клонуйте репозиторій
git clone <repository-url>
cd rag-python-rag

# Створіть віртуальне середовище
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Встановіть залежності
pip install -r requirements.txt
```

### 3. Запустіть Застосунок

```bash
python main.py
```

Застосунок:
1. Завантажить тестовий документ (Think Python PDF)
2. Обробить та проіндексує його (~30 секунд)
3. Запустить веб-інтерфейс на `http://localhost:7860`

### 4. Додайте Свої Документи

Помістіть PDF, DOCX або TXT файли в директорію `documents/` та перезапустіть застосунок.

## Конфігурація

Відредагуйте `config.py` для налаштування:

```python
# Модель embeddings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# LLM модель
OLLAMA_MODEL_NAME = "llama3.2"

# Розбиття тексту
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Результати пошуку
DEFAULT_N_RESULTS = 5
```

### Змінні Середовища

Скопіюйте `.env.example` в `.env` та налаштуйте:

```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Структура Проєкту

```
rag-python-rag/
├── config.py              # Конфігурація
├── document_converter.py  # PDF/DOCX в markdown
├── text_splitter.py       # Логіка розбиття
├── vector_store.py        # Інтерфейс ChromaDB
├── llm_handler.py         # Інтеграція Ollama
├── main.py                # Точка входу
├── requirements.txt       # Python залежності
├── documents/             # Вихідні документи (gitignored)
├── processed_docs/        # Конвертований markdown (gitignored)
└── chroma_db/            # Vector database (gitignored)
```

## Приклади Використання

### Python API

```python
from vector_store import retrieve_context
from llm_handler import stream_llm_answer

# Запит до документів
question = "Як працюють цикли в Python?"
context, sources = retrieve_context(question, n_results=5)

# Stream відповідь
for token in stream_llm_answer(question, context):
    print(token, end='', flush=True)
```

### Веб-Інтерфейс

1. Перейдіть на `http://localhost:7860`
2. Введіть запитання будь-якою підтримуваною мовою
3. Перегляньте відповідь з посиланнями на джерела

## Обмеження

Дивіться [LIMITATIONS.md](LIMITATIONS.md) для детальних обмежень включно з:
- Підтримкою мов embedding моделлю
- Обмеженнями форматів документів
- Вимогами до обладнання
- Прогалинами готовності до production

## Розгортання

Це **локальний застосунок**, який потребує Python backend та Ollama runtime.

Дивіться [DEPLOYMENT.md](DEPLOYMENT.md) для опцій розгортання:
- Hugging Face Spaces (рекомендовано для демо)
- Хмарні платформи (Render, Fly.io, Railway)
- Локальне використання

**Примітка**: GitHub Pages та статичний хостинг не підтримуються.

## Roadmap

- [ ] Підтримка Excel та PowerPoint файлів
- [ ] Кешування embeddings для швидшого запуску
- [ ] REST API endpoints
- [ ] Контекст розмови з кількома документами
- [ ] Витягування зображень та таблиць з PDF
- [ ] Docker контейнеризація

## Внесок

Внески вітаються. Будь ласка:
1. Зробіть fork репозиторію
2. Створіть feature branch
3. Надішліть pull request з чітким описом

## Ліцензія

MIT License - дивіться файл LICENSE для деталей.

Цей проєкт призначений для освітніх цілей та прототипування.

## Подяки

Створено з:
- [Ollama](https://ollama.ai/) - Локальний LLM runtime
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [LangChain](https://www.langchain.com/) - Обробка тексту
- [Sentence Transformers](https://www.sbert.net/) - Embeddings
- [Gradio](https://www.gradio.app/) - Веб-інтерфейс

Натхнення: [Побудова RAG Системи за Один Вечір](https://habr.com/ru/articles/955798/)

---

**Статус**: Proof of concept / Освітній проєкт  
**Підтримка**: Активна розробка  
**Python**: 3.9+
