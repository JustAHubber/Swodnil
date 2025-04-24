# shell_core.py
# Contains the main REPL, command execution logic, and state management.

import os
import subprocess
import shlex
import copy # For deep copying environment

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
        # Add default aliases? e.g., ll='ls -l'
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

        if cmd_lower == 'cd':
            if not args: target_dir = os.path.expanduser("~") # Go home
            else: target_dir = args[0]
            try: os.chdir(target_dir)
            except FileNotFoundError: ui_manager.display_error(f"cd: directory not found: {target_dir}")
            except Exception as e: ui_manager.display_error(f"cd: failed to change directory: {e}")
            continue # Handled internally

        if cmd_lower == 'history':
            ui_manager.display_list(command_history, title="Command History")
            continue # Handled internally

        if cmd_lower == 'alias':
            if not args: # Print all aliases
                alias_items = [f"{name}='{cmd}'" for name, cmd in aliases.items()]
                ui_manager.display_list(alias_items, title="Aliases")
            elif '=' in args[0]: # Define alias (basic parsing)
                try:
                    name, cmd = args[0].split('=', 1)
                    # Remove surrounding quotes if present from cmd part
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
                    # Remove surrounding quotes if present
                    if value.startswith("'") and value.endswith("'"): value = value[1:-1]
                    elif value.startswith('"') and value.endswith('"'): value = value[1:-1]
                    shell_environment[name] = value
                    ui_manager.display_info(f"Exported '{name}'.")
                except ValueError:
                    ui_manager.display_error("export: invalid format. Use export NAME=VALUE")
            else: # Handle 'export NAME' (maybe print value if exists?) - or require =
                 ui_manager.display_error("export: invalid format. Use export NAME=VALUE")
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

        # Pass the actual command and args (post-alias) to the translator
        processing_result = command_translator.process_command(command, args)

        if isinstance(processing_result, str):
            if processing_result.startswith(SIMULATION_MARKER_PREFIX):
                # Simulation handled internally, no external execution needed
                execute_external = False
            elif processing_result.startswith(NO_EXEC_MARKER):
                 # Command failed translation or guides user, no external execution
                 execute_external = False
            else:
                # Successful translation to PowerShell command
                final_command_str = processing_result
                ui_manager.console.print(f"[dim]Translated: {final_command_str}[/dim]")
        elif processing_result is None:
            # No translation -> Treat as native command (use the processed_input)
            final_command_str = processed_input
            # Check if command *might* exist before trying to run it?
            # _, _, check_code = command_translator._run_powershell_command(f"Get-Command {shlex.quote(command)} -ErrorAction SilentlyContinue")
            # if check_code != 0:
            #    ui_manager.display_error(f"{command}: command not found")
            #    execute_external = False
            # else: pass # Assume it exists
        else:
            ui_manager.display_error(f"Internal error: Unexpected result from translator: {processing_result}")
            execute_external = False

        # --- Execute External Command (if required) ---
        if execute_external and final_command_str:
            ui_manager.console.print(f"[dim]Executing: {final_command_str}[/dim]")

            # Use the helper function, passing the current shell environment
            stdout_res, stderr_res, return_code = command_translator._run_powershell_command(
                final_command_str,
                env=shell_environment
            )

            # Display output
            ui_manager.display_output(stdout_res, stderr_res)

            # Optionally display return code if non-zero and no stderr?
            if return_code != 0 and (not stderr_res or stderr_res.isspace()):
                 ui_manager.display_error(f"Command exited with code {return_code}")


# --- Main entry point ---
if __name__ == "__main__":
    # Better to run via swodnil.py which sets up UI first
    print("Please run Swodnil via the main 'swodnil.py' script.")