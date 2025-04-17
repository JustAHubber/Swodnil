# swodnil.py
# Main entry point for the Swodnil application.

import sys
# Add project root to path if needed, depending on execution context
# import os
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import shell_core
    import ui_manager
    import command_translator # Ensure it's importable, check for psutil early?
except ImportError as e:
    print(f"Error importing required modules: {e}", file=sys.stderr)
    print("Please ensure 'rich', 'pyfiglet', and 'psutil' are installed (`pip install rich pyfiglet psutil`)", file=sys.stderr)
    sys.exit(1)

def main():
    """Main function to set up and run the Swodnil shell."""
    # Display the startup banner and messages using ui_manager's console
    ui_manager.display_startup()

    # Start the co shell loop
    try:
        shell_core.run_shell()
    except Exception as e:
        # Catch unexpected errors in the main loop and display using rich
        ui_manager.console.print_exception(show_locals=True) # Detailed traceback
        ui_manager.display_error(f"An unexpected critical error occurred: {e}")
    finally:
        ui_manager.console.print("\n[bold cyan]Exiting Swodnil. Goodbye![/bold cyan]")

if __name__ == "__main__":
    # Check for psutil dependency needed by neofetch simulation
    if command_translator.psutil is None:
         ui_manager.display_warning("Module 'psutil' not found. Neofetch simulation and some 'df' features will be unavailable.")
         ui_manager.display_warning("Install it using: pip install psutil")

    main()