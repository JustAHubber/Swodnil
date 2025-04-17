# ui_manager.py
# Handles all user interface elements: startup, prompts, output formatting.

import os
from rich.console import Console
from rich.table import Table
import pyfiglet

# Initialize the Rich Console globally
console = Console()

def display_startup():
    """Displays the cool ASCII art startup sequence."""
    console.print("\n" * 2) # Add some spacing before
    try:
        ascii_banner = pyfiglet.figlet_format("Swodnil", font="slant")
        console.print(f"[bold magenta]{ascii_banner}[/bold magenta]")
    except Exception as e:
        console.print("[bold magenta] S W O D N I L [/bold magenta]")
        console.print(f"[yellow]Note: pyfiglet banner failed: {e}[/yellow]")

    console.print("[cyan]Welcome to Swodnil - Linux commands on Windows![/cyan]")
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]\n")

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
    console.print(f"[cyan]{message}[/cyan]")

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