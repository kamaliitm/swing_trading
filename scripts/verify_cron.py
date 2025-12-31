#!/usr/bin/env python3
"""
Helper script to verify and test cron setup for swing trading automation.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def check_cron_jobs():
    """Check if cron jobs are installed."""
    print_header("Checking Cron Jobs")
    
    try:
        result = subprocess.run(['crontab', '-l'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        
        if result.returncode == 0:
            cron_content = result.stdout.strip()
            
            if not cron_content:
                print_warning("Crontab exists but is empty")
                return False
            
            print_success("Crontab found")
            print(f"\nCurrent crontab entries:\n")
            print(cron_content)
            
            # Check for our specific jobs
            has_finalization = 'run_finalization.py' in cron_content
            has_pool_creation = 'run_pool_creation.py' in cron_content
            
            if has_finalization:
                print_success("Finalization job found in crontab")
            else:
                print_error("Finalization job NOT found in crontab")
            
            if has_pool_creation:
                print_success("Pool creation job found in crontab")
            else:
                print_error("Pool creation job NOT found in crontab")
            
            return has_finalization and has_pool_creation
        
        else:
            print_error("No crontab found")
            print("  Run 'crontab -e' to create one")
            return False
    
    except subprocess.TimeoutExpired:
        print_error("Timeout checking crontab")
        return False
    except Exception as e:
        print_error(f"Error checking crontab: {e}")
        return False


def check_paths():
    """Check if all required paths exist."""
    print_header("Checking Paths")
    
    project_root = Path(__file__).parent.parent
    required_paths = {
        'Project root': project_root,
        'Virtual environment': project_root / '.venv',
        'Python executable': project_root / '.venv' / 'bin' / 'python3',
        'Finalization script': project_root / 'scripts' / 'run_finalization.py',
        'Pool creation script': project_root / 'scripts' / 'run_pool_creation.py',
        'Data directory': project_root / 'data',
        'Logs directory': project_root / 'logs',
    }
    
    all_exist = True
    for name, path in required_paths.items():
        if path.exists():
            print_success(f"{name}: {path}")
        else:
            print_error(f"{name}: {path} (NOT FOUND)")
            all_exist = False
    
    return all_exist


def check_scripts_executable():
    """Check if scripts are executable and can run."""
    print_header("Testing Scripts")
    
    project_root = Path(__file__).parent.parent
    scripts = {
        'Finalization': project_root / 'scripts' / 'run_finalization.py',
        'Pool Creation': project_root / 'scripts' / 'run_pool_creation.py',
    }
    
    all_ok = True
    for name, script_path in scripts.items():
        print(f"\nTesting {name} script...")
        
        # Check if file exists
        if not script_path.exists():
            print_error(f"Script not found: {script_path}")
            all_ok = False
            continue
        
        # Check if executable
        if not os.access(script_path, os.X_OK):
            print_warning(f"Script is not executable: {script_path}")
            print(f"  Fix with: chmod +x {script_path}")
        
        # Try to run with --help or dry-run (if supported)
        # For now, just check syntax
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(script_path)],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print_success(f"{name} script syntax is valid")
            else:
                print_error(f"{name} script has syntax errors")
                print(f"  {result.stderr.decode()}")
                all_ok = False
        except Exception as e:
            print_warning(f"Could not verify {name} script: {e}")
    
    return all_ok


def check_logs():
    """Check log files."""
    print_header("Checking Log Files")
    
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / 'logs'
    
    if not logs_dir.exists():
        print_warning(f"Logs directory does not exist: {logs_dir}")
        print("  It will be created automatically when jobs run")
        return True
    
    log_files = {
        'Finalization': logs_dir / 'finalization.log',
        'Pool Creation': logs_dir / 'pool_creation.log',
    }
    
    for name, log_path in log_files.items():
        if log_path.exists():
            size = log_path.stat().st_size
            if size > 0:
                print_success(f"{name} log exists ({size} bytes)")
                # Show last few lines
                try:
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            print(f"  Last line: {lines[-1].strip()}")
                except Exception as e:
                    print_warning(f"Could not read log: {e}")
            else:
                print_warning(f"{name} log exists but is empty")
        else:
            print_warning(f"{name} log does not exist yet (will be created on first run)")


def show_cron_instructions():
    """Show instructions for adding cron jobs."""
    print_header("How to Add Cron Jobs")
    
    project_root = Path(__file__).parent.parent
    crontab_example = project_root / 'crontab.example'
    
    print("1. Edit your crontab:")
    print(f"   {YELLOW}crontab -e{RESET}")
    print("\n2. Add these lines (update PROJECT_PATH if needed):")
    print()
    
    if crontab_example.exists():
        with open(crontab_example, 'r') as f:
            lines = f.readlines()
            # Show only the actual cron entries (skip comments)
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    print(f"   {line.rstrip()}")
    else:
        print(f"   PROJECT_PATH={project_root}")
        print(f"   15 15 * * 1-5 cd $PROJECT_PATH && $PROJECT_PATH/.venv/bin/python3 scripts/run_finalization.py >> logs/finalization.log 2>&1")
        print(f"   30 16 * * 1-5 cd $PROJECT_PATH && $PROJECT_PATH/.venv/bin/python3 scripts/run_pool_creation.py >> logs/pool_creation.log 2>&1")
    
    print("\n3. Save and exit the editor")
    print("\n4. Verify with:")
    print(f"   {YELLOW}crontab -l{RESET}")


def test_manual_run():
    """Test if scripts can run manually."""
    print_header("Testing Manual Execution")
    
    project_root = Path(__file__).parent.parent
    venv_python = project_root / '.venv' / 'bin' / 'python3'
    
    if not venv_python.exists():
        print_error("Virtual environment Python not found")
        return False
    
    print("Testing scripts with dry-run (checking imports and basic execution)...")
    
    scripts = {
        'Finalization': project_root / 'scripts' / 'run_finalization.py',
        'Pool Creation': project_root / 'scripts' / 'run_pool_creation.py',
    }
    
    all_ok = True
    for name, script_path in scripts.items():
        print(f"\nTesting {name}...")
        try:
            # Try importing the main module to check dependencies
            result = subprocess.run(
                [str(venv_python), '-c', f'import sys; sys.path.insert(0, "{project_root}"); exec(open("{script_path}").read().split("if __name__")[0])'],
                capture_output=True,
                timeout=10,
                cwd=str(project_root)
            )
            
            if result.returncode == 0:
                print_success(f"{name} script can be executed")
            else:
                stderr = result.stderr.decode()
                if 'ModuleNotFoundError' in stderr or 'ImportError' in stderr:
                    print_error(f"{name} script has import errors")
                    print(f"  {stderr[:200]}")
                else:
                    print_warning(f"{name} script execution check completed (may have runtime errors)")
        except Exception as e:
            print_warning(f"Could not fully test {name}: {e}")
    
    return all_ok


def main():
    """Main function."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Swing Trading Cron Setup Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"\nProject: {Path(__file__).parent.parent}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run checks
    paths_ok = check_paths()
    scripts_ok = check_scripts_executable()
    cron_installed = check_cron_jobs()
    check_logs()
    
    # Summary
    print_header("Summary")
    
    if paths_ok:
        print_success("All required paths exist")
    else:
        print_error("Some paths are missing")
    
    if scripts_ok:
        print_success("Scripts are valid")
    else:
        print_error("Some scripts have issues")
    
    if cron_installed:
        print_success("Cron jobs are installed")
    else:
        print_error("Cron jobs are NOT installed")
        show_cron_instructions()
    
    # Test manual execution (skip in non-interactive mode)
    try:
        print("\n")
        test_manual = input("Do you want to test manual script execution? (y/n): ").strip().lower()
        if test_manual == 'y':
            test_manual_run()
    except EOFError:
        # Non-interactive mode, skip manual test
        pass
    
    print_header("Next Steps")
    print("1. If cron jobs are not installed, follow the instructions above")
    print("2. Verify cron jobs with: crontab -l")
    print("3. Check logs after jobs run: tail -f logs/*.log")
    print("4. Test manually: python scripts/run_finalization.py")
    print("\n")


if __name__ == "__main__":
    main()

