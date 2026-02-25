"""
CLI utility for managing the movie-bot system
"""
import argparse
import subprocess
import os
import sys
from pathlib import Path


class MovieBotCLI:
    """Command-line interface for Movie Bot"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
    
    def activate_venv(self):
        """Activate virtual environment"""
        if not self.venv_path.exists():
            print("Virtual environment not found. Creating...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)])
    
    def run_command(self, cmd):
        """Run a command with activated venv"""
        venv_python = self.venv_path / "bin" / "python"
        if not venv_python.exists():
            venv_python = self.venv_path / "Scripts" / "python.exe"
        
        subprocess.run([str(venv_python)] + cmd)
    
    def install_deps(self):
        """Install dependencies"""
        print("Installing dependencies...")
        self.activate_venv()
        venv_pip = self.venv_path / "bin" / "pip"
        if not venv_pip.exists():
            venv_pip = self.venv_path / "Scripts" / "pip.exe"
        
        subprocess.run([str(venv_pip), "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
    
    def setup_db(self):
        """Setup database"""
        print("Setting up database...")
        self.activate_venv()
        self.run_command(["db/load_data.py"])
        print("✅ Database setup complete")
    
    def start_api(self):
        """Start API server"""
        print("Starting API server...")
        self.activate_venv()
        self.run_command(["-m", "api_server.main"])
    
    def start_mcp(self):
        """Start MCP server"""
        print("Starting MCP server...")
        self.activate_venv()
        self.run_command(["-m", "mcp_server.server"])
    
    def start_agent(self):
        """Start agent"""
        print("Starting agent...")
        self.activate_venv()
        self.run_command(["agent/agent.py"])
    
    def test(self):
        """Run tests"""
        print("Running tests...")
        subprocess.run(["bash", "test.sh"], cwd=self.project_root)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Movie Bot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cli install            # Install dependencies
  python -m cli db                 # Setup database
  python -m cli api                # Start API server
  python -m cli mcp                # Start MCP server
  python -m cli agent              # Start agent
  python -m cli test               # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    subparsers.add_parser("install", help="Install dependencies")
    
    # Database command
    subparsers.add_parser("db", help="Setup database")
    
    # API server command
    subparsers.add_parser("api", help="Start API server")
    
    # MCP server command
    subparsers.add_parser("mcp", help="Start MCP server")
    
    # Agent command
    subparsers.add_parser("agent", help="Start agent")
    
    # Test command
    subparsers.add_parser("test", help="Run tests")
    
    args = parser.parse_args()
    
    cli = MovieBotCLI()
    
    if args.command == "install":
        cli.install_deps()
    elif args.command == "db":
        cli.setup_db()
    elif args.command == "api":
        cli.start_api()
    elif args.command == "mcp":
        cli.start_mcp()
    elif args.command == "agent":
        cli.start_agent()
    elif args.command == "test":
        cli.test()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
