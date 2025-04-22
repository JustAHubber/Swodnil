# shell_core.py
# Contains the main REPL, command execution logic, state management, and completion.

import os
import subprocess
import shlex
import copy # For deep copying environment
import base64 # For encoding elevated commands
import json # For reading/writing aliases
import glob # For path completion
import re # For pipeline parsing

# --- Add prompt_toolkit imports ---
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# --- End prompt_toolkit imports ---

import ui_manager
import command_translator

# Constants from command_translator
SIMULATION_MARKER_PREFIX = command_translator.SIMULATION_MARKER_PREFIX
NO_EXEC_MARKER = command_translator.NO_EXEC_MARKER

# --- Configuration File Paths ---
# ... (Paths remain the same) ...
APP_DATA_DIR = os.getenv('APPDATA')
SWODNIL_CONFIG_DIR = os.path.join(APP_DATA_DIR, "Swodnil") if APP_DATA_DIR else None
ALIAS_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "aliases.json") if SWODNIL_CONFIG_DIR else None
HISTORY_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "history.txt") if SWODNIL_CONFIG_DIR else None

# --- Helper Function for Saving Aliases ---
# ... (_save_aliases function remains the same) ...
def _save_aliases(aliases_to_save: dict):
    """Saves the current aliases to the JSON file."""
    if not ALIAS_FILE_PATH:
        ui_manager.display_warning("Cannot save aliases: APPDATA environment variable not found.")
        return
    try:
        config_dir = os.path.dirname(ALIAS_FILE_PATH)
        dir_existed_before = os.path.exists(config_dir)
        if not dir_existed_before:
            os.makedirs(config_dir, exist_ok=True)
        with open(ALIAS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(aliases_to_save, f, indent=4, sort_keys=True)
        if not dir_existed_before:
             ui_manager.display_warning(
                 f"Created configuration directory and alias file at: {ALIAS_FILE_PATH}"
             )
    except Exception as e:
        ui_manager.display_error(f"Failed to save aliases to {ALIAS_FILE_PATH}: {e}")

# --- Custom Completer for prompt_toolkit ---
# ... (SwodnilCompleter class remains the same) ...
class SwodnilCompleter(Completer):
    def __init__(self, aliases: dict, translation_map: dict):
        self.aliases = aliases
        self.commands = set(['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset'])
        self.commands.update(aliases.keys())
        self.commands.update(translation_map.keys())

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        is_first_word = not text_before_cursor.lstrip().startswith(word_before_cursor) and ' ' not in text_before_cursor.strip()

        # Basic check: Don't offer path completion immediately after pipe or bg operator
        last_char = text_before_cursor.rstrip()[-1:] if text_before_cursor.rstrip() else ''
        if last_char in ['|', '&']:
            is_first_word = True # Treat as first word of next command

        if is_first_word:
            # Command Completion
            for cmd in sorted(list(self.commands)):
                if cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor), display_meta=f"Command")
        elif word_before_cursor: # Only complete paths if there's something to complete
            # Path Completion
            try:
                if word_before_cursor.startswith('~'):
                    expanded_path = os.path.expanduser(word_before_cursor) + "*"
                else:
                    # Handle relative paths by ensuring they match from current dir
                    # If path contains separators, glob needs the full pattern
                    # If no separators, glob relative to cwd
                    if os.sep not in word_before_cursor and '/' not in word_before_cursor :
                        expanded_path = word_before_cursor + "*"
                    else: # Contains separators, treat as potentially longer path
                         expanded_path = word_before_cursor + "*"

                # Need to handle spaces in paths better - glob doesn't directly
                # For now, this works for paths without spaces
                for path in glob.glob(expanded_path):
                    display_text = os.path.basename(path) or path # Handle case where basename is empty (like C:/)
                    completion_text = path # Use the matched path
                    meta = "File"
                    if os.path.isdir(path):
                         meta = "Directory"
                         completion_text += os.sep
                    # Simple quote handling: if original word had quotes, add them back? Complex.
                    # For now, don't add quotes automatically. User needs to quote spaces.
                    yield Completion(completion_text, start_position=-len(word_before_cursor), display=display_text, display_meta=meta)
            except Exception:
                 pass # Ignore completion errors


# --- Pipeline Parsing Function ---
def parse_pipeline(line: str) -> tuple[list[str], bool]:
    """
    Parses a command line into segments based on pipes (|) and checks for background operator (&).
    Handles basic quoting. Returns (list_of_segments, is_background).
    """
    segments = []
    current_segment = ""
    in_single_quotes = False
    in_double_quotes = False
    escaped = False
    is_background = False
    line = line.strip() # Remove leading/trailing whitespace

    # Check for trailing '&' before processing
    if line.endswith('&'):
        # Ensure it's not escaped or quoted
        # Simple check: if the char before & is whitespace, it's likely a background op
        if len(line) > 1 and line[-2].isspace():
            is_background = True
            line = line[:-1].rstrip() # Remove '&' and trailing space
        # More complex check needed for quoted/escaped '&' - skip for now

    for char in line:
        if char == "'" and not escaped:
            in_single_quotes = not in_single_quotes
            current_segment += char
        elif char == '"' and not escaped:
            in_double_quotes = not in_double_quotes
            current_segment += char
        elif char == '|' and not in_single_quotes and not in_double_quotes and not escaped:
            segments.append(current_segment.strip())
            current_segment = ""
        # elif char == '&' and not in_single_quotes and not in_double_quotes and not escaped:
            # Background check moved to the start - ignore '&' within command? Or treat as error?
            # For now, treat '&' mid-command as literal character if not handled above
            # current_segment += char
        elif char == '\\' and not escaped:
            escaped = True
            current_segment += char # Keep the escape char for now, shlex might handle it later?
        else:
            escaped = False
            current_segment += char

    # Add the last segment
    if current_segment.strip():
        segments.append(current_segment.strip())

    # Basic validation: Ensure no empty segments resulting from parsing (e.g., "cmd | | cmd2")
    segments = [seg for seg in segments if seg]

    return segments, is_background


# --- Main Shell Function ---
def run_shell():
    """Runs the main Read-Evaluate-Print Loop (REPL) for Swodnil."""

    # ... (Shell State, Alias loading, Environment Setup) ...
    # ... (Setup prompt_toolkit Session - SwodnilCompleter, history etc.) ...
    default_aliases: dict[str, str] = {'ll': 'ls -l', 'la': 'ls -la'}
    aliases = default_aliases.copy()
    if ALIAS_FILE_PATH and os.path.exists(ALIAS_FILE_PATH):
        try: # Load Aliases
            with open(ALIAS_FILE_PATH, 'r', encoding='utf-8') as f:
                loaded_aliases = json.load(f); aliases.update(loaded_aliases)
        except Exception as e: ui_manager.display_warning(f"Could not load aliases: {e}")
    shell_environment = copy.deepcopy(os.environ)
    if HISTORY_FILE_PATH:
        try: os.makedirs(os.path.dirname(HISTORY_FILE_PATH), exist_ok=True); history = FileHistory(HISTORY_FILE_PATH)
        except OSError as e: ui_manager.display_warning(f"Could not create history directory: {e}"); history = None
    else: history = None
    swodnil_completer = SwodnilCompleter(aliases, command_translator.TRANSLATION_MAP)
    session = PromptSession(history=history, auto_suggest=AutoSuggestFromHistory(), completer=swodnil_completer, complete_while_typing=True, reserve_space_for_menu=6)
    command_history_list: list[str] = list(session.history.get_strings()) if history else []
    background_jobs = {} # Simple dict to store Popen objects: {job_id: Popen_obj}
    next_job_id = 1

    while True:
        # 1. Read Input using prompt_toolkit
        try:
            try: cwd = os.getcwd()
            except OSError: cwd = "[dim]?[/dim]"
            prompt_message = ui_manager.get_prompt_string(cwd)
            raw_input_line = session.prompt(prompt_message, rprompt="Swodnil")
            if raw_input_line.strip():
                 command_history_list.append(raw_input_line) # Add to simple list for 'history' command

        except KeyboardInterrupt: continue # Just show a new prompt line
        except EOFError: break # Exit the main loop

        if not raw_input_line.strip():
            continue

        # --- Pipeline Parsing ---
        try:
            segments, is_background = parse_pipeline(raw_input_line)
            if not segments: continue # Ignore empty pipelines
        except Exception as e:
            ui_manager.display_error(f"Pipeline parsing error: {e}")
            continue

        # --- Process Segments (Translate, Check Elevation) ---
        translated_segments = []
        any_segment_failed = False
        any_needs_elevation = False

        for i, segment_str in enumerate(segments):
            # Apply alias ONLY to the first word of the first segment (simplification)
            # More complex alias handling (e.g., aliases containing pipes) is not handled here.
            processed_segment_str = segment_str
            if i == 0: # Only apply alias to the first command in the pipeline
                 potential_alias = segment_str.split(maxsplit=1)[0]
                 if potential_alias in aliases:
                     alias_expansion = aliases[potential_alias]
                     remaining_args = segment_str.split(maxsplit=1)[1] if ' ' in segment_str else ''
                     processed_segment_str = f"{alias_expansion} {remaining_args}".strip()
                     if i==0: # Only print expansion for the very first command
                          ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_segment_str}[/dim]")

            # Parse the individual segment
            try:
                parts = shlex.split(processed_segment_str)
                if not parts:
                    ui_manager.display_error(f"Pipeline error: Empty command segment found near '{segment_str}'")
                    any_segment_failed = True; break
                command = parts[0]
                args = parts[1:]
            except ValueError as e:
                ui_manager.display_error(f"Input parsing error in segment '{segment_str}': {e}")
                any_segment_failed = True; break

            # --- Handle Built-in Check (Disallow most built-ins in pipeline/bg) ---
            cmd_lower = command.lower()
            is_valid_pipeline_cmd = True
            if cmd_lower in ['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset']:
                # Allow 'cd' maybe? No, dangerous in pipeline.
                # Allow 'history'? Maybe useful? `history | grep ...`
                if cmd_lower != 'history': # Allow history in pipeline
                    is_valid_pipeline_cmd = False
                    # Allow builtins only if it's a single command segment and not background
                    if len(segments) > 1 or is_background:
                         ui_manager.display_error(f"Built-in command '{cmd_lower}' cannot be used in pipelines or background.")
                         any_segment_failed = True; break
                    else: # Single segment, non-background: handle built-in directly
                         # Need to refactor built-in handling slightly
                         pass # Let the built-in logic below handle it if single segment

            # --- Translate the segment ---
            if is_valid_pipeline_cmd: # Skip translation if invalid builtin detected above
                try:
                    translation_result, needs_elevation = command_translator.process_command(command, args)
                    if needs_elevation:
                        any_needs_elevation = True
                        # If elevation needed in pipeline or background, abort early
                        if len(segments) > 1 or is_background:
                             ui_manager.display_error(f"Command '{command}' requires elevation, which is not supported in pipelines or background jobs.")
                             any_segment_failed = True; break

                    if isinstance(translation_result, str):
                        if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                             # Simulations generally shouldn't be in pipelines/background
                             ui_manager.display_error(f"Simulation command '{command}' cannot be used in pipelines or background.")
                             any_segment_failed = True; break
                        elif translation_result.startswith(NO_EXEC_MARKER):
                             # Command failed translation or is a guide
                             any_segment_failed = True; break # Error message already shown by translator
                        else: # Successful translation
                             translated_segments.append(translation_result)
                    elif translation_result is None: # Native command
                         translated_segments.append(processed_segment_str) # Use the processed segment string directly
                    else: # Unexpected result
                         ui_manager.display_error(f"Internal error: Unexpected result type from translator for '{command}': {type(translation_result)}")
                         any_segment_failed = True; break

                except Exception as e:
                     ui_manager.display_error(f"Critical error processing segment '{segment_str}': {e}")
                     import traceback; traceback.print_exc()
                     any_segment_failed = True; break

        # --- Check for Built-ins if it was a single, non-piped command ---
        if not any_segment_failed and len(segments) == 1 and not is_background:
            cmd_lower = shlex.split(segments[0])[0].lower() # Reparse first word
            if cmd_lower == 'help': ui_manager.display_help_page(); continue
            if cmd_lower in ['exit', 'quit']: break
            if cmd_lower == 'cd':
                # CD logic (same as before)
                target_dir = os.path.expanduser("~") if not args else args[0]
                try: expanded_target_dir = os.path.expandvars(target_dir); os.chdir(expanded_target_dir); shell_environment['PWD'] = os.getcwd()
                except FileNotFoundError: ui_manager.display_error(f"cd: directory not found: {expanded_target_dir}")
                except Exception as e: ui_manager.display_error(f"cd: failed to change directory to '{expanded_target_dir}': {e}")
                continue
            if cmd_lower == 'history': ui_manager.display_list(command_history_list, title="Command History"); continue
            if cmd_lower == 'alias':
                # Alias logic (same as before, including saving and updating completer)
                if not args: ui_manager.display_list([f"{n}='{c}'" for n, c in sorted(aliases.items())], title="Aliases")
                elif '=' in args[0]:
                    try: n, c = args[0].split('=', 1); c = c.strip("'\""); aliases[n] = c; swodnil_completer.commands.add(n); ui_manager.display_info(f"Alias '{n}' set."); _save_aliases(aliases)
                    except ValueError: ui_manager.display_error("alias: invalid format.")
                else: n = args[0]; ui_manager.console.print(f"alias {n}='{aliases[n]}'") if n in aliases else ui_manager.display_error(f"alias: {n}: not found")
                continue
            if cmd_lower == 'unalias':
                # Unalias logic (same as before, including saving and updating completer)
                if not args: ui_manager.display_error("unalias: missing alias name")
                else: n = args[0]; del aliases[n]; swodnil_completer.commands.discard(n); ui_manager.display_info(f"Alias '{n}' removed."); _save_aliases(aliases) if n in aliases else ui_manager.display_error(f"unalias: {n}: not found")
                continue
            if cmd_lower == 'export':
                 # Export logic (same as before)
                if not args: ui_manager.display_error("export: invalid format.")
                elif '=' in args[0]:
                    try: n, v = args[0].split('=', 1); v = v.strip("'\""); shell_environment[n] = os.path.expandvars(v); ui_manager.display_info(f"Exported '{n}'.")
                    except ValueError: ui_manager.display_error("export: invalid format.")
                else: n = args[0]; ui_manager.display_info(f"{n}={shell_environment[n]}") if n in shell_environment else ui_manager.display_error(f"export: var '{n}' not found.")
                continue
            if cmd_lower == 'unset':
                # Unset logic (same as before)
                if not args: ui_manager.display_error("unset: missing var name")
                else: n = args[0]; del shell_environment[n]; ui_manager.display_info(f"Unset '{n}'.") if n in shell_environment else ui_manager.display_warning(f"unset: var '{n}' not found.")
                continue

        # --- Proceed if no failures and not a handled built-in ---
        if any_segment_failed:
            continue # Skip execution

        # --- Construct Final PowerShell Command ---
        final_command_str = " | ".join(translated_segments)

        # --- Handle Elevation Request (Only if single command, checked earlier) ---
        # This block should only be reachable now if len(segments)==1 and needs_elevation=True
        if any_needs_elevation and not is_background and final_command_str: # Redundant check?
            ui_manager.display_warning(f"Command '{command}' may require Administrator privileges.")
            confirm = ui_manager.console.input("Attempt to run elevated? (A UAC prompt will appear) [y/N]: ")
            if confirm.lower() == 'y':
                ui_manager.display_info("Requesting elevation...")
                ui_manager.display_warning("Output will appear in a new window.")
                try:
                    command_to_elevate = final_command_str + '; Read-Host -Prompt "Press Enter to close window"'
                    encoded_command = base64.b64encode(command_to_elevate.encode('utf-16le')).decode('ascii')
                    elevate_cmd = f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"'
                    stdout_elev, stderr_elev, code_elev = command_translator._run_powershell_command_batch(elevate_cmd, env=shell_environment)
                    if code_elev != 0:
                        if code_elev == 740: ui_manager.display_error(f"Elevation failed (Code: {code_elev} - UAC cancelled or insufficient privileges).")
                        else: ui_manager.display_error(f"Failed to request elevation (Code: {code_elev}).")
                        if stderr_elev: ui_manager.display_error(f"Stderr: {stderr_elev}")
                except Exception as e: ui_manager.display_error(f"Error during elevation attempt: {e}"); import traceback; traceback.print_exc()
            else: ui_manager.display_info("Elevation cancelled. Command not executed.")
            continue # Skip non-elevated execution

        # --- Execute External Command (Pipeline or Single Non-Elevated) ---
        elif final_command_str:
            if is_background:
                # --- Execute Background Job ---
                ui_manager.console.print(f"[dim]Running in background: {final_command_str}[/dim]")
                try:
                    # Launch without waiting, redirect output to avoid terminal clutter? Optional.
                    # For now, let output potentially mix or go nowhere if PS handles it.
                    process = subprocess.Popen(
                        ['powershell', '-NoProfile', '-Command', final_command_str],
                        stdout=subprocess.DEVNULL, # Redirect stdout
                        stderr=subprocess.DEVNULL, # Redirect stderr
                        shell=False,
                        env=shell_environment,
                        # Close fds is generally good practice on Unix, less critical on Windows
                        # close_fds=True,
                        # Prevent window popup on Windows? Seems default for Popen.
                        # creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    job_id = next_job_id
                    background_jobs[job_id] = process # Store the process object
                    next_job_id += 1
                    ui_manager.console.print(f"[{job_id}] {process.pid}") # Print job ID and PID

                except Exception as e:
                    ui_manager.display_error(f"Failed to start background job: {e}")
                    import traceback; traceback.print_exc()

            else:
                # --- Execute Foreground Job (Streaming) ---
                ui_manager.console.print(f"[dim]Executing: {final_command_str}[/dim]")
                final_return_code = -1
                try:
                    output_generator = command_translator._run_powershell_command(
                        final_command_str,
                        env=shell_environment
                    )
                    for line, is_stderr, code in output_generator:
                        if line is not None: ui_manager.display_streamed_output(line, is_stderr)
                        elif code is not None: final_return_code = code

                    if final_return_code != 0:
                         ui_manager.display_error(f"Command finished with exit code {final_return_code}")
                         if final_return_code == 5: ui_manager.display_info("Hint: Exit code 5 often means 'Access Denied'.")

                except KeyboardInterrupt:
                     ui_manager.display_warning("\nCommand interrupted.")
                     # How to kill the PowerShell process started by _run_powershell_command?
                     # The Popen object is inside the generator function. We'd need to modify
                     # _run_powershell_command to somehow expose or kill its child on exception.
                     # For now, the PowerShell process might continue running after Ctrl+C here.
                except Exception as e:
                     ui_manager.display_error(f"Error during command execution: {e}")
                     import traceback; traceback.print_exc()

            # --- Check for completed background jobs ---
            # Simple check after each command - could be done more efficiently
            completed_jobs = []
            for job_id, process in background_jobs.items():
                if process.poll() is not None: # Check if process finished
                    completed_jobs.append(job_id)
                    return_code = process.returncode
                    ui_manager.console.print(f"[{job_id}]+ Done (Exit code: {return_code})\t{process.args[-1]}") # Show command approx
            # Remove completed jobs
            for job_id in completed_jobs:
                del background_jobs[job_id]


# --- Main entry point ---
if __name__ == "__main__":
    print("Please run Swodnil via the main 'swodnil.py' script.")