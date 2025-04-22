# ui_manager.py
# Handles all user interface elements: startup, prompts, output formatting.

import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import pyfiglet
import time

# Initialize the Rich Console globally
console = Console()

def display_startup():
    """Displays the cool ASCII art startup sequence - Line by Line."""
    console.clear() # Start with a clear screen (optional)
    try:
        ascii_banner_str = pyfiglet.figlet_format("Swodnil", font="slant")
        lines = ascii_banner_str.splitlines()
        delay = 0.25 # Adjust delay between lines (seconds)

        console.print() # Initial newline
        for line in lines:
            console.print(f"[bold magenta]{line}[/bold magenta]")
            time.sleep(delay)
        console.print() # Extra newline after banner

    except Exception as e:
        # Fallback if pyfiglet fails
        console.print("[bold magenta] S W O D N I L [/bold magenta]")
        console.print(f"[yellow]Note: pyfiglet banner failed: {e}[/yellow]")

    console.print("[magenta]Welcome to Swodnil - A Linux to Windows command translator![/magenta]")
    console.print("[dim]Type 'help' to get started.[/dim]")
    console.print("[dim]Type 'exit' or 'quit' at any time.[/dim]\n")

def display_help_page():
    """Displays the custom Swodnil help page."""
    console.print() # Add spacing before the help page
    console.print(Panel(
        "[bold red]Welcome to Swodnil, a program built by Daolyap[/]\n\n"
        "A command-line interface providing a Linux-like experience on Windows.\n"
        "It translates many common Linux commands and flags into their PowerShell equivalents."
        "I am open to suggestions!",
        title="Swodnil Help",
        border_style="magenta",
        expand=False
    ))
    console.print()

    # --- Built-in Commands ---
    builtins_table = Table(
        title="[bold magenta]Built-in Shell Commands[/]",
        show_header=True,
        header_style="bold blue",
        border_style="dim"
    )
    builtins_table.add_column("Command", style="magenta", width=25)
    builtins_table.add_column("Description")

    builtins_table.add_row("help", "Display this help message.")
    builtins_table.add_row("cd [directory]", "Change the current working directory (use '~' for home).")
    builtins_table.add_row("exit | quit", "Terminate the Swodnil shell session.")
    builtins_table.add_row("history", "Show the command history for the current session.")
    builtins_table.add_row("alias", "List all defined command aliases.")
    builtins_table.add_row("alias name='command'", "Define a new command alias.")
    builtins_table.add_row("unalias name", "Remove a previously defined alias.")
    builtins_table.add_row("export NAME=VALUE", "Set an environment variable for Swodnil and its child processes.")
    builtins_table.add_row("unset NAME", "Remove an environment variable.")

    console.print(builtins_table)
    console.print()

    # --- Translated Commands Examples ---
    translated_table = Table(
        title="[bold magenta]Common Translated Commands (Examples)[/]",
        show_header=True,
        header_style="bold blue",
        border_style="dim"
    )
    translated_table.add_column("Linux Command(s)", style="magenta", width=25)
    translated_table.add_column("Purpose / Windows Equivalent")

    translated_table.add_row("ls, dir", "List directory contents (uses [dim]Get-ChildItem[/]).")
    translated_table.add_row("cp", "Copy files/directories (uses [dim]Copy-Item[/]).")
    translated_table.add_row("mv", "Move/rename files/directories (uses [dim]Move-Item[/]).")
    translated_table.add_row("rm, del", "Remove files/directories (uses [dim]Remove-Item[/]).")
    translated_table.add_row("mkdir", "Create directories (uses [dim]New-Item[/]).")
    translated_table.add_row("cat", "Display file content (uses [dim]Get-Content[/]; special handling for paths like /etc/fstab, /proc/cpuinfo).")
    translated_table.add_row("grep", "Search text using patterns (uses [dim]Select-String[/]).")
    translated_table.add_row("pwd", "Print current working directory.")
    translated_table.add_row("clear", "Clear the terminal screen (uses [dim]Clear-Host[/]).")
    translated_table.add_row("wget, curl", "Download files from the web (uses [dim]Invoke-WebRequest[/]).")
    translated_table.add_row("ps", "List running processes (uses [dim]Get-Process[/]).")
    translated_table.add_row("kill, killall", "Terminate processes (uses [dim]Stop-Process[/]; may need elevation).")
    translated_table.add_row("df", "Show disk space usage (uses [dim]Get-PSDrive[/] or [dim]Get-Volume[/]).")
    translated_table.add_row("apt, yum, dnf, pacman, zypper", "Manage software packages (uses [dim]winget[/]; install/upgrade/remove need elevation).")
    translated_table.add_row("hostname", "Show the computer name.")
    translated_table.add_row("which, command -v", "Locate a command (uses [dim]Get-Command[/]).")
    # Add more key examples if desired

    console.print(translated_table)
    console.print("\n[italic]Note: This is not an exhaustive list. Many other commands and flags are translated or passed to PowerShell.[/italic]\n")

    # --- General Info ---
    console.print(Panel(
        "[bold]How Translation Works:[/]\n"
        "- Swodnil intercepts commands and checks its internal map.\n"
        "- If a match is found (e.g., 'ls -l'), it constructs the equivalent PowerShell command (e.g., 'Get-ChildItem | Format-Table ...').\n"
        "- If no specific translation exists, the command is passed directly to PowerShell for execution.\n"
        "- Package management commands (apt, yum, etc.) are mapped to [magenta]winget[/].\n"
        "- Some commands (like software installs or specific system queries) may require [yellow]Administrator privileges[/] and will trigger a UAC prompt.",
        title="Under the Hood",
        border_style="green",
        expand=False
    ))
    console.print()
    console.print("Type [magenta]exit[/] or [magenta]quit[/] to leave Swodnil.")
    console.print()

def get_prompt_input() -> str:
    """Gets user input with a formatted prompt."""
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = "[dim]?[/dim]" # Handle cases where CWD might be inaccessible

    prompt_str = f"[bold blue]{cwd}[/bold blue] [green]❯[/green] "

    try:
        user_input = console.input(prompt_str)
        return user_input
    except EOFError:
        console.print("\n[yellow]EOF detected. Exiting.[/yellow]")
        return "exit"
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        return "" # Return empty string to show a new prompt

def display_output(stdout: str | None, stderr: str | None):
    """Displays the standard output and standard error from commands."""
    if stdout and stdout.strip():
        console.print(stdout.strip())
    if stderr and stderr.strip():
        # Check for common non-error stderr messages from winget if needed later
        # Example: if "winget" in context and ("%" in stderr or "Found" in stderr): color="yellow" else: color="red"
        console.print(f"[bold red]Stderr: {stderr.strip()}[/bold red]")

def display_error(message: str):
    """Displays an internal error message from Swodnil itself."""
    console.print(f"[bold red]Swodnil Error: {message}[/bold red]")

def display_warning(message: str):
    """Displays an internal warning message from Swodnil itself."""
    console.print(f"[bold yellow]Swodnil Warning: {message}[/bold yellow]")

def display_info(message: str):
    """Displays an internal informational message from Swodnil itself."""
    console.print(f"[magenta]{message}[/magenta]")

def display_list(items: list[str], title: str = "Items"):
    """Displays a list of items, possibly in a table for better formatting."""
    if not items:
        console.print(f"[dim]No {title.lower()} to display.[/dim]")
        return

    # Simple numbered list for now
    for i, item in enumerate(items, 1):
        console.print(f"{i:>4}: {item}")

# --- Placeholder/Example Usage ---
if __name__ == "__main__":
    display_startup()
    test_input = get_prompt_input()
    print(f"You entered: {test_input}")
    display_output("This is sample stdout.", "This is sample stderr.")
    display_error("This is a sample internal error.")
    display_warning("This is a sample warning.")
    display_info("This is sample info.")
    display_list(["item 1", "item 2 with space"], title="Test List")