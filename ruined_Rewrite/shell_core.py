# shell_core.py
# Contains the main REPL, command execution logic, state management, and completion.

import os
import subprocess
import shlex
import copy # For deep copying environment
import base64 # For encoding elevated commands
import json # For reading/writing aliases
import glob # For path completion
import re # Potentially needed for parsing refinement
from enum import Enum, auto # For separator types

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
APP_DATA_DIR = os.getenv('APPDATA')
SWODNIL_CONFIG_DIR = os.path.join(APP_DATA_DIR, "Swodnil") if APP_DATA_DIR else None
ALIAS_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "aliases.json") if SWODNIL_CONFIG_DIR else None
HISTORY_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "history.txt") if SWODNIL_CONFIG_DIR else None

# --- Helper Function for Saving Aliases ---
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
class SwodnilCompleter(Completer):
    def __init__(self, aliases: dict, translation_map: dict):
        self.aliases = aliases
        self.commands = set(['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset'])
        self.commands.update(aliases.keys())
        self.commands.update(translation_map.keys())

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        if not word_before_cursor and not text_before_cursor.endswith(' '):
             word_before_cursor = '' # Handle completion when cursor is at end of non-space char

        # Determine context: first word of a segment or an argument/path
        last_separator_pos = -1
        in_quotes = False
        escaped = False
        # Simple check for start of segment - needs refinement for quotes/escapes
        for i, char in reversed(list(enumerate(text_before_cursor))):
             # Basic quote/escape handling needed here for accuracy
             # This logic needs improvement for robustness
             if char in ['|', ';', '&'] and not in_quotes and not escaped: # Rough check
                 # Check for &&
                 if char == '&' and i > 0 and text_before_cursor[i-1] == '&':
                      last_separator_pos = i -1 # Position before &&
                 else:
                      last_separator_pos = i
                 break
        current_segment_text = text_before_cursor[last_separator_pos+1:]
        is_first_word_in_segment = not current_segment_text.strip().startswith(word_before_cursor) and ' ' not in current_segment_text.strip()

        if is_first_word_in_segment or (last_separator_pos == -1 and ' ' not in text_before_cursor.strip()):
            # Command Completion
            for cmd in sorted(list(self.commands)):
                if cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor), display_meta=f"Command")
        elif word_before_cursor or text_before_cursor.endswith(' '): # Allow path completion after space
            # Path Completion (Basic)
            path_to_complete = word_before_cursor
            base_dir = '.' # Default to current directory

            try:
                 # Expand ~
                 if path_to_complete.startswith('~'):
                      path_to_complete = os.path.expanduser(path_to_complete)

                 # Separate directory part from partial filename/dirname
                 if os.sep in path_to_complete or (os.altsep and os.altsep in path_to_complete):
                      base_dir = os.path.dirname(path_to_complete)
                      partial_name = os.path.basename(path_to_complete)
                 else:
                      partial_name = path_to_complete

                 if not base_dir: base_dir = '.'
                 if not os.path.isdir(base_dir): return

                 # List directory and match against partial name
                 for item in os.listdir(base_dir):
                      if item.startswith(partial_name):
                            full_path = os.path.join(base_dir, item)
                            display_text = item
                            completion_text = full_path
                            is_dir = False
                            try:
                                if os.path.isdir(full_path):
                                    is_dir = True
                                    completion_text += os.sep
                            except OSError: pass

                            yield Completion(
                                completion_text,
                                start_position=-len(word_before_cursor),
                                display=display_text,
                                display_meta="Directory" if is_dir else "File"
                            )
            except Exception: pass


# --- ENUM for Separator Types ---
class Separator(Enum):
    PIPE = auto()        # |
    AND = auto()         # &&
    SEMICOLON = auto()   # ;
    BACKGROUND = auto()  # Trailing &

# --- Updated Pipeline Parsing Function ---
def parse_command_line(line: str) -> list[tuple[str, Separator | None]]:
    """
    Parses a command line into segments and their following separators.
    Handles basic quoting/escaping and recognizes |, &&, ;, and trailing &.
    Returns a list of tuples: [(command_segment, separator_after_segment), ...].
    The last segment's separator will be BACKGROUND or None.
    """
    segments = []
    current_segment = ""
    in_single_quotes = False
    in_double_quotes = False
    escaped = False
    i = 0
    n = len(line)

    while i < n:
        char = line[i]
        next_char = line[i+1] if i + 1 < n else None

        if char == "'" and not escaped:
            in_single_quotes = not in_single_quotes; current_segment += char; i += 1
        elif char == '"' and not escaped:
            in_double_quotes = not in_double_quotes; current_segment += char; i += 1
        elif char == '\\' and not escaped:
            escaped = True; current_segment += char; i += 1 # Keep escape for now
        elif not in_single_quotes and not in_double_quotes and not escaped:
            separator = None
            increment = 1
            if char == '|': separator = Separator.PIPE
            elif char == '&' and next_char == '&': separator = Separator.AND; increment = 2
            elif char == ';': separator = Separator.SEMICOLON
            elif char == '&':
                 is_trailing = True
                 for j in range(i + 1, n):
                     if not line[j].isspace(): is_trailing = False; break
                 if is_trailing: separator = Separator.BACKGROUND; increment = n
                 else: current_segment += char # Treat as literal '&'
            else: current_segment += char

            if separator:
                segment_to_add = current_segment.strip()
                if segment_to_add: segments.append((segment_to_add, separator))
                current_segment = ""
                i += increment
                escaped = False # Reset escape state after operator
            else: # No separator found, just move to next char
                 escaped = False
                 i += 1
        else: # Inside quotes or escaped character
            current_segment += char
            escaped = False
            i += 1

    # Add the last segment if non-empty
    last_segment = current_segment.strip()
    if last_segment:
        last_separator = Separator.BACKGROUND if 'separator' in locals() and separator == Separator.BACKGROUND else None
        segments.append((last_segment, last_separator))

    segments = [(cmd, sep) for cmd, sep in segments if cmd]
    return segments


# --- Main Shell Function ---
def run_shell():
    """Runs the main Read-Evaluate-Print Loop (REPL) for Swodnil."""
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
    background_jobs = {}
    next_job_id = 1

    while True:
        # 1. Read Input
        try:
            try: cwd = os.getcwd()
            except OSError: cwd = "[dim]?[/dim]"
            prompt_message = ui_manager.get_prompt_string(cwd)
            raw_input_line = session.prompt(prompt_message, rprompt="Swodnil")
            if raw_input_line.strip(): command_history_list.append(raw_input_line)
        except KeyboardInterrupt: continue # Catch Ctrl+C during prompt
        except EOFError: break # Catch Ctrl+D/Ctrl+Z during prompt
        if not raw_input_line.strip(): continue

        # 2. Parse Command Line
        try:
            parsed_commands = parse_command_line(raw_input_line)
            if not parsed_commands: continue
        except Exception as e: ui_manager.display_error(f"Command line parsing error: {e}"); continue

        # --- Check for Single Built-in Command FIRST ---
        is_single_command = len(parsed_commands) == 1
        if is_single_command:
            single_command_str, single_separator = parsed_commands[0]
            is_background_builtin_attempt = (single_separator == Separator.BACKGROUND)

            if is_background_builtin_attempt:
                 # No need to parse, just show error
                 try: cmd_name = shlex.split(single_command_str)[0] # Get command name if possible
                 except: cmd_name = "Built-in"
                 ui_manager.display_error(f"{cmd_name} command cannot be run in the background.")
                 continue # Skip to next prompt

            # Apply alias if it's the single command
            processed_single_command_str = single_command_str
            potential_alias = single_command_str.split(maxsplit=1)[0]
            if potential_alias in aliases:
                 alias_expansion = aliases[potential_alias]
                 remaining_args = single_command_str.split(maxsplit=1)[1] if ' ' in single_command_str else ''
                 processed_single_command_str = f"{alias_expansion} {remaining_args}".strip()
                 ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_single_command_str}[/dim]")

            # --- Try block specifically for parsing/executing single built-ins ---
            try:
                 parts = shlex.split(processed_single_command_str)
                 if parts:
                      command = parts[0]; args = parts[1:]; cmd_lower = command.lower()
                      builtins = ['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset']
                      if cmd_lower in builtins:
                          # --- Execute Built-in ---
                          last_return_code = 0 # Default to success for builtins unless error
                          if cmd_lower == 'help': ui_manager.display_help_page()
                          elif cmd_lower in ['exit', 'quit']: raise EOFError # Signal loop exit cleanly
                          elif cmd_lower == 'cd':
                              target_dir = os.path.expanduser("~") if not args else args[0]
                              try: expanded_target_dir = os.path.expandvars(target_dir); os.chdir(expanded_target_dir); shell_environment['PWD'] = os.getcwd()
                              except Exception as e: ui_manager.display_error(f"cd failed: {e}"); last_return_code = 1
                          elif cmd_lower == 'history': ui_manager.display_list(command_history_list, title="Command History")
                          elif cmd_lower == 'alias':
                              if not args: ui_manager.display_list([f"{n}='{c}'" for n, c in sorted(aliases.items())], title="Aliases")
                              elif '=' in args[0]:
                                  try: n, c = args[0].split('=', 1); c = c.strip("'\""); aliases[n] = c; swodnil_completer.commands.add(n); ui_manager.display_info(f"Alias '{n}' set."); _save_aliases(aliases)
                                  except ValueError: ui_manager.display_error("alias: invalid format."); last_return_code = 1
                              else: n = args[0]; ui_manager.console.print(f"alias {n}='{aliases[n]}'") if n in aliases else ui_manager.display_error(f"alias: {n}: not found"); last_return_code = 0 if n in aliases else 1
                          elif cmd_lower == 'unalias':
                              if not args: ui_manager.display_error("unalias: missing name"); last_return_code = 1
                              else: n = args[0];
                              if n in aliases: del aliases[n]; swodnil_completer.commands.discard(n); ui_manager.display_info(f"Alias '{n}' removed."); _save_aliases(aliases)
                              else: ui_manager.display_error(f"unalias: {n}: not found"); last_return_code = 1
                          elif cmd_lower == 'export':
                              if not args: ui_manager.display_error("export: invalid format."); last_return_code = 1
                              elif '=' in args[0]:
                                  try: n, v = args[0].split('=', 1); v = v.strip("'\""); shell_environment[n] = os.path.expandvars(v); ui_manager.display_info(f"Exported '{n}'.")
                                  except ValueError: ui_manager.display_error("export: invalid format."); last_return_code = 1
                              else: n = args[0]; ui_manager.display_info(f"{n}={shell_environment[n]}") if n in shell_environment else ui_manager.display_error(f"export: var '{n}' not found."); last_return_code = 0 if n in shell_environment else 1
                          elif cmd_lower == 'unset':
                              if not args: ui_manager.display_error("unset: missing name"); last_return_code = 1
                              else: n = args[0];
                              if n in shell_environment: del shell_environment[n]; ui_manager.display_info(f"Unset '{n}'.")
                              else: ui_manager.display_warning(f"unset: var '{n}' not found."); last_return_code = 0
                          # If it was a built-in, skip rest of loop for this input line
                          continue # Go to next prompt iteration

            # --- CORRECTED Exception Handling for Single Built-in Check ---
            except ValueError as e: # Catch shlex parsing errors
                 ui_manager.display_error(f"Input parsing error: {e}")
                 continue # Skip rest of loop for this input
            except OSError as e: # Catch potential OS errors from cd etc.
                 ui_manager.display_error(f"OS error executing built-in: {e}")
                 continue # Skip rest of loop
            # --- Let EOFError and KeyboardInterrupt propagate ---
            # --- End Single Built-in Check ---


        # --- If not a handled single built-in, proceed with pipeline/external command execution ---
        last_return_code = 0
        pipeline_failed_for_and = False
        current_pipeline_segments_translated: list[str] = []
        current_pipeline_original_commands: list[str] = []
        needs_elevation_overall = False # Track if elevation needed for the whole sequence

        for cmd_index, (command_str, separator) in enumerate(parsed_commands):

            # --- Conditional Execution Check (&&) ---
            if pipeline_failed_for_and:
                 if separator == Separator.SEMICOLON: pipeline_failed_for_and = False
                 continue

            # --- Process Segment (Alias, Parse, Translate) ---
            processed_command_str = command_str
            if cmd_index == 0: # Apply alias only to first command of the line
                potential_alias = command_str.split(maxsplit=1)[0]
                if potential_alias in aliases:
                    alias_expansion = aliases[potential_alias]
                    remaining_args = command_str.split(maxsplit=1)[1] if ' ' in command_str else ''
                    processed_command_str = f"{alias_expansion} {remaining_args}".strip()
                    ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_command_str}[/dim]")

            try: # Parse
                parts = shlex.split(processed_command_str)
                if not parts: ui_manager.display_error("Syntax error: Empty command segment."); pipeline_failed_for_and=True; break
                command = parts[0]; args = parts[1:]
                current_pipeline_original_commands.append(processed_command_str) # Store original
            except ValueError as e: ui_manager.display_error(f"Parsing error: {e}"); pipeline_failed_for_and=True; break

            # Check disallowed built-ins in complex sequences
            cmd_lower = command.lower()
            if len(parsed_commands) > 1 and cmd_lower in ['help', 'exit', 'quit', 'cd', 'alias', 'unalias', 'export', 'unset']:
                 ui_manager.display_error(f"Built-in '{cmd_lower}' invalid in complex command sequences.")
                 pipeline_failed_for_and = True; break

            # Translate
            try:
                translation_result, needs_elevation_segment = command_translator.process_command(command, args)
                if needs_elevation_segment:
                    needs_elevation_overall = True # Mark if any part needs elevation
                    if len(parsed_commands) > 1 or separator == Separator.BACKGROUND:
                        ui_manager.display_error(f"Elevation for '{command}' disallowed in sequences/background.")
                        pipeline_failed_for_and = True; break

                if isinstance(translation_result, str):
                    if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                        ui_manager.display_error(f"Simulation '{command}' invalid in sequences/background.")
                        pipeline_failed_for_and = True; break
                    elif translation_result.startswith(NO_EXEC_MARKER):
                        pipeline_failed_for_and = True; break
                    else: current_pipeline_segments_translated.append(translation_result)
                elif translation_result is None: current_pipeline_segments_translated.append(processed_command_str)
                else: ui_manager.display_error("Internal translator error."); pipeline_failed_for_and = True; break
            except Exception as e: ui_manager.display_error(f"Translation error: {e}"); pipeline_failed_for_and = True; break

            if pipeline_failed_for_and: break # Stop processing line if segment failed

            # --- Execute assembled pipeline if separator is NOT PIPE ---
            if separator != Separator.PIPE:
                final_command_exec_str = " | ".join(current_pipeline_segments_translated)
                original_cmd_display = " | ".join(current_pipeline_original_commands)
                current_pipeline_segments_translated = [] # Reset for next group
                current_pipeline_original_commands = []

                if final_command_exec_str:
                    is_background_job = (separator == Separator.BACKGROUND)
                    can_elevate_this = needs_elevation_overall and len(parsed_commands) == 1 and not is_background_job

                    if is_background_job:
                        # --- Execute Background ---
                        ui_manager.console.print(f"[dim]Running in background: {original_cmd_display}[/dim]")
                        try:
                            process = subprocess.Popen(['powershell', '-NoProfile', '-Command', final_command_exec_str],
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False, env=shell_environment)
                            # Store original command with Popen object for job display
                            process.swodnil_cmd_str = original_cmd_display
                            job_id = next_job_id; background_jobs[job_id] = process; next_job_id += 1
                            ui_manager.console.print(f"[{job_id}] {process.pid} {original_cmd_display}")
                            last_return_code = 0
                        except Exception as e: ui_manager.display_error(f"Failed to start job: {e}"); last_return_code = 1
                    elif can_elevate_this:
                        # --- Handle Elevation ---
                        ui_manager.display_warning(f"Command '{command}' may require Admin privileges.")
                        confirm = ui_manager.console.input("Attempt to run elevated? [y/N]: ")
                        if confirm.lower() == 'y':
                            try:
                                command_to_elevate = final_command_exec_str + '; Read-Host -Prompt "Press Enter to close window"'
                                encoded_command = base64.b64encode(command_to_elevate.encode('utf-16le')).decode('ascii')
                                elevate_cmd = f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"'
                                _, _, code_elev = command_translator._run_powershell_command_batch(elevate_cmd, env=shell_environment)
                                last_return_code = code_elev
                                if code_elev != 0: ui_manager.display_error(f"Elevation failed (Code: {code_elev}).")
                            except Exception as e: ui_manager.display_error(f"Error elevating: {e}"); last_return_code = 1
                        else: ui_manager.display_info("Elevation cancelled."); last_return_code = 1
                    else:
                        # --- Execute Foreground ---
                        ui_manager.console.print(f"[dim]Executing: {final_command_exec_str}[/dim]")
                        current_pipeline_return_code = -1
                        try:
                            output_generator = command_translator._run_powershell_command(final_command_exec_str, env=shell_environment)
                            for line, is_stderr_line, code in output_generator: # Renamed 'code' -> 'is_stderr_line', 'final_code' -> 'code'
                                if line is not None: ui_manager.display_streamed_output(line, is_stderr_line)
                                elif code is not None: current_pipeline_return_code = code
                            last_return_code = current_pipeline_return_code
                            if last_return_code != 0:
                                ui_manager.display_error(f"Command finished with exit code {last_return_code}") # Always show code
                                if last_return_code == 5: ui_manager.display_info("Hint: Exit code 5 often means 'Access Denied'.")
                        except KeyboardInterrupt: ui_manager.display_warning("\nCommand interrupted."); last_return_code = 130
                        except Exception as e: ui_manager.display_error(f"Execution error: {e}"); last_return_code = 1

                # Check for && condition failure *after* executing this group
                if separator == Separator.AND and last_return_code != 0:
                     pipeline_failed_for_and = True
                # Reset failure flag if separator is ;
                if separator == Separator.SEMICOLON:
                     pipeline_failed_for_and = False


        # --- Check for completed background jobs ---
        completed_jobs = []
        for job_id, process in background_jobs.items():
             if process.poll() is not None:
                 completed_jobs.append(job_id)
                 rc = process.returncode
                 cmd_approx = getattr(process, 'swodnil_cmd_str', 'Background Command') # Get stored command
                 ui_manager.console.print(f"\n[{job_id}]+ Done (Exit code: {rc})\t{cmd_approx}")
        for job_id in completed_jobs: del background_jobs[job_id]


# --- Main entry point ---
if __name__ == "__main__":
    print("Please run Swodnil via the main 'swodnil.py' script.")