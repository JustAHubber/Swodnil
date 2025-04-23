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

# --- ENUM for Separator Types ---
from enum import Enum, auto

# Constants from command_translator
SIMULATION_MARKER_PREFIX = command_translator.SIMULATION_MARKER_PREFIX
NO_EXEC_MARKER = command_translator.NO_EXEC_MARKER

# --- Configuration File Paths ---
# ... (Paths remain the same) ...
APP_DATA_DIR = os.getenv('APPDATA')
SWODNIL_CONFIG_DIR = os.path.join(APP_DATA_DIR, "Swodnil") if APP_DATA_DIR else None
ALIAS_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "aliases.json") if SWODNIL_CONFIG_DIR else None
HISTORY_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "history.txt") if SWODNIL_CONFIG_DIR else None

class Separator(Enum):
    PIPE = auto()        # |
    AND = auto()         # &&
    SEMICOLON = auto()   # ;
    BACKGROUND = auto()  # Trailing &

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


# --- Updated Pipeline Parsing Function ---
def parse_command_line(line: str) -> list[tuple[str, Separator | None]]:
    """
    Parses a command line into segments and their following separators.
    Handles basic quoting and recognizes |, &&, ;, and trailing &.
    Returns a list of tuples: [(command_segment, next_separator), ...].
    The last segment's separator will be BACKGROUND or None.
    """
    segments = []
    current_segment = ""
    in_single_quotes = False
    in_double_quotes = False
    escaped = False
    i = 0
    n = len(line)
    separator = None

    while i < n:
        char = line[i]
        next_char = line[i+1] if i + 1 < n else None
        next_next_char = line[i+2] if i + 2 < n else None

        if char == "'" and not escaped:
            in_single_quotes = not in_single_quotes
            current_segment += char
            i += 1
        elif char == '"' and not escaped:
            in_double_quotes = not in_double_quotes
            current_segment += char
            i += 1
        elif char == '\\' and not escaped:
            escaped = True
            # Handle escaped char by adding both backslash and next char
            if next_char:
                current_segment += char + next_char
                i += 2
            else: # Dangling escape at end
                current_segment += char
                i += 1
        elif not in_single_quotes and not in_double_quotes and not escaped:
            # Check for separators
            if char == '|':
                separator = Separator.PIPE
                segments.append((current_segment.strip(), separator))
                current_segment = ""
                i += 1
            elif char == '&' and next_char == '&':
                separator = Separator.AND
                segments.append((current_segment.strip(), separator))
                current_segment = ""
                i += 2 # Skip both '&'
            elif char == ';':
                separator = Separator.SEMICOLON
                segments.append((current_segment.strip(), separator))
                current_segment = ""
                i += 1
            elif char == '&' and (next_char is None or next_char.isspace()):
                 # Check if it's a trailing & for background
                 is_trailing = True
                 for j in range(i + 1, n):
                     if not line[j].isspace():
                         is_trailing = False
                         break
                 if is_trailing:
                     separator = Separator.BACKGROUND
                     # Don't add segment yet, just note background and break loop
                     break # End parsing here, '&' consumed
                 else: # It's a literal '&' in the command
                    current_segment += char
                    i += 1
            else: # Regular character
                current_segment += char
                escaped = False
                i += 1
        else: # Inside quotes or escaped character
            current_segment += char
            escaped = False
            i += 1

    # Add the last segment (if any)
    last_segment = current_segment.strip()
    if last_segment:
        # Determine the separator for the last segment (BACKGROUND or None)
        final_separator = Separator.BACKGROUND if separator == Separator.BACKGROUND else None
        segments.append((last_segment, final_separator))

    # Filter out potentially empty segments created by adjacent separators etc.
    segments = [(cmd, sep) for cmd, sep in segments if cmd]

    return segments


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
                 command_history_list.append(raw_input_line)

        except KeyboardInterrupt: continue
        except EOFError: break

        if not raw_input_line.strip():
            continue

        # --- Parse Command Line into Segments and Separators ---
        try:
            parsed_commands = parse_command_line(raw_input_line)
            if not parsed_commands: continue
        except Exception as e:
            ui_manager.display_error(f"Command line parsing error: {e}")
            continue

        # --- Group Commands by Pipelines ---
        # A pipeline is a sequence of commands linked by Separator.PIPE
        pipelines: list[list[tuple[str, Separator | None]]] = []
        current_pipeline: list[tuple[str, Separator | None]] = []
        last_separator = None

        for command_str, separator in parsed_commands:
            current_pipeline.append((command_str, separator))
            if separator != Separator.PIPE:
                pipelines.append(current_pipeline)
                current_pipeline = [] # Start a new pipeline group
            last_separator = separator # Track the separator *after* the pipeline

        # If the loop ended mid-pipeline (shouldn't happen if parse_command_line is correct)
        # or the last command wasn't followed by ;, &&, or &
        if current_pipeline:
             pipelines.append(current_pipeline)


        # --- Execute Pipelines Sequentially ---
        last_return_code = 0 # Track return code for && operator
        pipeline_failed = False

        for i, pipeline in enumerate(pipelines):
            pipeline_str_segments = [cmd for cmd, sep in pipeline]
            # Determine the separator *following* this pipeline group
            # It's the separator of the *last* command in this pipeline group
            pipeline_separator = pipeline[-1][1]

            # --- Conditional Execution (&&) ---
            if i > 0 and pipelines[i-1][-1][1] == Separator.AND:
                if last_return_code != 0:
                    # Skip this pipeline and subsequent && pipelines
                    pipeline_failed = True
                    break # Stop processing further pipelines in this line

            if pipeline_failed: continue # Skip if previous && failed


            # --- Translate Segments within the Pipeline ---
            translated_pipeline_segments = []
            any_segment_failed = False
            any_needs_elevation = False
            is_builtin_pipeline = False # Flag if a built-in was encountered

            for seg_idx, (segment_str, _) in enumerate(pipeline):
                 processed_segment_str = segment_str
                 # Apply alias ONLY to the first word of the first segment of the *entire line*
                 if i == 0 and seg_idx == 0:
                      potential_alias = segment_str.split(maxsplit=1)[0]
                      if potential_alias in aliases:
                          alias_expansion = aliases[potential_alias]
                          remaining_args = segment_str.split(maxsplit=1)[1] if ' ' in segment_str else ''
                          processed_segment_str = f"{alias_expansion} {remaining_args}".strip()
                          ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_segment_str}[/dim]")

                 # Parse individual segment
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

                 # Check for Built-ins
                 cmd_lower = command.lower()
                 is_valid_pipeline_cmd = True
                 if cmd_lower in ['help', 'exit', 'quit', 'cd', 'alias', 'unalias', 'export', 'unset']:
                     is_builtin_pipeline = True # Mark that a built-in was found
                     # Allow 'history' in pipelines, disallow others
                     if cmd_lower != 'history':
                         ui_manager.display_error(f"Built-in command '{cmd_lower}' cannot be used in pipelines.")
                         any_segment_failed = True; break
                     # If history, treat it like a normal command for translation/execution

                 # Translate the segment (if not an invalid built-in)
                 try:
                     translation_result, needs_elevation = command_translator.process_command(command, args)
                     if needs_elevation:
                         any_needs_elevation = True
                         # Elevation not allowed in pipelines or background
                         if len(pipeline) > 1 or pipeline_separator == Separator.BACKGROUND:
                             ui_manager.display_error(f"Command '{command}' requires elevation, not supported in pipelines or background jobs.")
                             any_segment_failed = True; break

                     if isinstance(translation_result, str):
                         if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                             ui_manager.display_error(f"Simulation command '{command}' cannot be used in pipelines or background.")
                             any_segment_failed = True; break
                         elif translation_result.startswith(NO_EXEC_MARKER):
                             any_segment_failed = True; break # Error message already shown
                         else: translated_pipeline_segments.append(translation_result)
                     elif translation_result is None: # Native command
                         translated_pipeline_segments.append(processed_segment_str)
                     else: # Unexpected result
                         ui_manager.display_error(f"Internal error: Unexpected translator result for '{command}': {type(translation_result)}")
                         any_segment_failed = True; break
                 except Exception as e:
                      ui_manager.display_error(f"Critical error processing segment '{segment_str}': {e}")
                      import traceback; traceback.print_exc()
                      any_segment_failed = True; break

            # If any segment in the pipeline failed, stop processing this line
            if any_segment_failed:
                pipeline_failed = True # Ensure subsequent && blocks are skipped
                break # Stop processing further pipelines

            # Handle single-segment built-ins here if needed (e.g., if not a pipeline but was marked is_builtin_pipeline)
            if is_builtin_pipeline and len(pipeline) == 1:
                 # The only allowed built-in here is 'history'
                 cmd_lower = shlex.split(pipeline[0][0])[0].lower()
                 if cmd_lower == 'history':
                     ui_manager.display_list(command_history_list, title="Command History")
                     last_return_code = 0 # History succeeded
                 else: # Should not happen if checks above are correct
                     ui_manager.display_error("Internal error: Invalid built-in reached execution.")
                     last_return_code = 1
                 continue # Move to next pipeline/command

            # --- Construct and Execute Pipeline ---
            final_pipeline_command_str = " | ".join(translated_pipeline_segments)
            is_background_job = (pipeline_separator == Separator.BACKGROUND)

            # Handle Elevation (only possible if single command in pipeline and not background)
            if any_needs_elevation and not is_background_job:
                # ... (Elevation logic using final_pipeline_command_str - SAME AS BEFORE) ...
                # ... This section requests elevation via UAC ...
                ui_manager.display_warning(f"Command '{shlex.split(pipeline[0][0])[0]}' may require Administrator privileges.")
                confirm = ui_manager.console.input("Attempt to run elevated? (A UAC prompt will appear) [y/N]: ")
                if confirm.lower() == 'y':
                    # ... (Full elevation request logic with Start-Process -Verb RunAs) ...
                     try:
                         command_to_elevate = final_pipeline_command_str + '; Read-Host -Prompt "Press Enter to close window"'
                         encoded_command = base64.b64encode(command_to_elevate.encode('utf-16le')).decode('ascii')
                         elevate_cmd = f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"'
                         stdout_elev, stderr_elev, code_elev = command_translator._run_powershell_command_batch(elevate_cmd, env=shell_environment)
                         if code_elev != 0:
                             if code_elev == 740: ui_manager.display_error(f"Elevation failed (Code: {code_elev} - UAC cancelled or insufficient privileges).")
                             else: ui_manager.display_error(f"Failed to request elevation (Code: {code_elev}).")
                             if stderr_elev: ui_manager.display_error(f"Stderr: {stderr_elev}")
                         last_return_code = code_elev # Store elevation attempt result? Or assume 0 if success?
                     except Exception as e:
                         ui_manager.display_error(f"Error during elevation attempt: {e}"); import traceback; traceback.print_exc()
                         last_return_code = 1 # Mark as failed
                else:
                    ui_manager.display_info("Elevation cancelled. Command not executed.")
                    last_return_code = 1 # Command did not run
                continue # Skip non-elevated execution for this pipeline


            # Execute Non-Elevated Pipeline (Foreground or Background)
            elif final_pipeline_command_str:
                 if is_background_job:
                     # --- Execute Background Job ---
                     # ... (Background execution using Popen - SAME AS BEFORE) ...
                     ui_manager.console.print(f"[dim]Running in background: {final_pipeline_command_str}[/dim]")
                     try:
                         process = subprocess.Popen(
                             ['powershell', '-NoProfile', '-Command', final_pipeline_command_str],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False, env=shell_environment)
                         job_id = next_job_id; background_jobs[job_id] = process; next_job_id += 1
                         ui_manager.console.print(f"[{job_id}] {process.pid}")
                         last_return_code = 0 # Background launch success assumed for && check
                     except Exception as e:
                         ui_manager.display_error(f"Failed to start background job: {e}"); import traceback; traceback.print_exc()
                         last_return_code = 1 # Background launch failed
                 else:
                     # --- Execute Foreground Job (Streaming) ---
                     # ... (Foreground streaming execution using _run_powershell_command - SAME AS BEFORE) ...
                     ui_manager.console.print(f"[dim]Executing: {final_pipeline_command_str}[/dim]")
                     current_pipeline_return_code = -1
                     try:
                         output_generator = command_translator._run_powershell_command(final_pipeline_command_str, env=shell_environment)
                         for line, is_stderr, code in output_generator:
                             if line is not None: ui_manager.display_streamed_output(line, is_stderr)
                             elif code is not None: current_pipeline_return_code = code
                         # Store the result of this foreground pipeline
                         last_return_code = current_pipeline_return_code
                         if last_return_code != 0:
                             ui_manager.display_error(f"Command finished with exit code {last_return_code}")
                             if last_return_code == 5: ui_manager.display_info("Hint: Exit code 5 often means 'Access Denied'.")
                     except KeyboardInterrupt:
                         ui_manager.display_warning("\nCommand interrupted.")
                         last_return_code = 130 # Standard code for Ctrl+C interrupt
                     except Exception as e:
                         ui_manager.display_error(f"Error during command execution: {e}"); import traceback; traceback.print_exc()
                         last_return_code = 1 # Generic failure code


        # --- Check for completed background jobs ---
        # ... (Check and print completed jobs - SAME AS BEFORE) ...
        completed_jobs = []
        for job_id, process in background_jobs.items():
            if process.poll() is not None:
                completed_jobs.append(job_id)
                rc = process.returncode
                # Attempt to reconstruct command - fragile
                cmd_approx = process.args[-1] if isinstance(process.args, list) and process.args else 'Unknown Command'
                ui_manager.console.print(f"[{job_id}]+ Done (Exit code: {rc})\t{cmd_approx}")
        for job_id in completed_jobs: del background_jobs[job_id]


# --- Main entry point ---
if __name__ == "__main__":
    print("Please run Swodnil via the main 'swodnil.py' script.")