import os
import ast
import re
import shutil
import tempfile
import zipfile
import requests
from bs4 import BeautifulSoup
from packaging import version
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session
from tree_sitter import Language, Parser
import tree_sitter_python as tspython
from langchain_core.prompts import PromptTemplate
from langchain_google_genai.llms import GoogleGenerativeAI

# Flask app setup
app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # Replace with a secure key
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)
CORS(app)

# Globals
CURRENT_PROJECT_ROOT = None
DEFAULT_PROJECT_ROOT = r'c:\Users\Admin\Downloads\Final_Run'  # Update as needed

def get_project_root():
    return CURRENT_PROJECT_ROOT if CURRENT_PROJECT_ROOT else DEFAULT_PROJECT_ROOT

# Tree-sitter parser setup
PY_LANGUAGE = Language(tspython.language())  # Adjust path if needed
parser = Parser(PY_LANGUAGE)


# LLM setup (update with your API key and model)
llm = GoogleGenerativeAI(api_key="AIzaSyDPttmV5DJMt9VSiBohBOzukoAIkTHvXuc", model="gemini-2.5-flash")
prompt_template = PromptTemplate(
    input_variables=["code", "task", "context"],
    template="""You are an expert software assistant.
Given the following code:
{code}
Task: {task}
Context:
{context}
Respond precisely:"""
)
prompt_explain = PromptTemplate(
    input_variables=["code", "context"],
    template="""You are an expert software assistant.
Explain the following code:
{code}
Context:
{context}"""
)
prompt_summarize = PromptTemplate(
    input_variables=["code", "context"],
    template="""You are an expert software assistant.
Summarize the following code:
{code}
Context:
{context}"""
)
llm_chain = prompt_template | llm
llm_chain_explain = prompt_explain | llm
llm_chain_summarize = prompt_summarize | llm

# Conversation memory management
def append_to_conversation(text):
    conv = session.get("conversation_history", [])
    conv.append(text)
    session["conversation_history"] = conv[-20:]  # Keep last 20 messages

def clear_conversation():
    session["conversation_history"] = []

# -----------------------------
# Code parsing and extraction functions (example for functions, classes)

def extract_code_element(source, element_type, name):
    tree = parser.parse(bytes(source, "utf8"))
    node_type = "function_definition" if element_type == "function" else "class_definition"
    root = tree.root_node

    def recurse(n):
        if n.type == node_type:
            for c in n.children:
                if c.type == "identifier" and c.text.decode() == name:
                    return source[n.start_byte:n.end_byte]
        for c in n.children:
            ret = recurse(c)
            if ret: return ret
        return None

    return recurse(root)

def extract_elements(source):
    tree = parser.parse(bytes(source, "utf8"))
    elements = {"functions": [], "classes": [], "imports": [], "variables": []}

    def visit(node):
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                elements["functions"].append({"name": source[name_node.start_byte:name_node.end_byte].decode()})
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                elements["classes"].append({"name": source[name_node.start_byte:name_node.end_byte].decode()})
        elif node.type in ("import_statement", "import_from_statement"):
            elements["imports"].append(source[node.start_byte:node.end_byte].decode())
        elif node.type == "assignment":
            target = node.child_by_field_name("left")
            if target and target.type == "identifier":
                elements["variables"].append({"name": source[target.start_byte:target.end_byte].decode()})
        for c in node.children:
            visit(c)

    visit(tree.root_node)
    return elements

# Helper: Docstrings and comments extraction
def extract_docstrings_and_comments(code):
    docstrings, comments = [], []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                doc = ast.get_docstring(node)
                if doc:
                    docstrings.append(f"{node.__class__.__name__} {node.name} docstring:\n{doc}")
        for line in code.splitlines():
            line = line.strip()
            if line.startswith("#"):
                comments.append(line)
    except:
        pass
    return {"docstrings": docstrings, "comments": comments}

# Context builder (includes imports and external info scraping)
def build_context(code, external_texts=None):
    imports = [l.strip() for l in code.splitlines() if l.strip().startswith(("import ","from "))]
    packages = set()
    for imp in imports:
        parts = imp.split()
        if parts[0] == "import":
            for pkg in parts[1].split(","):
                packages.add(pkg.strip())
        elif parts[0] == "from":
            packages.add(parts[1])
    context_parts = []
    if imports:
        context_parts.append("Imports:\n" + "\n".join(imports))
    doc_comments = extract_docstrings_and_comments(code)
    if doc_comments["docstrings"]:
        context_parts.append("Docstrings:\n" + "\n\n".join(doc_comments["docstrings"]))
    if doc_comments["comments"]:
        context_parts.append("Comments:\n" + "\n".join(doc_comments["comments"]))
    for pkg in list(packages)[:3]:
        context_parts.append(f"Package Info: {pkg}")
        context_parts.append(f"Latest PyPI Versions: {', '.join(scrape_pypi_versions(pkg))}")
        context_parts.append(f"Python Docs:\n{scrape_python_docs(pkg)}")
        context_parts.append(f"Stack Overflow Snippet:\n{scrape_stackoverflow(pkg)}")
    if external_texts:
        context_parts.append("Additional Context:\n" + "\n".join(external_texts))
    return "\n\n".join(context_parts) or "No relevant context found."

# Scraper functions for packages (PyPI, Docs, StackOverflow)
def scrape_pypi_versions(package):
    try:
        url = f"https://pypi.org/project/{package}/#history"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        versions = [v.text.strip() for v in soup.select(".release__version")]
        return versions[:5]
    except:
        return []

def scrape_python_docs(topic):
    try:
        url = f"https://docs.python.org/3/search.html?q={topic}&check_keywords=yes&area=default"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, "html.parser")
        results = []
        for item in soup.select(".search li")[:3]:
            title = item.find("a").text.strip()
            snippet = item.find("p").text.strip() if item.find("p") else ""
            results.append(f"{title}: {snippet}")
        return "\n".join(results)
    except:
        return ""

def scrape_stackoverflow(query):
    try:
        url = f"https://stackoverflow.com/search?q={query}"
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.content, "html.parser")
        first = soup.select_one(".question-summary .result-link span")
        return first.text.strip() if first else ""
    except:
        return ""

# ---------------------------
# Project upload endpoints

def remove_old_project():
    global CURRENT_PROJECT_ROOT
    if CURRENT_PROJECT_ROOT and os.path.exists(CURRENT_PROJECT_ROOT):
        try:
            shutil.rmtree(CURRENT_PROJECT_ROOT)
        except:
            pass


def parse_requirements(requirements_text):
    """
    Parse requirements.txt content to extract package names and versions.
    """
    packages = []
    for line in requirements_text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('-'):
            continue
        # Supports simple package==version, or package>=version etc.
        match = re.match(r'^([a-zA-Z0-9_\-\.]+)([<>=!~]=?)(.+)$', line)
        if match:
            pkg_name, operator, ver = match.groups()
            packages.append({'name': pkg_name, 'operator': operator, 'version': ver})
        else:
            # No version specified
            if re.match(r'^[a-zA-Z0-9_\-\.]+$', line):
                packages.append({'name': line, 'operator': None, 'version': None})
    return packages

def check_updates(packages_list):
    """
    For each package in packages_list, check PyPI for latest version.
    """
    results = []
    for pkg in packages_list:
        name = pkg['name']
        local_ver = pkg.get('version')
        try:
            resp = requests.get(f'https://pypi.org/pypi/{name}/json', timeout=5)
            if resp.status_code != 200:
                results.append({'name': name, 'current_version': local_ver, 'latest_version': None,
                                'status': 'Package not found', 'needs_update': False})
                continue
            data = resp.json()
            latest_ver = data['info'].get('version')
            if local_ver:
                # Clean versions for comparison
                local_ver_clean = re.sub(r'[^\d\.]', '', local_ver)
                latest_ver_clean = re.sub(r'[^\d\.]', '', latest_ver)
                if version.parse(latest_ver_clean) > version.parse(local_ver_clean):
                    status = f'Update available: {local_ver} -> {latest_ver}'
                    needs_update = True
                else:
                    status = 'Up to date'
                    needs_update = False
            else:
                status = f'Latest version: {latest_ver}'
                needs_update = True
            results.append({'name': name, 'current_version': local_ver, 'latest_version': latest_ver,
                            'status': status, 'needs_update': needs_update})
        except Exception as e:
            results.append({'name': name, 'current_version': local_ver, 'latest_version': None,
                            'status': 'Error checking version', 'needs_update': False})
    return results

@app.route("/upload-project", methods=["POST"])
def upload_project():
    global CURRENT_PROJECT_ROOT
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.endswith(".zip"):
        return jsonify({"error": "Only .zip files allowed"}), 400
    remove_old_project()
    CURRENT_PROJECT_ROOT = tempfile.mkdtemp(prefix="proj_")
    zip_path = os.path.join(CURRENT_PROJECT_ROOT, "upload.zip")
    file.save(zip_path)
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(CURRENT_PROJECT_ROOT)
        os.remove(zip_path)
        clear_conversation()
        return jsonify({"message": "Project uploaded and extracted."}), 200
    except Exception as e:
        shutil.rmtree(CURRENT_PROJECT_ROOT)
        CURRENT_PROJECT_ROOT = None
        return jsonify({"error": f"Failed to extract: {str(e)}"}), 500

@app.route("/clear-project", methods=["POST"])
def clear_project():
    global CURRENT_PROJECT_ROOT
    remove_old_project()
    CURRENT_PROJECT_ROOT = None
    clear_conversation()
    return jsonify({"message": "Project cleared and conversation reset."})

# ---------------------
# File browsing

@app.route("/files", methods=["GET"])
def list_files():
    rel_path = request.args.get("path", "")
    root = get_project_root()
    abs_path = os.path.abspath(os.path.join(root, rel_path))
    if not abs_path.startswith(root):
        return jsonify({"error": "Access denied"}), 403
    if not os.path.exists(abs_path):
        return jsonify({"error": "Not found"}), 404
    if os.path.isfile(abs_path):
        return jsonify({"error": "Not a folder"}), 400
    items = []
    for entry in os.listdir(abs_path):
        full = os.path.join(abs_path, entry)
        items.append({"name": entry, "is_dir": os.path.isdir(full)})
    return jsonify({"path": rel_path, "items": items})

@app.route("/file-content", methods=["GET"])
def file_content():
    rel_path = request.args.get("path", "")
    root = get_project_root()
    abs_path = os.path.abspath(os.path.join(root, rel_path))
    if not abs_path.startswith(root):
        return jsonify({"error": "Access denied"}), 403
    if not os.path.isfile(abs_path):
        return jsonify({"error": "Not a file"}), 404
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"path": rel_path, "content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# Snippet extraction and listing

@app.route("/extract-snippet", methods=["POST"])
def extract_snippet():
    data = request.json
    file_path = data.get("file_path")
    element_type = data.get("type")
    element_name = data.get("name")
    if not file_path or not element_type or not element_name:
        return jsonify({"error": "Missing parameters"}), 400
    root = get_project_root()
    abs_path = os.path.abspath(os.path.join(root, file_path))
    if not abs_path.startswith(root) or not os.path.isfile(abs_path):
        return jsonify({"error": "Invalid file path"}), 400
    with open(abs_path, "r", encoding="utf-8") as f:
        source = f.read()
    snippet = extract_code_element(source, element_type, element_name)
    if snippet is None:
        return jsonify({"error": f"{element_type} {element_name} not found"}), 404
    return jsonify({"snippet": snippet})

@app.route("/list-elements", methods=["POST"])
def list_elements():
    data = request.json
    file_path = data.get("file_path")
    if not file_path:
        return jsonify({"error": "Missing file_path"}), 400
    root = get_project_root()
    abs_path = os.path.abspath(os.path.join(root, file_path))
    if not abs_path.startswith(root) or not os.path.isfile(abs_path):
        return jsonify({"error": "Invalid file path"}), 400
    with open(abs_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = parser.parse(bytes(source, "utf-8"))
    elements = extract_elements(source.encode("utf-8"))
    return jsonify(elements)

# ---------------------
# File upload text extraction

@app.route("/extract-text-file", methods=["POST"])
def extract_text_file():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.lower().endswith((".txt",".md",".csv",".log")):
        return jsonify({"error": "Unsupported file type"}), 400
    try:
        content = file.read().decode("utf-8")
        if not content.strip():
            return jsonify({"error": "Empty file"}), 400
        return jsonify({"extracted_text": content})
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

# ---------------------
# Dependency check

@app.route("/dependency-check", methods=["POST"])
def dependency_check():
    data = request.json
    req_content = data.get("requirements")
    req_file_path = data.get("file_path")
    root = get_project_root()
    if req_file_path:
        abs_path = os.path.abspath(os.path.join(root, req_file_path))
        if not abs_path.startswith(root) or not os.path.isfile(abs_path):
            return jsonify({"error": "Invalid requirements file path"}),400
        with open(abs_path, "r", encoding="utf-8") as f:
            req_content = f.read()
    if not req_content:
        return jsonify({"error": "No requirements content"}), 400
    packages = parse_requirements(req_content)
    if not packages:
        return jsonify({"error": "No packages found"}), 400
    result = check_updates(packages)
    total = len(result)
    updates = sum(1 for p in result if p["needs_update"])
    return jsonify({
        "message": "Dependency check completed",
        "summary": {"total_packages": total, "packages_to_update": updates, "up_to_date": total - updates},
        "packages": result
    })

# ---------------------
# AI Task routes

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    code = data.get("code")
    file_path = data.get("file_path")
    external_texts = data.get("external_texts")
    conv_mem = data.get("conversation_memory")
    root = get_project_root()
    if file_path and not code:
        abs_path = os.path.abspath(os.path.join(root, file_path))
        if not abs_path.startswith(root) or not os.path.isfile(abs_path):
            return jsonify({"error": "Invalid file path"}),400
        with open(abs_path, "r", encoding="utf-8") as f:
            code = f.read()
    if not code:
        return jsonify({"error": "No code provided"}),400
    tree = parser.parse(bytes(code, "utf-8"))
    elements = extract_elements(code.encode("utf-8"))
    if conv_mem:
        append_to_conversation(conv_mem)
    return jsonify({"message": "Analysis complete","code_elements": elements})

@app.route("/refactor", methods=["POST"])
def refactor():
    data = request.json
    code = data.get("code")
    task_ = data.get("task", "refactor")
    file_path = data.get("file_path")
    external_texts = data.get("external_texts")
    conv_mem = data.get("conversation_memory")
    root = get_project_root()
    if file_path and not code:
        abs_path = os.path.abspath(os.path.join(root, file_path))
        if not abs_path.startswith(root) or not os.path.isfile(abs_path):
            return jsonify({"error": "Invalid file path"}),400
        with open(abs_path, "r", encoding="utf-8") as f:
            code = f.read()
    if not code:
        return jsonify({"error": "No code"}),400
    context = build_context(code, external_texts)
    if conv_mem:
        context = f"{conv_mem}\n\n{context}"
    try:
        result = llm_chain.invoke({"code": code, "task": task_, "context": context})
        append_to_conversation(f"User task: {task_}, code len: {len(code)}")
        return jsonify({"message": "Success", "result": result, "used_context": context})
    except Exception as e:
        return jsonify({"error": f"LLM Failure: {str(e)}"}),500

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    code = data.get("code")
    file_path = data.get("file_path")
    external_texts = data.get("external_texts")
    conv_mem = data.get("conversation_memory")
    root = get_project_root()
    if file_path and not code:
        abs_path = os.path.abspath(os.path.join(root, file_path))
        if not abs_path.startswith(root) or not os.path.isfile(abs_path):
            return jsonify({"error": "Invalid file path"}),400
        with open(abs_path, "r", encoding="utf-8") as f:
            code = f.read()
    if not code:
        return jsonify({"error": "No code"}),400
    context = build_context(code, external_texts)
    if conv_mem:
        context = f"{conv_mem}\n\n{context}"
    try:
        result = llm_chain_summarize.invoke({"code": code, "context": context})
        append_to_conversation(f"User requested summary, code len: {len(code)}")
        return jsonify({"message": "Success", "summary": result, "used_context": context})
    except Exception as e:
        return jsonify({"error": f"LLM Failure: {str(e)}"}),500

@app.route("/explain", methods=["POST"])
def explain():
    data = request.json
    code = data.get("code")
    file_path = data.get("file_path")
    external_texts = data.get("external_texts")
    conv_mem = data.get("conversation_memory")
    root = get_project_root()
    if file_path and not code:
        abs_path = os.path.abspath(os.path.join(root, file_path))
        if not abs_path.startswith(root) or not os.path.isfile(abs_path):
            return jsonify({"error": "Invalid file path"}),400
        with open(abs_path, "r", encoding="utf-8") as f:
            code = f.read()
    if not code:
        return jsonify({"error": "No code"}),400
    context = build_context(code, external_texts)
    if conv_mem:
        context = f"{conv_mem}\n\n{context}"
    try:
        result = llm_chain_explain.invoke({"code": code, "context": context})
        append_to_conversation(f"User requested explanation, code len: {len(code)}")
        return jsonify({"message": "Success", "explanation": result, "used_context": context})
    except Exception as e:
        return jsonify({"error": f"LLM Failure: {str(e)}"}),500

@app.route("/clear-memory", methods=["POST"])
def clear_memory():
    clear_conversation()
    return jsonify({"message": "Conversation memory cleared"})

if __name__ == "__main__":
    app.run(debug=True)
