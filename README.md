# 🧠 C Code Compiler & Syntax Fixer (Django + CodeT5 + LLVM)

This project is a web-based C programming environment built with Django that allows users to write, correct, compile, and execute C code from the browser. It integrates a custom LLVM-based modular compilation pipeline and a fine-tuned [CodeT5](https://huggingface.co/Salesforce/codet5-small) transformer model for intelligent syntax error correction.

---

## 🌟 Features

- 🧾 **Write & Run C Code** in a web interface  
- 🧠 **Syntax Error Correction** using fine-tuned CodeT5 model  
- ⚙️ **Custom LLVM Compilation** with per-function partitioning and caching  
- ⚡ **Parallel Compilation** using multiprocessing for faster builds  
- 🖥️ **Live Output** of compiled code directly in the browser  

---

## 📌 Project Workflow

1. **Dataset Creation**: A JSON file with buggy and fixed C code examples is created.
2. **Model Training**: The dataset is used to fine-tune CodeT5 on Google Colab using Hugging Face Transformers.
3. **LLVM Pipeline**: A custom script `compile.py` compiles `input.c` using Clang to `.ll`, partitions functions, and builds the final binary with caching.
4. **Web Integration**: A Django app allows users to submit code, correct it via CodeT5, or compile and run using the LLVM backend.

---

## 🏗️ Technologies Used

- **Programming Language**: Python, C  
- **Web Framework**: Django  
- **Compiler Toolchain**: Clang, LLVM  
- **Model Framework**: PyTorch, Hugging Face Transformers  
- **Frontend**: HTML, CSS (Django templates)  
- **Syntax Highlighting**: Python `difflib`  
- **Environment**: PyCharm on Linux  

---

## 🚀 Getting Started

### ✅ Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
