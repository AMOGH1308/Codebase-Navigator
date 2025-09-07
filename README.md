# Codebase Navigator and Refactoring Assistant with Dynamic Web Integration

Developed an AI-powered code assistant that enables dynamic project upload, interactive file browsing, and precise
Python code snippet extraction using Tree-sitter. Integrated LangChain with Google Generative AI for context-aware code
refactoring, summarization, and explanation. Implemented real-time dependency version checking with PyPI integration and
conversational memory for continuity. Built a responsive frontend offering seamless user interaction and efficient developer
workflows.

## Features

- **Dynamic Project Upload**: Upload entire project folders as ZIP files for comprehensive analysis
- **Interactive File Browser**: Navigate through project structure with an intuitive web interface
- **Intelligent Code Parsing**: Leverages Tree-sitter for precise extraction of functions, classes, and dependencies
- **AI-Powered Analysis**: Integrates Google Gemini through LangChain for code explanation, refactoring, and summarization
- **Context-Aware Assistance**: Enriches AI prompts with imports, docstrings, comments, and external documentation
- **Real-Time Dependency Checking**: Validates package versions against PyPI with automated scraping
- **Conversational Memory**: Maintains context across interactions for improved continuity
- **Responsive Web Interface**: Clean, modern UI with loading indicators and error handling

## Tech Stack

**Backend:**
- Python, Flask, Flask-Session, Flask-CORS
- LangChain for LLM orchestration
- Google Generative AI (Gemini)
- Tree-sitter for syntax parsing
- Web scraping (BeautifulSoup, Requests)

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- Fetch API for asynchronous operations
- Responsive design with dynamic DOM manipulation

**APIs & Libraries:**
- Google Gemini API for AI capabilities
- PyPI JSON API for package information
- External documentation scraping (Python docs, StackOverflow)

## 📋 Prerequisites

- Python 3.8+
- Google API key for Gemini
- Modern web browser

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AMOGH1308/Codebase-Navigator.git
   cd Codebase-Navigator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```



## Usage

1. **Start the Flask server**
   ```cmd
   python server.py
   ```
   - It will by default run on port no 8000
     
2. **Run the Index.html on port 8000"
   ```cmd
   python -m http.server 8000
   ```
   
3. **Upload your project**
   - Click "Choose File" and select a ZIP archive of your Python project
   - Click "Upload" to process the codebase

4. **Explore and analyze**
   - Browse files using the interactive file tree
   - Load code snippets for analysis
   - Select AI tasks: Analyze, Refactor, Explain, or Summarize
   - View dependency information and version status

## Project Structure

```
├── server.py              # Main Flask application
├── index.html            # Frontend interface
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
```

## Key Components

**Backend Architecture:**
- **Project Handler**: Manages ZIP upload, extraction, and file organization
- **Code Parser**: Uses Tree-sitter for AST-based code analysis
- **AI Interface**: LangChain integration with contextual prompt engineering
- **Dependency Analyzer**: Real-time package version checking and validation
- **Session Manager**: Maintains user context and conversation history

**Frontend Features:**
- **File Explorer**: Interactive project navigation with expand/collapse
- **Code Viewer**: Syntax-highlighted code display with snippet selection
- **AI Interaction Panel**: Multi-task selection with real-time response streaming
- **Dependency Dashboard**: Visual package status and version information

## Future Enhancements

- [ ] Support for additional programming languages
- [ ] Vector Search & Retrieval-Augmented Generation (RAG) to improve context awareness through Document embeddings and similarity            search
- [ ] Automatically apply AI-generated refactoring changes directly to project files with preview and undo options.
- [ ] dependency compatibility checker that automatically fetches latest package versions and iteratively resolves conflicts by               downgrading incompatible packages to maintain a stable environment.


## Acknowledgments

- Google Gemini AI for advanced language model capabilities
- Tree-sitter community for robust parsing tools
- LangChain for AI orchestration framework
- Flask community for web framework support
  

## Contact

**Amogh** - [GitHub Profile](https://github.com/AMOGH1308)

Project Link: [https://github.com/AMOGH1308/Codebase-Navigator](https://github.com/AMOGH1308/Codebase-Navigator)

---

⭐ If you find this project helpful, please consider giving it a star!
