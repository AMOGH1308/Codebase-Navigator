# AI-Powered Interactive Code Analysis and Refactoring Platform

An intelligent codebase navigator and refactoring assistant that combines static code analysis with AI-powered insights to help developers understand, analyze, and improve their Python codebases.

## 🚀 Features

- **Dynamic Project Upload**: Upload entire project folders as ZIP files for comprehensive analysis
- **Interactive File Browser**: Navigate through project structure with an intuitive web interface
- **Intelligent Code Parsing**: Leverages Tree-sitter for precise extraction of functions, classes, and dependencies
- **AI-Powered Analysis**: Integrates Google Gemini through LangChain for code explanation, refactoring, and summarization
- **Context-Aware Assistance**: Enriches AI prompts with imports, docstrings, comments, and external documentation
- **Real-Time Dependency Checking**: Validates package versions against PyPI with automated scraping
- **Conversational Memory**: Maintains context across interactions for improved continuity
- **Responsive Web Interface**: Clean, modern UI with loading indicators and error handling

## 🛠️ Tech Stack

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

## 🔧 Installation

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

4. **Install Tree-sitter Python grammar**
   ```bash
   # This may be handled automatically by the application
   # or follow Tree-sitter Python installation guide
   ```

## 🚦 Usage

1. **Start the Flask server**
   ```bash
   python server.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

3. **Upload your project**
   - Click "Choose File" and select a ZIP archive of your Python project
   - Click "Upload" to process the codebase

4. **Explore and analyze**
   - Browse files using the interactive file tree
   - Load code snippets for analysis
   - Select AI tasks: Analyze, Refactor, Explain, or Summarize
   - View dependency information and version status

## 📁 Project Structure

```
├── server.py              # Main Flask application
├── index.html            # Frontend interface
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
├── codebase/            # Uploaded project storage
├── flask_session/       # Session data storage
└── nexuscodenavigator/  # Core application modules
```

## 🎯 Key Components

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

## 🔮 Future Enhancements

- [ ] Support for additional programming languages
- [ ] Code execution in sandboxed environment
- [ ] Integration with version control systems
- [ ] Real-time collaboration features
- [ ] Advanced code metrics and visualization
- [ ] Custom AI model fine-tuning capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for advanced language model capabilities
- Tree-sitter community for robust parsing tools
- LangChain for AI orchestration framework
- Flask community for web framework support

## 📧 Contact

**Amogh** - [GitHub Profile](https://github.com/AMOGH1308)

Project Link: [https://github.com/AMOGH1308/Codebase-Navigator](https://github.com/AMOGH1308/Codebase-Navigator)

---

⭐ If you find this project helpful, please consider giving it a star!