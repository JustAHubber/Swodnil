import subprocess
import os
import shlex
from rich import print as rprint # Use rprint to avoid conflict with input prompt
from rich.console import Console
import pyfiglet

console = Console()

# --- Translation Setup ---
# Simple mapping, real version needs function handlers for args
translation_map = {
    'ls': 'Get-ChildItem',
    'pwd': 'Get-Location',
    'cp': 'Copy-Item',
    'mv': 'Move-Item',
    'rm': 'Remove-Item',
    'mkdir': 'New-Item -ItemType Directory',
    'grep': 'Select-String',
    # More complex commands need specific functions
}

def translate_apt(args):
    if not args:
        return "winget --help" # Or similar
    sub_command = args[0]
    packages = " ".join(args[1:])
    if sub_command == 'update':
        return "winget source update"
    elif sub_command == 'upgrade':
        # winget upgrade needs package names or --all
        return f"winget upgrade {packages if packages else '--all'}"
    elif sub_command == 'install':
        if not packages: return "echo 'Usage: apt install <package>...'"
        return f"winget install {packages}"
    elif sub_command == 'remove' or sub_command == 'purge':
        if not packages: return "echo 'Usage: apt remove <package>...'"
        return f"winget uninstall {packages}"
    elif sub_command == 'search':
        if not packages: return "echo 'Usage: apt search <query>'"
        return f"winget search {packages}"
    else:
        return f"winget {sub_command} {packages}" # Best guess passthrough

# --- Startup Sequence ---
ascii_banner = pyfiglet.figlet_format("Swodnil", font="slant")
rprint(f"[bold magenta]{ascii_banner}[/bold magenta]")
rprint("[cyan]Welcome! Type 'exit' or 'quit' to exit.[/cyan]\n")

# --- Main Loop ---
while True:
    try:
        # Get current directory for prompt
        cwd = os.getcwd()
        # Basic prompt (prompt_toolkit could make this fancier)
        prompt_str = f"[bold blue]{cwd}[/bold blue] [green]❯[/green] "
        raw_input = console.input(prompt_str)

        if not raw_input.strip():
            continue

        # Basic exit command
        if raw_input.strip().lower() in ['exit', 'quit']:
            break

        # Parse input
        parts = shlex.split(raw_input)
        command = parts[0]
        args = parts[1:]

        final_command = ""

        # --- Translation Logic ---
        if command == 'cd':
            # Handle 'cd' directly as it changes the script's state
            if not args:
                # 'cd' without args often goes home, let's just print cwd
                 rprint(f"[yellow]{os.getcwd()}[/yellow]")
                 continue
            try:
                os.chdir(args[0])
                # Update prompt for next iteration, no command execution needed
                continue
            except FileNotFoundError:
                rprint(f"[bold red]Error: Directory not found: {args[0]}[/bold red]")
                continue
            except Exception as e:
                rprint(f"[bold red]Error changing directory: {e}[/bold red]")
                continue

        elif command in translation_map:
            # Simple 1-to-1 mapping (needs arg handling!)
            translated_cmd = translation_map[command]
            final_command = f"{translated_cmd} {' '.join(args)}" # Basic arg passing

        elif command in ['apt', 'apt-get']:
            final_command = translate_apt(args)

        else:
            # Assume native command
            final_command = raw_input # Pass the raw input

        # --- Execution Logic ---
        if final_command:
            rprint(f"[dim]Executing: {final_command}[/dim]")
            try:
                # Execute using PowerShell
                # Using shell=True can be a security risk if not careful with input
                # Using shell=False is safer but requires command path resolution
                # For simplicity here, using shell=True with powershell
                # A better approach uses shell=False and passes args safely
                process = subprocess.run(
                    ['powershell', '-Command', final_command],
                    capture_output=True,
                    text=True,
                    encoding='utf-8', # Explicitly set encoding
                    errors='replace', # Handle potential encoding errors
                    shell=False, # Safer - PowerShell handles the command string
                    cwd=os.getcwd() # Ensure it runs in the correct directory
                )

                # Print output
                if process.stdout:
                    console.print(process.stdout.strip())
                if process.stderr:
                    # Winget often prints progress to stderr, check if it's just that
                    if "winget" in final_command and ("%" in process.stderr or "Found" in process.stderr or "Starting" in process.stderr):
                         console.print(f"[yellow]{process.stderr.strip()}[/yellow]")
                    else:
                         console.print(f"[bold red]Stderr: {process.stderr.strip()}[/bold red]")

            except FileNotFoundError:
                 rprint(f"[bold red]Error: 'powershell' command not found. Is PowerShell installed and in PATH?[/bold red]")
            except Exception as e:
                rprint(f"[bold red]Execution Error: {e}[/bold red]")

    except KeyboardInterrupt:
        rprint("\n[yellow]Ctrl+C detected. Type 'exit' to quit.[/yellow]")
    except EOFError:
        rprint("\n[yellow]EOF detected. Exiting.[/yellow]")
        break