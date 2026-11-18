import ast
import streamlit as st

# -----------------------------------------------------------------------------
# 🔑 PUT YOUR API KEYS HERE (For OpenAI and Gemini)
# -----------------------------------------------------------------------------
# For Ollama, you do NOT need an API key.
OPENAI_API_KEY = "sk-proj-..." # <--- Paste your OpenAI key here
GEMINI_API_KEY = "AQ..."       # <--- Paste your Gemini key here

# -----------------------------------------------------------------------------
# 1. AST STATIC ANALYSIS MODULE (Deterministic Checks)
# -----------------------------------------------------------------------------
class CodeQualityVisitor(ast.NodeVisitor):
    """Traverses the AST to find common code-quality issues."""
    def __init__(self):
        self.issues = []
        self.imports = set()
        self.functions = set()
        self.calls = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.functions.add(node.name)
        if not ast.get_docstring(node):
            self.issues.append({
                "line": node.lineno,
                "severity": "INFO",
                "message": f"Function '{node.name}' is missing a docstring.",
                "type": "Best Practice"
            })
        if len(list(ast.walk(node))) > 100:
            self.issues.append({
                "line": node.lineno,
                "severity": "WARNING",
                "message": f"Function '{node.name}' is very large. Consider refactoring.",
                "type": "Complexity"
            })
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        self.generic_visit(node)

    def report(self):
        for imp in self.imports:
            if imp not in self.calls and imp not in self.functions:
                self.issues.append({
                    "line": 0,
                    "severity": "INFO",
                    "message": f"Import '{imp}' may be unused.",
                    "type": "Clean Code"
                })
        return self.issues

def run_static_analysis(code: str):
    """Parses code and runs the AST visitor."""
    try:
        tree = ast.parse(code)
        visitor = CodeQualityVisitor()
        visitor.visit(tree)
        return visitor.report()
    except SyntaxError as e:
        return [{
            "line": e.lineno or 0,
            "severity": "CRITICAL",
            "message": f"Syntax Error: {e.msg}",
            "type": "Error"
        }]

# -----------------------------------------------------------------------------
# 2. LLM INTEGRATION MODULE (Semantic Analysis)
# -----------------------------------------------------------------------------
def get_ai_review(code, provider, model):
    """Sends the code to the selected LLM for a thorough review."""
    
    prompt = (
        "You are an expert Python Code Reviewer.\n"
        "Analyze the following Python code for bugs, improvements, and best-practice issues.\n"
        "Provide a structured response with:\n"
        "1. **Overall Summary**: A brief sentence on the code quality.\n"
        "2. **Critical Issues**: Bugs or security flaws.\n"
        "3. **Improvements**: Suggestions for refactoring or optimization.\n"
        "4. **Best Practices**: PEP 8, type hinting, etc.\n\n"
        "Code:\n"
        "```python\n"
        + code + 
        "\n```\n"
    )
    
    try:
        if provider == "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY) 
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        elif provider == "Google Gemini":
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY) 
            model_instance = genai.GenerativeModel(model)
            response = model_instance.generate_content(prompt)
            return response.text
            
        elif provider == "Ollama (Local)":
            # Ollama runs locally on port 11434. We use the OpenAI library 
            # because Ollama mimics the OpenAI API structure.
            from openai import OpenAI
            client = OpenAI(
                base_url="http://localhost:11434/v1", 
                api_key="ollama" # Required by the library, but ignored by Ollama
            )
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
            
        else:
            return "Please select a valid provider."
    except Exception as e:
        return f"AI Review failed: {str(e)}"

# -----------------------------------------------------------------------------
# 3. STREAMLIT UI (The "Code Auto Reviewer" Interface)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Code Auto Reviewer", page_icon="🐍", layout="wide")
st.title("🐍 Code Auto Reviewer")
st.markdown("Analyzes Python code for bugs, improvements, and best-practice issues.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 3 OPTIONS HERE
    provider = st.selectbox("Select AI Provider", ["Google Gemini", "OpenAI", "Ollama (Local)"])
    
    if provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
        st.info("Ensure your OpenAI key is pasted at the top of app.py")
        
    elif provider == "Google Gemini":
        model = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
        st.info("Ensure your Gemini key is pasted at the top of app.py")
        
    elif provider == "Ollama (Local)":
        model = st.selectbox("Model", ["llama3", "codellama", "deepseek-coder"])
        st.success("Ollama runs locally. No API key needed!")
        st.caption("Make sure Ollama is installed and running in your terminal.")

# Main Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Code Input")
    code_input = st.text_area(
        "Paste your Python code here:", 
        height=400, 
        placeholder="def hello():\n    print('Hello World')"
    )
    
    uploaded_file = st.file_uploader("...or upload a .py file", type=["py"])
    if uploaded_file is not None:
        code_input = uploaded_file.read().decode("utf-8")
        st.text_area("Uploaded Code:", code_input, height=200, disabled=True)

    analyze_btn = st.button("🔍 Analyze Code", type="primary", use_container_width=True)

with col2:
    st.subheader("📊 Review Results")
    
    if analyze_btn and code_input:
        # --- 1. Static Analysis ---
        st.markdown("### 🛡️ Static Analysis (AST)")
        static_issues = run_static_analysis(code_input)
        
        if not static_issues:
            st.success("No structural issues found by AST analysis!")
        else:
            for issue in static_issues:
                if issue["severity"] == "CRITICAL":
                    st.error(f"**Line {issue['line']}** ({issue['type']}): {issue['message']}")
                elif issue["severity"] == "WARNING":
                    st.warning(f"**Line {issue['line']}** ({issue['type']}): {issue['message']}")
                else:
                    st.info(f"**Line {issue['line']}** ({issue['type']}): {issue['message']}")

        # --- 2. AI Semantic Review ---
        st.markdown("---")
        st.markdown("### 🤖 AI Semantic Review")
        
        with st.spinner(f"Analyzing with {provider}..."):
            ai_feedback = get_ai_review(code_input, provider, model)
            st.markdown(ai_feedback)
                
    elif analyze_btn:
        st.warning("Please enter some code to review.")