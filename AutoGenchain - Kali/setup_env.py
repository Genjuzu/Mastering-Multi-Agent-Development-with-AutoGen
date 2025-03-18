import os
import sys
import subprocess
import platform

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")
    else:
        print(f"Directory already exists: {path}")

def setup_environment():
    """Set up the virtual environment and install dependencies"""
    # Create virtual environment
    venv_name = "bugbounty-env"
    
    if platform.system() == "Windows":
        venv_path = os.path.join(os.getcwd(), venv_name)
        activate_script = os.path.join(venv_path, "Scripts", "activate")
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        venv_path = os.path.join(os.getcwd(), venv_name)
        activate_script = os.path.join(venv_path, "bin", "activate")
        python_exe = os.path.join(venv_path, "bin", "python")
        pip_exe = os.path.join(venv_path, "bin", "pip")
    
    # Create virtual environment
    print("Creating virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", venv_name])
    
    # Install dependencies
    print("Installing dependencies...")
    requirements_file = os.path.join(os.getcwd(), "requirements.txt")
    
    if platform.system() == "Windows":
        subprocess.check_call([pip_exe, "install", "-r", requirements_file])
    else:
        subprocess.check_call([pip_exe, "install", "-r", requirements_file])
    
    print(f"Virtual environment created at {venv_path}")
    print(f"Activate with: {activate_script}")

def create_project_structure():
    """Create the project directory structure"""
    # Create main project directories
    project_root = "bugbounty-agents"
    create_directory(project_root)
    
    # Create subdirectories
    directories = [
        os.path.join(project_root, "langchain_agent"),
        os.path.join(project_root, "autogen_agents"),
        os.path.join(project_root, "knowledge_base"),
        os.path.join(project_root, "utils"),
        os.path.join(project_root, "data"),
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create initial files
    create_file(os.path.join(project_root, "__init__.py"), "")
    create_file(os.path.join(project_root, "langchain_agent", "__init__.py"), "")
    create_file(os.path.join(project_root, "autogen_agents", "__init__.py"), "")
    create_file(os.path.join(project_root, "utils", "__init__.py"), "")
    
    # Create .env file template
    env_content = """# API Keys
OPENAI_API_KEY=your-openai-api-key-here

# Agent Configuration
MAIN_AGENT_TEMPERATURE=0.2
AUTOGEN_TEMPERATURE=0.7

# Paths
KNOWLEDGE_BASE_PATH=./bugbounty-agents/knowledge_base
"""
    create_file(os.path.join(project_root, ".env.template"), env_content)
    
    # Create README
    readme_content = """# Bug Bounty Hybrid Agent System

A hybrid system combining Langchain and AutoGen agents for bug bounty planning and execution.

## Setup

1. Create a virtual environment:
   ```
   python setup_env.py
   ```

2. Activate the virtual environment:
   - Windows: `bugbounty-env\\Scripts\\activate`
   - Linux/Mac: `source bugbounty-env/bin/activate`

3. Copy `.env.template` to `.env` and fill in your API keys.

4. Run the main script:
   ```
   python -m bugbounty-agents.main
   ```

## Project Structure

- `langchain_agent/`: Main Langchain agent with RAG capabilities
- `autogen_agents/`: Specialized AutoGen agents
- `knowledge_base/`: Penetration testing knowledge
- `utils/`: Helper functions and utilities
- `data/`: Data storage and processing

## License

MIT
"""
    create_file(os.path.join("README.md"), readme_content)
    
    # Create initial main.py
    main_content = """import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("Bug Bounty Hybrid Agent System")
    print("==============================")
    print("Initializing system...")
    
    # TODO: Implement agent initialization and workflow
    
    print("System initialized successfully!")

if __name__ == "__main__":
    main()
"""
    create_file(os.path.join(project_root, "main.py"), main_content)

def create_file(path, content):
    """Create a file with the given content"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created file: {path}")

if __name__ == "__main__":
    print("Setting up Bug Bounty Hybrid Agent System...")
    setup_environment()
    create_project_structure()
    print("\nSetup complete! Follow the instructions in README.md to get started.") 