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

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from rich.panel import Panel # For help display
from rich.text import Text   # For help display

import ui_manager
import command_translator

SIMULATION_MARKER_PREFIX = command_translator.SIMULATION_MARKER_PREFIX
NO_EXEC_MARKER = command_translator.NO_EXEC_MARKER
HELP_MARKER_PREFIX = command_translator.HELP_MARKER_PREFIX

APP_DATA_DIR = os.getenv('APPDATA')
SWODNIL_CONFIG_DIR = os.path.join(APP_DATA_DIR, "Swodnil") if APP_DATA_DIR else None
ALIAS_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "aliases.json") if SWODNIL_CONFIG_DIR else None
HISTORY_FILE_PATH = os.path.join(SWODNIL_CONFIG_DIR, "history.txt") if SWODNIL_CONFIG_DIR else None

def _save_aliases(aliases_to_save: dict):
    if not ALIAS_FILE_PATH:
        ui_manager.display_warning("Cannot save aliases: APPDATA environment variable not found.")
        return
    try:
        config_dir = os.path.dirname(ALIAS_FILE_PATH)
        if not os.path.exists(config_dir): os.makedirs(config_dir, exist_ok=True)
        with open(ALIAS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(aliases_to_save, f, indent=4, sort_keys=True)
    except Exception as e: ui_manager.display_error(f"Failed to save aliases to {ALIAS_FILE_PATH}: {e}")

class SwodnilCompleter(Completer):
    def __init__(self, aliases: dict, translation_map: dict):
        self.aliases = aliases
        self.commands = set(['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset'])
        self.commands.update(aliases.keys())
        self.commands.update(translation_map.keys())
        self.command_options = {"--help", "-h"}

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        if not word_before_cursor and not text_before_cursor.endswith(' '): word_before_cursor = ''
        
        # Rudimentary check for first word based on spaces before cursor
        # This needs to be improved by parsing the line up to the cursor, respecting quotes and operators,
        # to determine if the current word is truly the start of a new command segment.
        is_first_word_in_segment_heuristic = not text_before_cursor.lstrip().startswith(word_before_cursor) or \
                                             ' ' not in text_before_cursor.lstrip() or \
                                             text_before_cursor.endswith(' ') or \
                                             text_before_cursor.rfind('|') > text_before_cursor.rfind(word_before_cursor) or \
                                             text_before_cursor.rfind(';') > text_before_cursor.rfind(word_before_cursor) or \
                                             text_before_cursor.rfind('&&') > text_before_cursor.rfind(word_before_cursor)


        if is_first_word_in_segment_heuristic:
            for cmd in sorted(list(self.commands)):
                if cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor), display_meta="Command")
        elif word_before_cursor.startswith('-'):
             line_parts_heuristic = text_before_cursor.strip().split()
             if line_parts_heuristic and line_parts_heuristic[0] in self.commands: # Check if first word is a known command
                for option in self.command_options:
                    if option.startswith(word_before_cursor):
                        yield Completion(option, start_position=-len(word_before_cursor), display_meta="Option")
        elif word_before_cursor or text_before_cursor.endswith(' '):
            path_to_complete = word_before_cursor; base_dir = '.'
            try:
                 if path_to_complete.startswith('~'): path_to_complete = os.path.expanduser(path_to_complete)
                 
                 current_working_dir = os.getcwd()
                 # Determine base_dir for completion
                 if os.path.isabs(path_to_complete):
                     base_dir = os.path.dirname(path_to_complete)
                     partial_name = os.path.basename(path_to_complete)
                 else: # Relative path
                     potential_base = os.path.dirname(os.path.join(current_working_dir, path_to_complete))
                     if os.path.isdir(potential_base):
                         base_dir = potential_base
                         partial_name = os.path.basename(path_to_complete)
                     else: # Likely just a partial name in the current directory
                         base_dir = current_working_dir
                         partial_name = path_to_complete
                 
                 if not os.path.isdir(base_dir): return # Cannot list if base_dir is not a directory

                 for item in os.listdir(base_dir):
                      if item.startswith(partial_name):
                            # Construct path that will be inserted
                            # If completing from '.', make it just 'item' or 'item/'
                            # If completing from a path, make it 'path/item'
                            completion_prefix = ""
                            if base_dir != current_working_dir or os.sep in path_to_complete or \
                               (os.altsep and os.altsep in path_to_complete):
                                # If base_dir is not CWD, or if user was typing a path, keep the path context
                                # This logic needs to be robust for how `start_position` works
                                # For now, let's assume word_before_cursor is the part to replace
                                pass # The start_position logic should handle this correctly.

                            full_path_for_stat = os.path.join(base_dir, item)
                            completion_text = item # What gets displayed and potentially completed
                            
                            # Adjust completion_text to include path if original word had path separators
                            # This makes prompt_toolkit replace the typed path prefix correctly.
                            # If word_before_cursor contains path separators, we assume user is typing a path.
                            if os.sep in word_before_cursor or (os.altsep and os.altsep in word_before_cursor):
                                completion_text = os.path.join(os.path.dirname(word_before_cursor), item)


                            is_dir = False
                            try:
                                if os.path.isdir(full_path_for_stat): is_dir = True; completion_text += os.sep
                            except OSError: pass
                            yield Completion(completion_text, start_position=-len(word_before_cursor), display=item, display_meta="Directory" if is_dir else "File")
            except Exception: pass

class Separator(Enum): PIPE = auto(); AND = auto(); SEMICOLON = auto(); BACKGROUND = auto()

def parse_command_line(line: str) -> list[tuple[str, Separator | None]]:
    segments = []; current_segment = ""; in_single_quotes = False; in_double_quotes = False; escaped = False; i = 0; n = len(line)
    while i < n:
        char = line[i]; next_char = line[i+1] if i + 1 < n else None
        if char == "'" and not escaped: in_single_quotes = not in_single_quotes; current_segment += char; i += 1
        elif char == '"' and not escaped: in_double_quotes = not in_double_quotes; current_segment += char; i += 1
        elif char == '\\' and not escaped: escaped = True; current_segment += char; i += 1
        elif not in_single_quotes and not in_double_quotes and not escaped:
            separator = None; increment = 1
            if char == '|': separator = Separator.PIPE
            elif char == '&' and next_char == '&': separator = Separator.AND; increment = 2
            elif char == ';': separator = Separator.SEMICOLON
            elif char == '&':
                 is_trailing = all(line[j].isspace() for j in range(i + 1, n))
                 if is_trailing: separator = Separator.BACKGROUND; increment = n
                 else: current_segment += char
            else: current_segment += char
            if separator:
                segment_to_add = current_segment.strip()
                if segment_to_add: segments.append((segment_to_add, separator))
                current_segment = ""; i += increment; escaped = False
            else: escaped = False; i += 1
        else: current_segment += char; escaped = False; i += 1
    last_segment = current_segment.strip()
    if last_segment: segments.append((last_segment, None))
    return [(cmd, sep) for cmd, sep in segments if cmd]


def run_shell():
    default_aliases: dict[str, str] = {'ll': 'ls -l', 'la': 'ls -la', 'l': 'ls -CF'}
    aliases = default_aliases.copy()
    if ALIAS_FILE_PATH and os.path.exists(ALIAS_FILE_PATH):
        try:
            with open(ALIAS_FILE_PATH, 'r', encoding='utf-8') as f: loaded_aliases = json.load(f); aliases.update(loaded_aliases)
        except Exception as e: ui_manager.display_warning(f"Could not load aliases: {e}")
    shell_environment = copy.deepcopy(os.environ)
    if HISTORY_FILE_PATH:
        try: os.makedirs(os.path.dirname(HISTORY_FILE_PATH), exist_ok=True); history = FileHistory(HISTORY_FILE_PATH)
        except OSError as e: ui_manager.display_warning(f"Could not create history directory: {e}"); history = None
    else: history = None
    swodnil_completer = SwodnilCompleter(aliases, command_translator.TRANSLATION_MAP)
    session = PromptSession(history=history, auto_suggest=AutoSuggestFromHistory(), completer=swodnil_completer, complete_while_typing=True, reserve_space_for_menu=6)
    command_history_list: list[str] = list(session.history.get_strings()) if history else []
    background_jobs = {}; next_job_id = 1

    while True:
        try:
            try: cwd = os.getcwd()
            except OSError: cwd = "[dim]?[/dim]"
            prompt_message = ui_manager.get_prompt_string(cwd)
            raw_input_line = session.prompt(prompt_message, rprompt="Swodnil")
            if raw_input_line.strip(): command_history_list.append(raw_input_line)
        except KeyboardInterrupt: continue
        except EOFError: break
        if not raw_input_line.strip(): continue

        try: parsed_commands = parse_command_line(raw_input_line)
        except Exception as e: ui_manager.display_error(f"Command line parsing error: {e}"); continue
        if not parsed_commands: continue
        
        is_single_command_segment = len(parsed_commands) == 1
        if is_single_command_segment:
            single_command_str, single_separator = parsed_commands[0]
            is_background_builtin_attempt = (single_separator == Separator.BACKGROUND)
            processed_single_command_str = single_command_str
            potential_alias_parts = single_command_str.split(maxsplit=1)
            potential_alias = potential_alias_parts[0]
            if potential_alias in aliases:
                 alias_expansion = aliases[potential_alias]
                 remaining_args_str = potential_alias_parts[1] if len(potential_alias_parts) > 1 else ''
                 processed_single_command_str = f"{alias_expansion} {remaining_args_str}".strip()
                 if single_command_str != processed_single_command_str : ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_single_command_str}[/dim]")
            current_command_name_for_check = processed_single_command_str.split(maxsplit=1)[0].lower()
            if is_background_builtin_attempt and current_command_name_for_check in ['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset']:
                 ui_manager.display_error(f"Built-in command '{current_command_name_for_check}' cannot be run in the background.")
                 continue
            try:
                 parts = shlex.split(processed_single_command_str, posix=False)
                 if parts:
                      command = parts[0]; args = parts[1:]; cmd_lower = command.lower()
                      builtins = ['help', 'exit', 'quit', 'cd', 'history', 'alias', 'unalias', 'export', 'unset']
                      if cmd_lower in builtins:
                          # (Built-in command logic as previously defined - unchanged)
                          last_return_code_builtin = 0 
                          if cmd_lower == 'help': ui_manager.display_help_page()
                          elif cmd_lower in ['exit', 'quit']: raise EOFError 
                          elif cmd_lower == 'cd':
                              target_dir = os.path.expanduser("~") if not args else args[0]
                              try: expanded_target_dir = os.path.expandvars(target_dir); os.chdir(expanded_target_dir); shell_environment['PWD'] = os.getcwd()
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
                              if not args: ui_manager.display_list([f"{k}='{v}'" for k,v in sorted(shell_environment.items())], title="Swodnil Environment")
                              elif '=' in args[0]: 
                                  try: name, value = args[0].split('=', 1); value = value.strip("'\""); shell_environment[name] = os.path.expandvars(value); ui_manager.display_info(f"Exported '{name}'.")
                                  except ValueError: ui_manager.display_error("export: invalid format."); last_return_code_builtin = 1
                              else: 
                                  name = args[0]
                                  if name in shell_environment: ui_manager.console.print(f"{name}='{shell_environment[name]}'")
                                  else: ui_manager.display_error(f"export: var '{name}' not found."); last_return_code_builtin = 1
                          elif cmd_lower == 'unset':
                              if not args: ui_manager.display_error("unset: missing operand"); last_return_code_builtin = 1
                              else:
                                  name = args[0]
                                  if name in shell_environment: del shell_environment[name]; ui_manager.display_info(f"Unset '{name}'.")
                                  else: ui_manager.display_warning(f"unset: var '{name}' not found."); 
                          continue 
            except ValueError as e: ui_manager.display_error(f"Input parsing error for built-in: {e}"); continue
            except OSError as e: ui_manager.display_error(f"OS error executing built-in: {e}"); continue

        last_return_code = 0; pipeline_failed_for_and = False
        current_pipeline_segments_translated: list[str] = []
        current_pipeline_original_commands: list[str] = []
        needs_elevation_overall = False

        for cmd_index, (command_str, separator) in enumerate(parsed_commands):
            if pipeline_failed_for_and:
                 if separator == Separator.SEMICOLON: pipeline_failed_for_and = False
                 continue
            processed_command_str = command_str
            can_apply_alias = (cmd_index == 0) or (cmd_index > 0 and parsed_commands[cmd_index-1][1] != Separator.PIPE)
            if can_apply_alias:
                potential_alias_parts = command_str.split(maxsplit=1)
                potential_alias = potential_alias_parts[0]
                if potential_alias in aliases:
                    alias_expansion = aliases[potential_alias]
                    remaining_args_str = potential_alias_parts[1] if len(potential_alias_parts) > 1 else ''
                    processed_command_str = f"{alias_expansion} {remaining_args_str}".strip()
                    if command_str != processed_command_str : ui_manager.console.print(f"[dim]Alias expanded: {potential_alias} -> {processed_command_str}[/dim]")
            try:
                parts = shlex.split(processed_command_str, posix=False)
                if not parts: ui_manager.display_error("Syntax error: Empty command segment."); pipeline_failed_for_and=True; break
                command = parts[0]; args = parts[1:]; current_pipeline_original_commands.append(processed_command_str)
            except ValueError as e: ui_manager.display_error(f"Parsing error for '{processed_command_str}': {e}"); pipeline_failed_for_and=True; break
            
            cmd_lower = command.lower()
            if (len(parsed_commands) > 1 or separator == Separator.PIPE or (cmd_index > 0 and parsed_commands[cmd_index-1][1] == Separator.PIPE)) \
               and cmd_lower in ['help', 'exit', 'quit', 'cd', 'alias', 'unalias', 'export', 'unset', 'history']:
                 ui_manager.display_error(f"Built-in command '{cmd_lower}' is invalid in this complex command sequence.")
                 pipeline_failed_for_and = True; break

            is_segment_simulated_and_standalone_valid = False
            try:
                translation_result, needs_elevation_segment = command_translator.process_command(command, args)
                if needs_elevation_segment: needs_elevation_overall = True
                if needs_elevation_segment and (len(parsed_commands) > 1 or separator == Separator.BACKGROUND or \
                   (cmd_index > 0 and parsed_commands[cmd_index-1][1] == Separator.PIPE) or separator == Separator.PIPE):
                    ui_manager.display_error(f"Elevation for '{command}' is disallowed in pipelines, sequences, or background jobs.")
                    pipeline_failed_for_and = True
                if pipeline_failed_for_and: break

                if isinstance(translation_result, str):
                    if translation_result.startswith(SIMULATION_MARKER_PREFIX):
                        is_problematic_sequence_for_sim = ((len(parsed_commands) > 1 and (separator is not None and separator != Separator.BACKGROUND)) or \
                                                          (cmd_index > 0 and parsed_commands[cmd_index-1][1] == Separator.PIPE))
                        if is_problematic_sequence_for_sim:
                            ui_manager.display_error(f"Simulation '{command}' is invalid in this command sequence context.")
                            pipeline_failed_for_and = True;
                        else: is_segment_simulated_and_standalone_valid = True
                    elif translation_result.startswith(NO_EXEC_MARKER):
                        full_no_exec_content = translation_result[len(NO_EXEC_MARKER):]
                        if full_no_exec_content.startswith(HELP_MARKER_PREFIX):
                            actual_help_text = full_no_exec_content[len(HELP_MARKER_PREFIX):].strip()
                            panel_title = f"Help: {command}"
                            ui_manager.console.print(Panel(Text.from_markup(actual_help_text), title=panel_title, border_style="green", padding=(1,1)))
                        pipeline_failed_for_and = True
                    else: current_pipeline_segments_translated.append(translation_result)
                elif translation_result is None: current_pipeline_segments_translated.append(processed_command_str)
                else: ui_manager.display_error(f"Internal Swodnil error: Unexpected translation result type for '{command}'."); pipeline_failed_for_and = True
            except Exception as e: ui_manager.display_error(f"Error during translation of '{command}': {e}"); import traceback; traceback.print_exc(); pipeline_failed_for_and = True
            if pipeline_failed_for_and: break

            if separator != Separator.PIPE:
                final_command_exec_str = ""
                # --- START REVISED LOGIC for pipeline object/string conversion ---
                processed_segments_for_pipe = []
                if len(current_pipeline_segments_translated) > 0:
                    temp_segments_to_process = list(current_pipeline_segments_translated)
                    i = 0
                    while i < len(temp_segments_to_process):
                        current_segment = temp_segments_to_process[i]
                        processed_segments_for_pipe.append(current_segment)

                        if i < len(temp_segments_to_process) - 1:
                            current_segment_lower = current_segment.lower()
                            next_segment_lower = temp_segments_to_process[i+1].lower()
                            is_gci = "get-childitem" in current_segment_lower
                            is_format_cmd = any(fmt in current_segment_lower for fmt in ["format-table", "format-list", "format-wide", "format-custom"])
                            is_select_string = "select-string" in next_segment_lower

                            if is_select_string:
                                if is_gci and not is_format_cmd:
                                    processed_segments_for_pipe.append("ForEach-Object {$_.Name}")
                                    ui_manager.display_info("[dim](Auto-injected ForEach-Object {$_.Name} for ls|grep)[/dim]")
                                elif is_format_cmd: # This applies if current_segment itself is the format command
                                    processed_segments_for_pipe.append("Out-String -Stream")
                                    ui_manager.display_info("[dim](Auto-injected Out-String -Stream for Format|grep)[/dim]")
                                # Else: Select-String is next, but current is not GCI or Format. Standard pipe.
                        i += 1
                final_command_exec_str = " | ".join(processed_segments_for_pipe)
                # --- END REVISED LOGIC ---
                
                original_cmd_display = " | ".join(current_pipeline_original_commands)
                current_pipeline_segments_translated = [] 
                current_pipeline_original_commands = []
                temp_needs_elevation_overall = needs_elevation_overall
                needs_elevation_overall = False

                if final_command_exec_str and final_command_exec_str.strip():
                    is_background_job = (separator == Separator.BACKGROUND and cmd_index == len(parsed_commands) -1)
                    can_elevate_this = temp_needs_elevation_overall and not is_background_job and \
                                       (len(parsed_commands) == 1 or (separator != Separator.PIPE and separator != Separator.AND))
                    if is_background_job:
                        ui_manager.console.print(f"[dim]Running in background: {original_cmd_display}[/dim]")
                        try:
                            process = subprocess.Popen(['powershell', '-NoProfile', '-Command', final_command_exec_str],
                                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL,
                                                        shell=False, env=shell_environment, creationflags=subprocess.CREATE_NO_WINDOW)
                            process.swodnil_cmd_str = original_cmd_display
                            job_id = next_job_id; background_jobs[job_id] = process; next_job_id += 1
                            ui_manager.console.print(f"[{job_id}] {process.pid} {original_cmd_display}")
                            last_return_code = 0
                        except Exception as e: ui_manager.display_error(f"Failed to start background job: {e}"); last_return_code = 1
                    elif can_elevate_this:
                        ui_manager.display_warning(f"Command '{original_cmd_display}' may require Admin privileges.")
                        confirm = ui_manager.console.input("Attempt to run elevated? [y/N]: ")
                        if confirm.lower() == 'y':
                            try:
                                current_cwd = os.getcwd()
                                script_to_elevate = f"Set-Location -LiteralPath '{current_cwd}'; {final_command_exec_str}"
                                script_to_elevate_with_pause = script_to_elevate + '; Write-Host "`n--- Elevated command finished. ---"; Read-Host -Prompt "Press Enter to close this window"'
                                encoded_command = base64.b64encode(script_to_elevate_with_pause.encode('utf-16le')).decode('ascii')
                                elevate_cmd_args = ["powershell", "-Command", f'Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile", "-EncodedCommand", "{encoded_command}"']
                                elevation_process = subprocess.run(elevate_cmd_args, capture_output=True, text=True, shell=False, env=shell_environment)
                                if elevation_process.returncode != 0: ui_manager.display_error(f"Failed to initiate elevation: {elevation_process.stderr if elevation_process.stderr else elevation_process.stdout}"); last_return_code = elevation_process.returncode
                                else: ui_manager.display_info("Elevated command window launched. Check it for results."); last_return_code = 0
                            except Exception as e: ui_manager.display_error(f"Error during elevation attempt: {e}"); last_return_code = 1
                        else: ui_manager.display_info("Elevation cancelled by user."); last_return_code = 1
                    else:
                        ui_manager.console.print(f"[dim]Executing: {final_command_exec_str}[/dim]")
                        current_pipeline_return_code = -1
                        try:
                            output_generator = command_translator._run_powershell_command(final_command_exec_str, env=shell_environment)
                            for line_content, is_stderr_line, exit_code_from_stream in output_generator:
                                if line_content is not None: ui_manager.display_streamed_output(line_content, is_stderr_line)
                                elif exit_code_from_stream is not None: current_pipeline_return_code = exit_code_from_stream
                            last_return_code = current_pipeline_return_code
                            if last_return_code != 0 and current_pipeline_return_code != -1:
                                 if last_return_code == 5: ui_manager.display_info("Hint: Exit code 5 (Access Denied) may indicate Admin privileges needed.")
                        except KeyboardInterrupt: ui_manager.display_warning("\nCommand interrupted by user (Ctrl+C)."); last_return_code = 130
                        except Exception as e: ui_manager.display_error(f"Unexpected error during command execution: {e}"); last_return_code = 1
                elif is_segment_simulated_and_standalone_valid: last_return_code = 0

                if separator == Separator.AND and last_return_code != 0: pipeline_failed_for_and = True
                elif separator == Separator.SEMICOLON: pipeline_failed_for_and = False
        
        completed_jobs_ids = []
        for job_id, process_obj in background_jobs.items():
             if process_obj.poll() is not None:
                 completed_jobs_ids.append(job_id); rc = process_obj.returncode
                 cmd_display_str = getattr(process_obj, 'swodnil_cmd_str', 'Background Command')
                 status_msg = "Done" if rc == 0 else f"Exit {rc}"
                 ui_manager.console.print(f"\n[{job_id}]+ {status_msg}\t{cmd_display_str}")
        for job_id in completed_jobs_ids: del background_jobs[job_id]

if __name__ == "__main__":
    print("Please run Swodnil via the main 'swodnil.py' script.")