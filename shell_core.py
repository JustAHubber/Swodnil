# shell_core.py
# Contains the main REPL, command execution logic, and state management.

import os
import subprocess
import shlex
import copy # For deep copying environment
import base64 # For encoding elevated commands

import ui_manager
import command_translator

# Constants from command_translator
SIMULATION_MARKER_PREFIX = command_translator.SIMULATION_MARKER_PREFIX
NO_EXEC_MARKER = command_translator.NO_EXEC_MARKER

def run_shell():
    """Runs the main Read-Evaluate-Print Loop (REPL) for Swodnil."""

    # Shell State
    command_history: list[str] = []
    aliases: dict[str, str] = {
        'll': 'ls -l',
        'la': 'ls -la',
    }
    # Start with a copy of the current process environment
    # Modifications via 'export'/'unset' only affect commands run *through* Swodnil
    shell_environment = copy.deepcopy(os.environ)

    while True:
        # 1. Read Input
        raw_input = ui_manager.get_prompt_input()

        if not raw_input.strip():
            continue

        # Add to history BEFORE processing aliases etc.
        if raw_input.strip():
             command_history.append(raw_input)

        # --- Apply Aliases ---
        potential_alias = raw_input.split(maxsplit=1)[0]
        if potential_alias in aliases:
            alias_expansion = aliases[potential_alias]
            remaining_args = raw_input.split(maxsplit=1)[1] if ' ' in raw_input else ''
            processed_input = f"{alias_expansion} {remaining_args}".strip()
            ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_input}[/dim]")
        else:
            processed_input = raw_input

        # --- Parse the processed input ---
        try:
            parts = shlex.split(processed_input)
            if not parts: continue
            command = parts[0]
            args = parts[1:]
        except ValueError as e:
            ui_manager.display_error(f"Input parsing error: {e}")
            continue

        # --- Handle Built-in Shell Commands FIRST ---
        cmd_lower = command.lower()

        if cmd_lower in ['exit', 'quit']:
            break

        if cmd_lower == 'help':
            ui_manager.display_help_page()
            continue # Skip translation/execution for help

        if cmd_lower == 'cd':
            target_dir = os.path.expanduser("~") if not args else args[0]
            try:
                # Expand environment variables in path
                expanded_target_dir = os.path.expandvars(target_dir)
                os.chdir(expanded_target_dir)
            except FileNotFoundError:
                ui_manager.display_error(f"cd: directory not found: {expanded_target_dir}")
            except Exception as e:
                ui_manager.display_error(f"cd: failed to change directory to '{expanded_target_dir}': {e}")
            continue # Handled internally

        if cmd_lower == 'history':
            ui_manager.display_list(command_history, title="Command History")
            continue # Handled internally

        if cmd_lower == 'alias':
            if not args: # Print all aliases
                alias_items = [f"{name}='{cmd}'" for name, cmd in aliases.items()]
                ui_manager.display_list(alias_items, title="Aliases")
            elif '=' in args[0]: # Define alias
                try:
                    name, cmd = args[0].split('=', 1)
                    if cmd.startswith("'") and cmd.endswith("'"): cmd = cmd[1:-1]
                    elif cmd.startswith('"') and cmd.endswith('"'): cmd = cmd[1:-1]
                    aliases[name] = cmd
                    ui_manager.display_info(f"Alias '{name}' set.")
                except ValueError:
                     ui_manager.display_error("alias: invalid format. Use name='command'")
            else: # Print specific alias
                 name_to_show = args[0]
                 if name_to_show in aliases:
                      ui_manager.console.print(f"alias {name_to_show}='{aliases[name_to_show]}'")
                 else:
                      ui_manager.display_error(f"alias: {name_to_show}: not found")
            continue # Handled internally

        if cmd_lower == 'unalias':
            if not args: ui_manager.display_error("unalias: missing alias name")
            else:
                name_to_remove = args[0]
                if name_to_remove in aliases:
                    del aliases[name_to_remove]
                    ui_manager.display_info(f"Alias '{name_to_remove}' removed.")
                else:
                     ui_manager.display_error(f"unalias: {name_to_remove}: not found")
            continue # Handled internally

        if cmd_lower == 'export':
            if not args: ui_manager.display_error("export: invalid format. Use export NAME=VALUE")
            elif '=' in args[0]:
                try:
                    name, value = args[0].split('=', 1)
                    if value.startswith("'") and value.endswith("'"): value = value[1:-1]
                    elif value.startswith('"') and value.endswith('"'): value = value[1:-1]
                    # Expand any existing vars within the value before setting
                    expanded_value = os.path.expandvars(value)
                    shell_environment[name] = expanded_value
                    ui_manager.display_info(f"Exported '{name}'.")
                except ValueError:
                    ui_manager.display_error("export: invalid format. Use export NAME=VALUE")
            else: # Handle 'export NAME' (print value if exists?)
                 name_to_export = args[0]
                 if name_to_export in shell_environment:
                      # TODO: Decide if 'export NAME' should print or just mark for export (bash behavior)
                      ui_manager.display_info(f"{name_to_export}={shell_environment[name_to_export]}")
                 else:
                      ui_manager.display_error(f"export: variable '{name_to_export}' not found.")
                 # For now, require NAME=VALUE format for setting
                 # ui_manager.display_error("export: invalid format. Use export NAME=VALUE")
            continue # Handled internally

        if cmd_lower == 'unset':
            if not args: ui_manager.display_error("unset: missing variable name")
            else:
                name_to_remove = args[0]
                if name_to_remove in shell_environment:
                    del shell_environment[name_to_remove]
                    ui_manager.display_info(f"Unset '{name_to_remove}'.")
                else:
                    ui_manager.display_warning(f"unset: variable '{name_to_remove}' not found.")
            continue # Handled internally

        # --- Try Translation/Simulation ---
        execute_external = True
        final_command_str = None
        needs_elevation = False # Initialize elevation flag

        # Pass the actual command and args (post-alias) to the translator
        # Expect a tuple: (result_string | None, needs_elevation: bool)
        try:
            translation_result, needs_elevation = command_translator.process_command(command, args)
        except Exception as e:
             ui_manager.display_error(f"Critical error during command processing: {e}")
             import traceback; traceback.print_exc()
             continue # Skip this command

        # --- Process Translation Result ---
        if isinstance(translation_result, str):
            if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                execute_external = False
                needs_elevation = False # Simulations run inline
            elif translation_result.startswith(NO_EXEC_MARKER):
                 execute_external = False
                 needs_elevation = False # No execution planned
            else:
                # Successful translation to PowerShell command
                final_command_str = translation_result
                ui_manager.console.print(f"[dim]Translated: {final_command_str}[/dim]")
        elif translation_result is None:
            # No translation -> Treat as native command (use the processed_input)
            final_command_str = processed_input
            # Native commands run non-elevated by default via this mechanism
            needs_elevation = False
        else:
            # This case should ideally not be reached if process_command is robust
            ui_manager.display_error(f"Internal error: Unexpected result type from translator: {type(translation_result)}")
            execute_external = False
            needs_elevation = False

        # --- Handle Elevation Request ---
        if execute_external and needs_elevation and final_command_str:
            ui_manager.display_warning(f"Command '{command}' may require Administrator privileges.")
            confirm = ui_manager.console.input("Attempt to run elevated? (A UAC prompt will appear) [Y/N]: ")
            if confirm.lower() == 'y':
                ui_manager.display_info("Requesting elevation...")
                ui_manager.display_warning("Output will appear in a new window.")
                try:
                    # Encode the PowerShell command to avoid quoting/newline issues in ArgumentList
                    # Ensure the command ends with a newline for safety if it's complex? No, handled by PS.
                    command_to_elevate = final_command_str + '; Read-Host -Prompt "Press Enter to close this window"'
                    # Optionally remove the pause at the end:
                    # command_to_elevate = final_command_str

                    encoded_command = base64.b64encode(command_to_elevate.encode('utf-16le')).decode('ascii')
                    # Construct the command to launch elevated PowerShell
                    elevate_cmd = f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"'

                    # Run the elevation request using the *non-elevated* helper
                    stdout_elev, stderr_elev, code_elev = command_translator._run_powershell_command(
                        elevate_cmd,
                        env=shell_environment # Pass environment for Start-Process itself
                    )

                    if code_elev != 0:
                        # Common error code 740 means user cancelled UAC or lacked permissions
                        if code_elev == 740:
                             ui_manager.display_error(f"Elevation failed (Error code: {code_elev} - UAC cancelled or insufficient privileges).")
                        else:
                             ui_manager.display_error(f"Failed to request elevation (Error code: {code_elev}).")
                        if stderr_elev: ui_manager.display_error(f"Stderr: {stderr_elev}")
                    # Don't display stdout_elev as it's usually empty for Start-Process

                except Exception as e:
                    ui_manager.display_error(f"Error during elevation attempt: {e}")
                # Prevent non-elevated execution attempt below
                execute_external = False
            else:
                ui_manager.display_info("Elevation cancelled. Command not executed.")
                execute_external = False # Prevent non-elevated execution attempt below

        # --- Execute External Command (Non-Elevated or Native) ---
        if execute_external and final_command_str:
            ui_manager.console.print(f"[dim]Executing (non-elevated): {final_command_str}[/dim]")

            # Use the helper function, passing the current shell environment
            stdout_res, stderr_res, return_code = command_translator._run_powershell_command(
                final_command_str,
                env=shell_environment
            )

            # Display output
            ui_manager.display_output(stdout_res, stderr_res)

            # Optionally display return code if non-zero and no specific error message
            if return_code != 0:
                 # Check if stderr already contains a clear error message
                 has_stderr_msg = stderr_res and not stderr_res.isspace()
                 # Check for common access denied error within stderr if possible
                 is_access_denied = "Access is denied" in str(stderr_res) or "[WinError 5]" in str(stderr_res)

                 if is_access_denied:
                      ui_manager.display_error(f"Command failed with Access Denied (Code {return_code}).")
                      ui_manager.display_info("This command might require elevation. Try running Swodnil as Administrator or check if the specific command needs elevation support.")
                 elif not has_stderr_msg:
                     # Only show generic exit code if no specific stderr was printed
                     ui_manager.display_error(f"Command exited with code {return_code}")
                 # else: stderr already displayed the error message


# --- Main entry point ---
if __name__ == "__main__":
    # Better to run via swodnil.py which sets up UI first
    print("Please run Swodnil via the main 'swodnil.py' script.")