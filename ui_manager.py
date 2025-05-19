# ui_manager.py
# Handles all user interface elements: startup, prompts, output formatting.

import os
import time # For startup animation
import sys # For flushing stdout in startup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live # For startup animation
from rich.spinner import Spinner # For startup animation
# Import Text for potential advanced prompt formatting (though list of tuples is used now)
from rich.text import Text
import pyfiglet

# Initialize the Rich Console globally
console = Console()

def display_startup():
    """Displays a loading sequence followed by the static ASCII art banner."""
    console.clear() # Start clean
    console.print() # Initial newline for spacing

    # --- Phase 1: Short Loading Sequence ---
    loading_stages = [
        ("Initializing Swodnil Core...", 0.4),
        ("Loading translation matrix...", 0.5),
        ("Engaging PowerShell bridge...", 0.3),
        ("Done!", 0.1)
    ]
    spinner = Spinner("dots", text=" Starting...")

    try:
        # Pass console explicitly to Live if running in non-standard environments
        with Live(spinner, refresh_per_second=10, transient=True, console=console) as live:
            for text, delay in loading_stages:
                spinner.update(text=f" {text}")
                live.refresh()
                time.sleep(delay)
        # Spinner disappears automatically here
    except Exception as e:
         console.print(f"[yellow]Warning: Loading animation skipped due to error: {e}[/yellow]")


    # --- Phase 2: Static ASCII Banner ---
    try:
        # Consider adding a check if pyfiglet is installed
        ascii_banner_str = pyfiglet.figlet_format("Swodnil", font="slant") # Or your preferred font
        styled_banner = f"\n[bold magenta]{ascii_banner_str}[/bold magenta]\n" # Add spacing

        # Print the fully formed banner at once
        console.print(styled_banner)

    except Exception as e:
        # Fallback if pyfiglet fails
        console.print(f"\n[bold magenta] S W O D N I L [/bold magenta]\n")
        console.print(f"[yellow]Note: pyfiglet banner failed: {e}[/yellow]")

    # --- Phase 3: Static Welcome Messages ---
    console.print("[bold purple]Welcome to Swodnil - Linux commands on Windows![/bold purple]")
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]\n")


# --- Helper function to format the prompt string for prompt_toolkit ---
def get_prompt_string(cwd: str):
    """
    Returns a list of (style_string, text_string) tuples for prompt_toolkit prompt formatting.
    These style strings are basic prompt_toolkit styles.
    """
    # Define prompt_toolkit style strings.
    cwd_style = 'bold #8A2BE2'  # Hex code for BlueViolet purple
    symbol_style = 'fg:magenta' # Standard magenta

    # Construct the list of tuples
    prompt_tuples = [
        (cwd_style, cwd),
        ('', ' '),           # Unstyled space
        (symbol_style, '❯'),
        ('', ' '),           # Unstyled space after symbol
    ]
    return prompt_tuples


def display_output(stdout: str | None, stderr: str | None):
    """Displays captured standard output and standard error from commands (Batch Mode)."""
    if stdout and stdout.strip():
        console.print(stdout.strip())
    if stderr and stderr.strip():
        console.print(f"[bold red]Stderr: {stderr.strip()}[/bold red]")

def display_streamed_output(line: str, is_stderr: bool):
    """Displays a single line of output, coloring stderr."""
    if is_stderr:
        console.print(f"[bold red]{line}[/bold red]")
    else:
        console.print(line)

# Corrected signature to include optional argument
def display_error(message: str, skip_if_stderr: bool = False):
    """
    Displays an internal error message from Swodnil itself,
    or a command execution error.
    The skip_if_stderr flag is intended to avoid redundant messages but isn't fully used yet.
    """
    console.print(f"[bold red]Swodnil: {message}[/bold red]")

def display_warning(message: str):
    """Displays an internal warning message from Swodnil itself."""
    console.print(f"[bold yellow]Swodnil Warning: {message}[/bold yellow]")

def display_info(message: str):
    """Displays an internal informational message from Swodnil itself."""
    console.print(f"[lightblue]{message}[/lightblue]") # Purple theme

def display_list(items: list[str], title: str = "Items"):
    """Displays a list of items, possibly in a table for better formatting."""
    if not items:
        console.print(f"[dim]No {title.lower()} to display.[/dim]")
        return
    # Use purple theme for list title and numbers
    console.print(f"[bold purple]{title}:[/]")
    for i, item in enumerate(items, 1):
        console.print(f"[purple]{i:>4}[/]: {item}")
    console.print() # Add spacing after list

def display_help_page():
    """Displays the custom Swodnil help page with purple theme."""
    console.print()
    console.print(Panel(
        "[bold purple]Welcome to Swodnil![/]\n\n"
        "A command-line interface providing a Linux-like experience on Windows.\n"
        "It translates many common Linux commands and flags into their PowerShell equivalents.",
        title="Swodnil Help",
        border_style="purple",
        expand=False
    ))
    console.print()

    # --- Built-in Commands ---
    builtins_table = Table(
        title="[bold purple]Built-in Shell Commands[/]",
        show_header=True,
        header_style="bold medium_purple",
        border_style="dim"
    )
    builtins_table.add_column("Command", style="magenta", width=25)
    builtins_table.add_column("Description")
    builtins_table.add_row("help", "Display this help message.")
    builtins_table.add_row("cd [directory]", "Change directory (use '~' for home).")
    builtins_table.add_row("exit | quit", "Terminate the Swodnil shell session.")
    builtins_table.add_row("history", "Show command history for the current session.")
    builtins_table.add_row("alias", "List all defined command aliases.")
    builtins_table.add_row("alias name='command'", "Define a new command alias (saved persistently).")
    builtins_table.add_row("unalias name", "Remove a previously defined alias (saved persistently).")
    builtins_table.add_row("export NAME=VALUE", "Set an environment variable for Swodnil/child processes.")
    builtins_table.add_row("unset NAME", "Remove an environment variable.")
    console.print(builtins_table)
    console.print()

    # --- Translated Commands Examples ---
    translated_table = Table(
        title="[bold purple]Common Translated Commands (Examples)[/]",
        show_header=True,
        header_style="bold medium_purple",
        border_style="dim"
    )
    translated_table.add_column("Linux Command(s)", style="magenta", width=25)
    translated_table.add_column("Purpose / Windows Equivalent")
    translated_table.add_row("ls, dir", "List contents ([dim]Get-ChildItem[/]).")
    translated_table.add_row("cp", "Copy ([dim]Copy-Item[/]).")
    translated_table.add_row("mv", "Move/rename ([dim]Move-Item[/]).")
    translated_table.add_row("rm, del", "Remove ([dim]Remove-Item[/]).")
    translated_table.add_row("mkdir", "Create directory ([dim]New-Item[/]).")
    translated_table.add_row("cat", "Display file content ([dim]Get-Content[/]; special path handling).")
    translated_table.add_row("grep", "Search text ([dim]Select-String[/]).")
    translated_table.add_row("pwd", "Print current directory.")
    translated_table.add_row("clear", "Clear screen ([dim]Clear-Host[/]).")
    translated_table.add_row("wget, curl", "Download web content ([dim]Invoke-WebRequest[/]).")
    translated_table.add_row("ps", "List processes ([dim]Get-Process[/]).")
    translated_table.add_row("kill, killall", "Terminate processes ([dim]Stop-Process[/]; may need elevation).")
    translated_table.add_row("df", "Disk usage ([dim]Get-PSDrive[/] or [dim]Get-Volume[/]).")
    translated_table.add_row("apt, yum, dnf, pacman, zypper", "Manage software packages (uses [magenta]winget[/]; needs elevation for changes).")
    translated_table.add_row("hostname", "Show the computer name.")
    translated_table.add_row("which, command -v", "Locate a command ([dim]Get-Command[/]).")
    console.print(translated_table)
    console.print("\n[italic]Note: Includes common flags. Many others translated or passed to PowerShell.[/italic]\n")

    # --- Shell Operators ---
    operators_table = Table(
        title="[bold purple]Shell Operators[/]",
        show_header=True,
        header_style="bold medium_purple",
        border_style="dim"
    )
    operators_table.add_column("Operator", style="magenta", width=10)
    operators_table.add_column("Description")
    operators_table.add_row("|", "Pipe: Send output of one command to the input of the next.")
    operators_table.add_row("&&", "AND: Execute next command only if the previous one succeeds (exit code 0).")
    operators_table.add_row(";", "Semicolon: Execute next command regardless of previous success/failure.")
    operators_table.add_row("&", "Background: Run the preceding command(s) in the background (at end of line).")
    # Add redirection later if implemented: >, >>, <, 2>
    console.print(operators_table)
    console.print()

    # --- General Info ---
    console.print(Panel(
        "[bold]How Translation Works:[/]\n"
        "- Swodnil intercepts commands and checks its internal map.\n"
        "- If a match is found (e.g., 'ls -l'), it constructs the equivalent PowerShell command.\n"
        "- If no specific translation exists, the command is passed directly to PowerShell.\n"
        "- Package management commands (apt, yum, etc.) are mapped to [magenta]winget[/].\n"
        "- Some commands may require [yellow]Administrator privileges[/] and trigger a UAC prompt (elevation disallowed in pipelines/background).",
        title="Under the Hood",
        border_style="medium_purple",
        expand=False
    ))
    console.print()
    console.print("Type [magenta]exit[/] or [magenta]quit[/] to leave Swodnil.")
    console.print()


# --- Placeholder/Example Usage ---
if __name__ == "__main__":
    display_startup()
    display_help_page()
    # Cannot easily test prompt here anymore
    # print(f"You entered: {test_input}")
    display_output("This is sample stdout.", "This is sample stderr.")
    print("--- Testing Streamed Output ---")
    display_streamed_output("This is line 1 from stdout.", False)
    display_streamed_output("This is line 2 from stderr.", True)
    display_streamed_output("This is line 3 from stdout.", False)
    print("--- End Streamed Test ---")
    display_error("This is a sample internal error.")
    display_warning("This is a sample warning.")
    display_info("This is sample info.")
    display_list(["item 1", "item 2 with space"], title="Test List")