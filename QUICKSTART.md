# 🚀 RAG System Quick Start

This quick guide will help you launch the RAG system in 5 minutes!

## Prerequisites

✅ Python 3.9+  
✅ Ollama installed and running  
✅ llama3.2 model downloaded

## Step 1: Check Ollama

```bash
# Check that Ollama is installed
ollama --version

# Check available models
ollama list

# If llama3.2 is not in the list, download it
ollama pull llama3.2
```

## Step 2: Activate Virtual Environment

```bash
cd /Users/v.hirenko/Desktop/DevHubVault/my-ai-projects/rag-python-rag
source venv/bin/activate
```

## Step 3: Run the Application

```bash
python main.py
```

## What Will Happen?

1. ⬇️ Test document will be downloaded (Think Python PDF)
2. 📄 Document will be converted to markdown
3. ✂️ Text will be split into 847 chunks
4. 🔢 Embeddings will be generated for each chunk
5. 💾 Data will be saved to ChromaDB
6. 🌐 Web interface will open at http://localhost:7860

## Usage Example

After launching, open your browser and go to http://localhost:7860

**Try these questions:**

**In English:**

- "How do if-else statements work in Python?"
- "What are the different types of loops in Python?"
- "How do you handle errors in Python?"

**In other languages:**

- "Як працюють умовні оператори if-else в Python?" (Ukrainian)
- "Какие типы циклов есть в Python?" (Russian)
- "Як обробляти помилки в Python?" (Ukrainian)

## Execution Time

⏱️ **First run:** ~1-2 minutes  
⏱️ **Subsequent runs:** ~5-10 seconds  
⏱️ **Answer to question:** ~5-15 seconds

## Troubleshooting

### ❌ "Model llama3.2 not found"

```bash
ollama pull llama3.2
```

### ❌ "Connection refused to localhost:11434"

```bash
# Make sure Ollama is running
ollama serve
```

### ❌ "No module named 'fitz'"

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

✅ Done? Great! Now try:

1. **Add your own documents:**

   - Place PDF/DOCX files in the `documents/` folder
   - Restart the application

2. **Configure parameters:**

   - Open `config.py`
   - Change model, chunk size, and other parameters

3. **Use programmatically:**

   ```python
   from vector_store import retrieve_context
   from llm_handler import generate_answer

   question = "Your question here"
   context, sources = retrieve_context(question)
   answer = generate_answer(question, context)
   print(answer)
   ```

## Useful Commands

```bash
# Check component status
python vector_store.py      # Vector DB statistics
python llm_handler.py        # LLM test
python document_converter.py # Document conversion

# Clear and reindex
python -c "
from vector_store import VectorStore
vs = VectorStore()
vs.clear_collection()
"

# Then restart main.py
python main.py
```

## Need Help?

📖 Full documentation: `README.md`  
🐛 Found a bug? Create an Issue  
💡 Have ideas? Pull Requests are welcome!

---

**Enjoy using the system! 🎉**
