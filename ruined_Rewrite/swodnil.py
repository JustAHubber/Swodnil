# swodnil.py
# Main entry point for the Swodnil application.

import sys
# Add project root to path if needed, depending on execution context
# import os
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Ensure all core modules are importable
    import shell_core
    import ui_manager
    import command_translator # Import to check dependency (psutil) early
except ImportError as e:
    print(f"Error importing required modules: {e}", file=sys.stderr)
    print("Please ensure 'rich', 'pyfiglet', and 'psutil' are installed (`pip install rich pyfiglet psutil`)", file=sys.stderr)
    # Also ensure all Swodnil files (shell_core.py etc.) are in the same directory or Python path.
    sys.exit(1)

def main():
    """Main function to set up and run the Swodnil shell."""

    # Check for optional dependency 'psutil' early (used by command_translator)
    # Display warning if missing but allow startup
    if command_translator.psutil is None:
         ui_manager.display_warning("Module 'psutil' not found. Neofetch simulation and some 'df' features will be unavailable.")
         ui_manager.display_warning("Install it using: pip install psutil")

    # Display the startup banner and messages using ui_manager's console
    ui_manager.display_startup()

    # Start the core shell loop
    try:
        shell_core.run_shell()
    except KeyboardInterrupt:
        # Handle Ctrl+C at the main loop level gracefully
        ui_manager.console.print("\n[yellow]Keyboard Interrupt detected. Exiting.[/yellow]")
    except Exception as e:
        # Catch unexpected errors in the main loop and display using rich
        ui_manager.console.print("\n[bold red]--- UNEXPECTED CRITICAL ERROR ---[/]")
        ui_manager.console.print_exception(show_locals=True) # Detailed traceback
        ui_manager.display_error(f"An unexpected critical error occurred: {e}")
        ui_manager.console.print("[bold red]---------------------------------[/]")
    finally:
        # Ensure exit message is printed
        ui_manager.console.print("\n[bold red]Exiting Swodnil. Goodbye![/bold red]") # Use purple theme

if __name__ == "__main__":
    main()