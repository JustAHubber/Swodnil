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
                 if is_trailing: separator = Separator.BACKGROUND; increment = n # Consume rest of line for trailing &
                 else: current_segment += char # Treat as literal '&' if not properly trailing
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
        # Check if the very last operator parsed was a background operator
        # This needs to be robust. If 'separator' was set in the loop for the *last* operator
        # and it was BACKGROUND, then this segment's separator is None, but the BACKGROUND
        # applies to the whole line.
        # Let's adjust how background is added. A segment can end with Separator.BACKGROUND only if it's the truly last one.
        is_overall_background = False
        if segments and segments[-1][1] == Separator.BACKGROUND:
            is_overall_background = True
            # Remove the background separator from the last parsed segment, it's a global state for this command group
            segments[-1] = (segments[-1][0], None)


        final_separator_for_this_segment = None
        if is_overall_background and not segments: # Single command ending with &
            final_separator_for_this_segment = Separator.BACKGROUND

        segments.append((last_segment, final_separator_for_this_segment))


    segments = [(cmd, sep) for cmd, sep in segments if cmd] # Clean empty commands again

    # If the original line ended with '&' (and it was parsed as BACKGROUND),
    # the last segment in `segments` might not have Separator.BACKGROUND yet.
    # This ensures the *last* segment correctly indicates the backgrounding.
    # The parser was changed to consume the rest of the line for trailing &,
    # so the last element should already have it or None.

    # Ensure only the very last segment can have Separator.BACKGROUND
    if len(segments) > 1:
        for k in range(len(segments) -1):
            if segments[k][1] == Separator.BACKGROUND:
                # This is an error or misparse, treat as literal & if not truly trailing
                # For now, let's assume parse_command_line handles this by not assigning BACKGROUND unless it's trailing
                pass # Or convert to literal ampersand processing earlier in parse_command_line

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
    background_jobs = {} # Stores Popen objects for background jobs: {job_id: process}
    next_job_id = 1

    while True:
        # 1. Read Input
        try:
            try: cwd = os.getcwd()
            except OSError: cwd = "[dim]?[/dim]" # Handle errors like deleted CWD
            prompt_message = ui_manager.get_prompt_string(cwd)
            # Add rprompt for visual flair or info
            raw_input_line = session.prompt(prompt_message, rprompt="Swodnil")
            if raw_input_line.strip(): command_history_list.append(raw_input_line)
        except KeyboardInterrupt: continue # Ctrl+C at prompt, new prompt
        except EOFError: break # Ctrl+D or Ctrl+Z at prompt, exit shell
        if not raw_input_line.strip(): continue # Empty input

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

            # Prevent built-ins (except potentially some passive ones if designed) from running in background
            if is_background_builtin_attempt:
                 # Temporarily parse to get command name for error message
                 try: temp_parts_for_error = shlex.split(single_command_str, posix=False)
                 except: temp_parts_for_error = None
                 cmd_name_for_error = temp_parts_for_error[0] if temp_parts_for_error else "Built-in"

                 # Allow 'clear &' or 'history &' ? For now, disallow all.
                 # if cmd_name_for_error.lower() not in ['some_allowed_bg_builtin']:
                 ui_manager.display_error(f"Built-in command '{cmd_name_for_error}' cannot be run in the background.")
                 continue # Skip to next prompt iteration

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
                 parts = shlex.split(processed_single_command_str, posix=False)
                 if parts:
                      command = parts[0]; args = parts[1:]; cmd_lower = command.lower()
                      # List of built-in commands
                      builtins = ['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset']
                      if cmd_lower in builtins:
                          # --- Execute Built-in ---
                          last_return_code_builtin = 0 # Default to success for builtins unless error
                          if cmd_lower == 'help': ui_manager.display_help_page()
                          elif cmd_lower in ['exit', 'quit']: raise EOFError # Signal loop exit cleanly
                          elif cmd_lower == 'cd':
                              target_dir = os.path.expanduser("~") if not args else args[0]
                              try:
                                  expanded_target_dir = os.path.expandvars(target_dir) # Expand env vars in path
                                  os.chdir(expanded_target_dir)
                                  shell_environment['PWD'] = os.getcwd() # Update PWD
                              except FileNotFoundError: ui_manager.display_error(f"cd: no such file or directory: {expanded_target_dir}"); last_return_code_builtin = 1
                              except Exception as e: ui_manager.display_error(f"cd failed: {e}"); last_return_code_builtin = 1
                          elif cmd_lower == 'history': ui_manager.display_list(command_history_list, title="Command History")
                          elif cmd_lower == 'alias':
                              if not args: ui_manager.display_list([f"{name}='{cmd_val}'" for name, cmd_val in sorted(aliases.items())], title="Aliases")
                              elif '=' in args[0]:
                                  try: name, cmd_val = args[0].split('=', 1); cmd_val = cmd_val.strip("'\""); aliases[name] = cmd_val; swodnil_completer.commands.add(name); ui_manager.display_info(f"Alias '{name}' set."); _save_aliases(aliases)
                                  except ValueError: ui_manager.display_error("alias: invalid format. Use name='command'"); last_return_code_builtin = 1
                              else: name = args[0]; ui_manager.console.print(f"alias {name}='{aliases[name]}'") if name in aliases else ui_manager.display_error(f"alias: {name}: not found"); last_return_code_builtin = 0 if name in aliases else 1
                          elif cmd_lower == 'unalias':
                              if not args: ui_manager.display_error("unalias: missing operand"); last_return_code_builtin = 1
                              else:
                                  name = args[0]
                                  if name in aliases: del aliases[name]; swodnil_completer.commands.discard(name); ui_manager.display_info(f"Alias '{name}' removed."); _save_aliases(aliases)
                                  else: ui_manager.display_error(f"unalias: {name}: not found"); last_return_code_builtin = 1
                          elif cmd_lower == 'export':
                              if not args or '=' not in args[0]: ui_manager.display_error("export: invalid format. Use NAME=VALUE or export NAME to display."); last_return_code_builtin = 1
                              elif '=' in args[0]:
                                  try: name, value = args[0].split('=', 1); value = value.strip("'\""); shell_environment[name] = os.path.expandvars(value); ui_manager.display_info(f"Exported '{name}'.")
                                  except ValueError: ui_manager.display_error("export: invalid format."); last_return_code_builtin = 1
                              else: # This case should be caught by the first condition, but as a fallback
                                  name = args[0]; ui_manager.display_info(f"{name}={shell_environment[name]}") if name in shell_environment else ui_manager.display_error(f"export: var '{name}' not found."); last_return_code_builtin = 0 if name in shell_environment else 1
                          elif cmd_lower == 'unset':
                              if not args: ui_manager.display_error("unset: missing operand"); last_return_code_builtin = 1
                              else:
                                  name = args[0]
                                  if name in shell_environment: del shell_environment[name]; ui_manager.display_info(f"Unset '{name}'.")
                                  else: ui_manager.display_warning(f"unset: var '{name}' not found (no error)."); last_return_code_builtin = 0 # Unsetting non-existent is not an error in bash

                          # If it was a built-in, set last_return_code and skip rest of loop
                          # For now, 'last_return_code' is not globally used by pipeline yet, but good to have
                          # last_return_code = last_return_code_builtin
                          continue # Go to next prompt iteration

            # --- Exception Handling for Single Built-in Check ---
            except ValueError as e: # Catches shlex parsing errors for the processed_single_command_str
                 ui_manager.display_error(f"Input parsing error for built-in: {e}")
                 continue
            except OSError as e: # Catches potential OS errors from cd etc.
                 ui_manager.display_error(f"OS error executing built-in: {e}")
                 # last_return_code = 1 # Update if using last_return_code for pipeline logic
                 continue
            # Allow EOFError to propagate to exit the main while True loop
            # Allow KeyboardInterrupt to be caught by the main loop's handler
            # --- End Single Built-in Check ---


        # --- If not a handled single built-in, proceed with pipeline/external command execution ---
        last_return_code = 0 # Tracks the exit code of the last executed command/pipeline segment
        pipeline_failed_for_and = False # Flag for '&&' conditional execution
        current_pipeline_segments_translated: list[str] = [] # Holds PS commands for current pipe group
        current_pipeline_original_commands: list[str] = [] # Holds original commands for display
        needs_elevation_overall = False # Tracks if any command in the current execution group needs elevation

        for cmd_index, (command_str, separator) in enumerate(parsed_commands):

            # --- Conditional Execution Check (&&) ---
            if pipeline_failed_for_and:
                 if separator == Separator.SEMICOLON: # Reset for ';'
                     pipeline_failed_for_and = False
                 continue # Skip this command and subsequent ones until ';' or end of line

            # --- Process Segment (Alias, Parse, Translate) ---
            processed_command_str = command_str
            # Alias expansion only for the first command in a pipeline, or any standalone command.
            # If cmd_index == 0, it's definitely the start.
            # If cmd_index > 0, it means there was a previous command. We need to check if the *previous* separator
            # was NOT a pipe. If it was ';', '&&', or initial command, then this new segment can have an alias.
            can_apply_alias = False
            if cmd_index == 0:
                can_apply_alias = True
            elif cmd_index > 0 and parsed_commands[cmd_index-1][1] != Separator.PIPE:
                can_apply_alias = True

            if can_apply_alias:
                potential_alias = command_str.split(maxsplit=1)[0]
                if potential_alias in aliases:
                    alias_expansion = aliases[potential_alias]
                    remaining_args = command_str.split(maxsplit=1)[1] if ' ' in command_str else ''
                    processed_command_str = f"{alias_expansion} {remaining_args}".strip()
                    ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_command_str}[/dim]")

            try: # Parse the (potentially alias-expanded) command string
                parts = shlex.split(processed_command_str, posix=False)
                if not parts: # Empty segment after alias expansion or due to parsing e.g. 'alias x=""' then 'x'
                    ui_manager.display_error("Syntax error: Empty command segment.")
                    pipeline_failed_for_and=True; break
                command = parts[0]; args = parts[1:]
                current_pipeline_original_commands.append(processed_command_str) # Store original for display
            except ValueError as e:
                ui_manager.display_error(f"Parsing error for '{processed_command_str}': {e}")
                pipeline_failed_for_and=True; break # Critical parsing error for this segment

            # Check disallowed built-ins in complex sequences (pipes, &&, ;)
            cmd_lower = command.lower()
            # Stricter check: any built-in in a multi-segment line or piped is usually problematic.
            if (len(parsed_commands) > 1 or separator == Separator.PIPE or (cmd_index > 0 and parsed_commands[cmd_index-1][1] == Separator.PIPE)) \
               and cmd_lower in ['help', 'exit', 'quit', 'cd', 'alias', 'unalias', 'export', 'unset', 'history']:
                 ui_manager.display_error(f"Built-in command '{cmd_lower}' is invalid in this complex command sequence.")
                 pipeline_failed_for_and = True; break

            # Translate
            is_segment_simulated_and_standalone_valid = False # Flag for this segment
            try:
                translation_result, needs_elevation_segment = command_translator.process_command(command, args)
                if needs_elevation_segment:
                    needs_elevation_overall = True # Mark if any part needs elevation for the current group
                    # Check if elevation is allowed in this context
                    if len(parsed_commands) > 1 or separator == Separator.BACKGROUND or \
                       (cmd_index > 0 and parsed_commands[cmd_index-1][1] == Separator.PIPE) or \
                       (separator == Separator.PIPE):
                        ui_manager.display_error(f"Elevation for '{command}' is disallowed in pipelines, sequences, or background jobs.")
                        pipeline_failed_for_and = True; # This will break below

                if pipeline_failed_for_and: break # If elevation check failed, stop this command line

                if isinstance(translation_result, str):
                    if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                        # ... (simulation logic) ...
                        is_segment_simulated_and_standalone_valid = True

                    elif translation_result.startswith(NO_EXEC_MARKER):
                        # --- REVISED HELP DISPLAY LOGIC ---
                        # New convention: NO_EXEC_MARKER + "SWODNIL_HELP_MESSAGE:" + actual_help_text
                        help_marker_convention = "SWODNIL_HELP_MESSAGE:"
                        full_no_exec_content = translation_result[len(NO_EXEC_MARKER):]

                        if full_no_exec_content.startswith(help_marker_convention):
                            actual_help_text = full_no_exec_content[len(help_marker_convention):].strip()
                            from rich.panel import Panel
                            from rich.text import Text
                            panel_title = f"Help: {command}"
                            ui_manager.console.print(
                                Panel(
                                    Text.from_markup(actual_help_text), 
                                    title=panel_title, 
                                    border_style="green",
                                    padding=(1,1) # Adjusted padding
                                )
                            )
                        else:
                            # Original NO_EXEC_MARKER behavior (e.g. error message or guide)
                            # These are often already printed by ui_manager within the translator.
                            # Or if not, the content_after_marker might be a simple message.
                            # For example, chmod might print its own warnings via ui_manager,
                            # then return NO_EXEC_MARKER + "chmod warning displayed".
                            # We don't want to re-print that.
                            # So, if it's not help, we generally do nothing here for NO_EXEC.
                            pass 
                        # --- END OF REVISED HELP DISPLAY LOGIC ---
                        pipeline_failed_for_and = True # Stop further execution for this segment
                    else: # Regular PowerShell command string
                        current_pipeline_segments_translated.append(translation_result)
                elif translation_result is None: # Native command, pass as is
                    current_pipeline_segments_translated.append(processed_command_str)
                else: # Should not happen
                    ui_manager.display_error(f"Internal Swodnil error: Unexpected translation result type for '{command}'.")
                    pipeline_failed_for_and = True

            except Exception as e:
                ui_manager.display_error(f"Error during translation of '{command}': {e}")
                import traceback; traceback.print_exc() # For debugging
                pipeline_failed_for_and = True
            
            if pipeline_failed_for_and: break # Stop processing this command line if translation or checks failed

            # --- Execute assembled pipeline if separator is NOT PIPE ---
            # (or if it's the end of the line, or if a simulation just ran standalone)
            if separator != Separator.PIPE:
                final_command_exec_str = ""
                if not is_segment_simulated_and_standalone_valid or current_pipeline_segments_translated:
                    # If it wasn't a simulation that ran standalone, OR if it was a simulation
                    # preceded by piped commands, build the PS string.
                    final_command_exec_str = " | ".join(current_pipeline_segments_translated)

                original_cmd_display = " | ".join(current_pipeline_original_commands)
                
                # Reset for the next command group (after ;, &&, or background)
                current_pipeline_segments_translated = []
                current_pipeline_original_commands = []
                
                temp_needs_elevation_overall = needs_elevation_overall # Store for this execution group
                needs_elevation_overall = False # Reset for next group


                if final_command_exec_str: # If there's an actual PowerShell command to execute
                    is_background_job = (separator == Separator.BACKGROUND and cmd_index == len(parsed_commands) -1)
                    can_elevate_this = temp_needs_elevation_overall and not is_background_job and \
                                       (len(parsed_commands) == 1 or (separator != Separator.PIPE and separator != Separator.AND and separator != Separator.SEMICOLON))


                    if is_background_job:
                        ui_manager.console.print(f"[dim]Running in background: {original_cmd_display}[/dim]")
                        try:
                            process = subprocess.Popen(['powershell', '-NoProfile', '-Command', final_command_exec_str],
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                                                        shell=False, env=shell_environment, creationflags=subprocess.CREATE_NO_WINDOW)
                            process.swodnil_cmd_str = original_cmd_display # Store original command for job display
                            job_id = next_job_id; background_jobs[job_id] = process; next_job_id += 1
                            ui_manager.console.print(f"[{job_id}] {process.pid} {original_cmd_display}")
                            last_return_code = 0
                        except Exception as e: ui_manager.display_error(f"Failed to start background job: {e}"); last_return_code = 1
                    
                    elif can_elevate_this:
                        ui_manager.display_warning(f"Command '{original_cmd_display}' may require Admin privileges.")
                        confirm = ui_manager.console.input("Attempt to run elevated? [y/N]: ")
                        if confirm.lower() == 'y':
                            try:
                                # Add a pause to keep the elevated window open to see output/errors
                                command_to_elevate = final_command_exec_str + '; Write-Host "`n--- Elevated command finished. ---"; Read-Host -Prompt "Press Enter to close this window"'
                                encoded_command = base64.b64encode(command_to_elevate.encode('utf-16le')).decode('ascii')
                                elevate_cmd_args = [
                                    "powershell", "-Command",
                                    f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"'
                                ]
                                # Run Start-Process itself non-elevated, it will trigger UAC
                                elevation_process = subprocess.run(elevate_cmd_args, capture_output=True, text=True, shell=False, env=shell_environment)
                                if elevation_process.returncode != 0:
                                    ui_manager.display_error(f"Failed to initiate elevation (Start-Process error): {elevation_process.stderr}")
                                    last_return_code = elevation_process.returncode
                                else:
                                    # Cannot get return code of the elevated process directly this way easily
                                    ui_manager.display_info("Elevated command window launched. Check it for results.")
                                    last_return_code = 0 # Assume success of launching
                            except Exception as e: ui_manager.display_error(f"Error during elevation attempt: {e}"); last_return_code = 1
                        else: ui_manager.display_info("Elevation cancelled by user."); last_return_code = 1 # Or some other code for user cancel
                    
                    else: # Regular foreground execution
                        ui_manager.console.print(f"[dim]Executing: {final_command_exec_str}[/dim]")
                        current_pipeline_return_code = -1 # Default for error
                        try:
                            # Use the streaming executor
                            output_generator = command_translator._run_powershell_command(final_command_exec_str, env=shell_environment)
                            for line_content, is_stderr_line, exit_code_from_stream in output_generator:
                                if line_content is not None:
                                    ui_manager.display_streamed_output(line_content, is_stderr_line)
                                elif exit_code_from_stream is not None:
                                    current_pipeline_return_code = exit_code_from_stream
                            
                            last_return_code = current_pipeline_return_code
                            if last_return_code != 0:
                                # ui_manager.display_error(f"Command finished with exit code {last_return_code}") # Already shown usually
                                if last_return_code == 5: # Access Denied
                                    ui_manager.display_info("Hint: Exit code 5 (Access Denied) may indicate need for Admin privileges.")
                        except KeyboardInterrupt:
                            ui_manager.display_warning("\nCommand interrupted by user (Ctrl+C).")
                            last_return_code = 130 # Standard code for SIGINT
                        except Exception as e:
                            ui_manager.display_error(f"Unexpected error during command execution: {e}")
                            last_return_code = 1 # General error

                elif is_segment_simulated_and_standalone_valid: # Only a simulation ran for this group
                    last_return_code = 0 # Assume simulation succeeded if it didn't raise an exception

                # Conditional execution logic based on last_return_code
                if separator == Separator.AND and last_return_code != 0:
                     pipeline_failed_for_and = True
                elif separator == Separator.SEMICOLON: # Reset for ';' regardless of success
                     pipeline_failed_for_and = False
                # If separator is None or BACKGROUND, pipeline_failed_for_and state persists or doesn't matter for next line


        # --- Check for completed background jobs ---
        completed_jobs_ids = []
        for job_id, process_obj in background_jobs.items():
             if process_obj.poll() is not None: # Check if process has terminated
                 completed_jobs_ids.append(job_id)
                 rc = process_obj.returncode
                 cmd_display_str = getattr(process_obj, 'swodnil_cmd_str', 'Background Command')
                 status_msg = "Done" if rc == 0 else f"Exit {rc}"
                 ui_manager.console.print(f"\n[{job_id}]+ {status_msg}\t{cmd_display_str}")
        for job_id in completed_jobs_ids:
            del background_jobs[job_id] # Remove completed job from tracking


# --- Main entry point ---
if __name__ == "__main__":
    # This is typically not run directly, but via swodnil.py
    print("Please run Swodnil via the main 'swodnil.py' script.")