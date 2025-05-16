# command_translator.py
# Handles translation logic and simulated commands.

import argparse
import os
import shlex
import platform
import time
import datetime
import random
import textwrap
import subprocess
import re # For chmod parsing
import base64 # For elevation encoding
import json # For aliases (though loaded/saved in shell_core)
from typing import Iterator

try:
    import psutil # Required for simulated neofetch, df, top helpers
except ImportError:
    psutil = None

import ui_manager # For displaying errors, warnings, simulation output

# --- Custom ASCII Art ---
LOGAN_ART = r"""
                                                                                                                                                                               
                                                                              +=+=============+++==                                                                            
                                                                       +++++++++++++*********+**+++++====                                                                      
                                                                ++++++++*******************************++====                                                                  
                                                          ++++************************+++++++++++++++********+=====                                                            
                                                       +++***************+++++++++++++++++++++=+==+++++++++*****++++==+                                                        
                                                   ++++***************+*++++++++++++==============++++++++++++********++===                                                    
                                               +++++++*********+++++++++++========================+++++++++++++++++++***+++===                                                 
                                           +++++++=++=++++++++======================================+=========++===+++++++++++====                                             
                                        ==+++++++======+=++==================--------====================================+====++====                                           
                                      ========++=======+++++===============------======================================================                                        
                                    ===============++****#***+++++=========-=======================================++++++++==============                                      
                                  ================+*#%%%%%%%#+++==+++=============================================+****###**++++++=========                                    
                                 ============-----+*#%%%%%@%#+=---=++============================================++##%%%%%%**+====+++======                                    
                                ===========--::::-+*%%%##%@@%*=:::--=======================================------=*%%%%%%%@#*=---==++========                                  
                               ==+=========--:::::+#%%####@@%*=::::--======================================-::::-=*%%%##%@@%*=::--============                                 
                             +++++===========-----+#%%###%@@%+-::::-=========-=============================--:::-=*%%###%@@%*=::::-============                                
                            ++++===============---+#%%###%@%#+-----========-============-====================-::-+#%%###%@@#*-::::-==========++==                              
                           **+++=================+*#%%%%%%%%#======+++====--=-==========-========================+#%%%%%@@%#+-:---============+++                              
                          ***++=================++++++++***++==============-----------==-======----=============++*####%%%#+===============-===++++                            
                        *****++====================+++++===================-----------==-======-------============+++++++++======================++==                          
                       ******+++====------============++++============-==---------------======---------==========+=====+===================---=====++                          
                      ******++======---------=======================-----------------------==-=----------=============+++===+=======------------===+++                         
                      *****++=====-===---------------===========-=------------------------------------------==-===================---------------===+==                        
                     *****+++========---------------------------------------------------------------------------------=========-------------------======                       
                    ****+++============-------------------------------------------------------------------------------------------------------------=====                      
                    ****+++============--------------------------------------------------------------------------------------------------------------=====                     
                   ****+++=============--------------------------------------------------------------------------------------------------------------=====                     
                   ***++++=============---------------------------------------------------------------------------------------------------------------=====                    
                  ***+++++============------------------------------------------------------------------------------------------------------------------===                    
                  *++++===============-------------------------------------------------------------------------------------------------------------------===                   
                 ++++++=============---------------------------------------------------------------------------------------------------------------------===                   
                 ++===============-----------------------------------------------------------------------------------------------------------------------====                  
                 ===============------------------------------------------------------------------------------------------------------------------------==+==                  
                 ===========------------------------==------------------------------------------------------------------------------------------------====+===                 
                 =-=======---------------------========----------------------------------------------------------------------------------------------=========                 
                 =========-----------------==========-=--------------------------------------------------------------------------------------------======++++=                 
                 -======-----------------============-----------------------------------------------------------------------------=====------------=====+++++=                 
                 --====-------------===============-----------------------------------------------------------------------------===========-------======++++++                 
                 --===-----------======++++++=====----------------------------------------------------------------------------=====+=++++====----======+++++++                 
                 ====----------====+++++++++====------------------------------------------------------------------------------=======++++++===========++++++++                 
                 -===-------=====+++++++++====-------------------------------------------------------------------------------------===+++++++++======++++++*++                 
                 ====--========+++++++++===------------------------------------------------------------------------------------------====++++++++++++++++++*++                 
                 =========++*****+++++===-----------------------------------------------------------------------------------------====+++++********++++++++*++                 
                 =======++*********+++++++===--------------------------------------------------------------------------------===+++*******************++++***+                 
                 +++++++**********************++===--=------------------------------------------------------------====+++**************+++++++*****#**********                 
                 +++++++*******+++++++++*************++===-------------------------------------------------===+++***********++++++++++++++++++****##**********                 
                 ++++++*********++++++====++++++++*********++================------===============++++=+++*********+++=============++++++++++***********###***                 
                  +++++++*********++++++++=========---=====+++********************++++++=========++++++++====------===============+++++++++**********#######**                 
                  ++++++++*********++++++++++========---=============================-----------------------------============+++++++++************########**                  
                   +++++++++++++**++++++++++++++++=======----------------------------------------------------==============++++++++++***********###########**                  
                   +++++++++++++++++++++++++=+++=============-------------------------------------------===============+++++++++++++**********#############*                   
                    ++++++++++++++++++++++====================-------------------------------------===============+++++++++++++************###############**                   
                    ++++++++=+++=+===========================-------------------------------================+++++++++++++++**********###############%%#**                    
                     ++++++=======================================---------------------------=================+++++++++++++**********####################*                     
                      =+++++=========================================-------------------================++++=+++++++++++***********######################                      
                       =+++++=========================-===============---------------================++++++++++++++++++********########################**                      
                       ==++**++++==================------===-====-==-------------===================+++++++++++++++++********#########################**                       
                        ===++***+++===========--===-------===-=-===------------===================++++++++++++++++++*******###########################                         
                        ====+*****++++============----------------------===========================++++++++++++++++*******#################%%#######**                         
                         ====++++****+++====================------===============+===========+==+++++++++++++++++********##########################*                           
                          ====++++++++++++=============================================+===+====++++++++++++++***********##############%%###%#%%##**                           
                            ===+++***+++++++=========================+==++++++++++++===========++=++++++++++***********################%%#######**                             
                            =====++++++++++++==============++++++++++++++++++++++++++++++++=+++++++++++***************##################%%#####**                              
                             ====++++++++++++====++++++++++++++++++++++++++++++++++++++++++++++++++++***************#####################%%%##**                               
                              ====++++++++++++==++++++++++++++++++++++++++++++++++++++++++++++++++****************#######################%%%#*                                 
                                ==++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++****************###########################**                                  
                                  ==+++++++++++++++++++++++++++++++++++++++++++++++++++++++********************##########################**                                    
                                   ===++++++++++++++++++++++++++++++++++++++++++++++++***********************######################%####*+                                     
                                      =++++++++++++++++++++++++++++++++++++++++++++++*******************#*############%%%%%%#####%%%##**                                       
                                        +++++++++++++++++++++++++++++++++++++++++++++******************###########%%%%%%%%%%##%%###**                                          
                                          +++++++++++++++++++++++++++++++++++++***+++***************############%%%%%%%%#######%##*                                            
                                           =+++++++***++++++++++++++++++++++********************###############%%%%%%%%##########                                              
                                              +=++*++****************************##############################%%%%%%%%%######                                                 
                                                ===++*********#################################%%###%#####%%%%#%%%%#####***                                                    
                                                     +++*****###############################%%%%%%%%%###%%##%###%###*#                                                         
                                                          ***#####################%%%%###%%%%%%%%%%%##############                                                             
                                                            ++**########%#######%%%%%#%####################****                                                                
                                                                  ###################################**#                                                                       
                                                                             ################                                                                                  
"""

# --- Constants ---
SIMULATION_MARKER_PREFIX = "#SIMULATION_EXEC:"
NO_EXEC_MARKER = "#NO_EXEC:"
HELP_MARKER_PREFIX = "SWODNIL_HELP_MESSAGE:" # For identifying help strings

# --- Argument Parser Error Handling ---
class NonExitingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"Argument Error: {message}")
    def _print_message(self, message, file=None):
        pass # Suppress default error printing

# --- Helper Functions ---
def _run_powershell_command(command: str, env: dict | None = None) -> Iterator[tuple[str | None, bool | None, int | None]]:
    try:
        process = subprocess.Popen(
            ['powershell', '-NoProfile', '-Command', command],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding='utf-8', errors='replace', shell=False, env=env
        )
        if process.stdout:
            for line in process.stdout: yield line.strip(), False, None
        if process.stderr:
            for line in process.stderr: yield line.strip(), True, None
        yield None, None, process.wait()
    except FileNotFoundError:
        yield "PowerShell not found in PATH.", True, -1
        yield None, None, -1
    except Exception as e:
        yield f"Failed to execute PowerShell command: {e}", True, -1
        yield None, None, -1

def _run_powershell_command_batch(command: str, env: dict | None = None) -> tuple[str | None, str | None, int]:
    try:
        process = subprocess.run(
            ['powershell', '-NoProfile', '-Command', command],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            shell=False, check=False, env=env
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except FileNotFoundError: return None, "PowerShell not found in PATH.", -1
    except Exception as e: return None, f"Failed to execute PowerShell command: {e}", -1

def _format_bytes(byte_count: int | None) -> str:
    if byte_count is None: return "N/A"
    if byte_count < 1024: return f"{byte_count} B"
    kib = byte_count / 1024;
    if kib < 1024: return f"{kib:.1f} KiB"
    mib = kib / 1024;
    if mib < 1024: return f"{mib:.1f} MiB"
    gib = mib / 1024; return f"{gib:.2f} GiB"

# --- Translation Functions ---

# === File System ===
def translate_ls(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='ls', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for ls')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-l', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-R', '--recursive', action='store_true')
    parser.add_argument('-t', action='store_true')
    parser.add_argument('-S', action='store_true')
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('paths', nargs='*', default=['.'])
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"ls: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]ls - List directory contents[/bold magenta]
[cyan]Description:[/cyan]
  Lists information about files and directories. Mapped to PowerShell's `Get-ChildItem`.

[cyan]Common Usage:[/cyan]
  ls [options] [path...]

[cyan]Supported Flags (approximate mapping):[/cyan]
  -l              Use a long listing format.
  -a, --all       Do not ignore entries starting with . (Shows hidden files via `-Force` in PS).
  -R, --recursive List subdirectories recursively.
  -t              Sort by modification time, newest first.
  -S              Sort by file size, largest first.
  -r, --reverse   Reverse order while sorting.
  --help, -h      Show this help message.
  [path...]       Specify directory or files to list. Defaults to current directory.

[cyan]Notes:[/cyan]
  - PowerShell's `Get-ChildItem` provides the core functionality.
  - Output formatting for `-l` is an approximation of Linux `ls -l`.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    base_cmd = "Get-ChildItem"; params = []; post_cmds = []
    paths_to_list = parsed_args.paths
    params.extend([shlex.quote(p) for p in paths_to_list])
    if parsed_args.all: params.append("-Force")
    if parsed_args.recursive: params.append("-Recurse")
    sort_prop = None; sort_desc = False
    if parsed_args.t: sort_prop = "LastWriteTime"
    if parsed_args.S: sort_prop = "Length"
    if sort_prop:
        sort_cmd = f"Sort-Object -Property {sort_prop}"
        if not parsed_args.reverse: sort_desc = True
        if sort_desc: sort_cmd += " -Descending"
        post_cmds.append(sort_cmd)
    elif parsed_args.reverse: post_cmds.append("Sort-Object -Property Name -Descending")
    if parsed_args.l:
         format_expression = ('@{N="Mode";E={($_.Mode -replace "-","").PadRight(10)}}, @{N="Owner";E={(Get-Acl $_.FullName).Owner}}, @{N="Size";E={$_.Length}}, @{N="LastWriteTime";E={$_.LastWriteTime.ToString("MMM dd HH:mm")}}, @{N="Name";E={$_.Name}}')
         post_cmds.append(f"Format-Table {format_expression} -AutoSize")
    full_cmd = f"{base_cmd} {' '.join(params)}"
    if post_cmds: full_cmd += " | " + " | ".join(post_cmds)
    return full_cmd, False

def translate_cp(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='cp', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for cp')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-r', '-R', '--recursive', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('source', nargs='*') # Changed to * to handle 'cp --help' with no source/dest
    parser.add_argument('destination', nargs='?') # Changed to ?
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"cp: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]cp - Copy files and directories[/bold magenta]
[cyan]Description:[/cyan]
  Copies files or directories. Mapped to PowerShell's `Copy-Item`.

[cyan]Common Usage:[/cyan]
  cp [options] <source> <destination>
  cp [options] <source_1> <source_2> ... <directory_destination>

[cyan]Supported Flags (approximate mapping):[/cyan]
  -r, -R, --recursive   Copy directories recursively (`-Recurse`).
  -i, --interactive     Prompt before overwrite (uses `-Confirm` in PS, behavior differs significantly).
  -v, --verbose         Explain what is being done (`-Verbose`).
  -f, --force           Attempt to force the copy operation (`-Force`).
  --help, -h            Show this help message.

[cyan]Notes:[/cyan]
  - When copying multiple sources, the destination must be a directory.
  - PowerShell's `-Confirm` is more pervasive than Linux `cp -i`.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.source or not parsed_args.destination:
        return NO_EXEC_MARKER + "cp: missing source or destination operand. Try 'cp --help'.", False

    base_cmd = "Copy-Item"; params = []
    if parsed_args.recursive: params.append("-Recurse")
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    sources_str = ", ".join([f'"{shlex.quote(src)}"' for src in parsed_args.source])
    params.append(f"-Path {sources_str}")
    params.append(f"-Destination {shlex.quote(parsed_args.destination)}")
    if len(parsed_args.source) > 1:
        is_dest_dir_check_ps = f"if (-not (Test-Path -Path {shlex.quote(parsed_args.destination)} -PathType Container)) {{ Write-Error 'cp: target must be a directory when copying multiple files'; exit 1; }} ; "
        final_cmd = f"{is_dest_dir_check_ps} {base_cmd} {' '.join(params)}"
    else: final_cmd = f"{base_cmd} {' '.join(params)}"
    return final_cmd, False

def translate_mv(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='mv', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for mv')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('source', nargs='?') # Optional for help
    parser.add_argument('destination', nargs='?') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"mv: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]mv - Move or rename files and directories[/bold magenta]
[cyan]Description:[/cyan]
  Moves or renames files and directories. Mapped to PowerShell's `Move-Item`.

[cyan]Common Usage:[/cyan]
  mv [options] <source> <destination>

[cyan]Supported Flags (approximate mapping):[/cyan]
  -i, --interactive     Prompt before overwrite (uses `-Confirm` in PS, behavior differs).
  -v, --verbose         Explain what is being done (`-Verbose`).
  -f, --force           Attempt to force the move operation (`-Force`).
  --help, -h            Show this help message.

[cyan]Notes:[/cyan]
  - PowerShell's `Move-Item` handles both moving and renaming.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.source or not parsed_args.destination:
        return NO_EXEC_MARKER + "mv: missing source or destination operand. Try 'mv --help'.", False

    base_cmd = "Move-Item"; params = []
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    params.append(f"-Path {shlex.quote(parsed_args.source)}")
    params.append(f"-Destination {shlex.quote(parsed_args.destination)}")
    return f"{base_cmd} {' '.join(params)}", False

def translate_rm(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='rm', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for rm')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-r', '-R', '--recursive', action='store_true')
    parser.add_argument('-f', '--force', action='store_true')
    parser.add_argument('-i', '--interactive', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('files', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"rm: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]rm - Remove files or directories[/bold magenta]
[cyan]Description:[/cyan]
  Removes (deletes) files or directories. Mapped to PowerShell's `Remove-Item`.

[cyan]Common Usage:[/cyan]
  rm [options] <file_or_directory ...>

[cyan]Supported Flags (approximate mapping):[/cyan]
  -r, -R, --recursive   Remove directories and their contents recursively (`-Recurse`).
  -f, --force           Ignore nonexistent files and arguments, never prompt (`-Force`).
  -i, --interactive     Prompt before every removal (uses `-Confirm` in PS).
  -v, --verbose         Explain what is being done (`-Verbose`).
  --help, -h            Show this help message.

[cyan]Notes:[/cyan]
  - Swodnil includes a safety check against removing drive roots without `-rf`.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.files:
        return NO_EXEC_MARKER + "rm: missing operand. Try 'rm --help'.", False

    base_cmd = "Remove-Item"; params = []
    if parsed_args.recursive: params.append("-Recurse")
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    paths_to_remove = [shlex.quote(f) for f in parsed_args.files]
    params.append(f"-Path {','.join(paths_to_remove)}")
    for f_path in parsed_args.files: # Check before forming command
        abs_path = os.path.abspath(f_path)
        drive = os.path.splitdrive(abs_path)[0].upper() + "\\"
        if abs_path == drive and not (parsed_args.recursive and parsed_args.force):
            ui_manager.display_error(f"rm: Refusing to remove root directory '{abs_path}' without -rf")
            return NO_EXEC_MARKER + "rm protection", False
    return f"{base_cmd} {' '.join(params)}", False

def translate_mkdir(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='mkdir', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for mkdir')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-p', '--parents', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('directories', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"mkdir: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]mkdir - Create directories[/bold magenta]
[cyan]Description:[/cyan]
  Creates directories. Mapped to PowerShell's `New-Item -ItemType Directory`.

[cyan]Common Usage:[/cyan]
  mkdir [options] <directory_name ...>

[cyan]Supported Flags (approximate mapping):[/cyan]
  -p, --parents     Create parent directories as needed (PS `-Force` on `New-Item`).
  -v, --verbose       Print a message for each created directory (`-Verbose`).
  --help, -h        Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.directories:
        return NO_EXEC_MARKER + "mkdir: missing operand. Try 'mkdir --help'.", False

    base_cmd = "New-Item -ItemType Directory"; params = []
    if parsed_args.parents: params.append("-Force")
    if parsed_args.verbose: params.append("-Verbose")
    quoted_dirs = [shlex.quote(d) for d in parsed_args.directories]
    params.append(f"-Path {','.join(quoted_dirs)}")
    return f"{base_cmd} {' '.join(params)}", False

def translate_pwd(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='pwd', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for pwd')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    # pwd does not take other arguments typically
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"pwd: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]pwd - Print working directory[/bold magenta]
[cyan]Description:[/cyan]
  Prints the current working directory. Mapped to PowerShell's `$PWD.Path`.

[cyan]Common Usage:[/cyan]
  pwd

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if remaining_args: # pwd takes no arguments other than its own options (which we don't have many of)
        ui_manager.display_error("pwd: does not support arguments other than --help/-h.")
        return NO_EXEC_MARKER + "pwd failed (has args)", False
    return "Write-Host $PWD.Path", False

def translate_touch(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='touch', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for touch')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('files', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"touch: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]touch - Change file timestamps or create empty files[/bold magenta]
[cyan]Description:[/cyan]
  Updates file timestamps or creates empty files if they don't exist.
  Mapped to `New-Item` (if not exists) and setting `LastWriteTime` in PowerShell.

[cyan]Common Usage:[/cyan]
  touch <file ...>

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (No other Linux flags like -t, -d, -r are currently supported).

[cyan]Notes:[/cyan]
  - Creates an empty file if it doesn't exist.
  - Updates `LastWriteTime` to current time if file exists.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.files:
        return NO_EXEC_MARKER + "touch: missing operand. Try 'touch --help'.", False

    commands = []; timestamp = "Get-Date"
    for file_path_str in parsed_args.files:
        quoted_file = shlex.quote(file_path_str)
        cmd = (f"if (-not (Test-Path {quoted_file})) {{ New-Item -Path {quoted_file} -ItemType File -Force -ErrorAction SilentlyContinue | Out-Null }} else {{ (Get-Item {quoted_file}).LastWriteTime = ({timestamp}) }}")
        commands.append(cmd)
    return " ; ".join(commands), False

def translate_find(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='find', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for find')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('path', nargs='?', default=None) # Path is optional if only help is requested
    parser.add_argument('-name', help='Filter by name (wildcards allowed)')
    parser.add_argument('-iname', help='Case-insensitive name filter')
    parser.add_argument('-type', choices=['f', 'd'], help='Filter by type (f=file, d=directory)')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"find: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]find - Search for files in a directory hierarchy[/bold magenta]
[cyan]Description:[/cyan]
  Searches for files based on criteria. Mapped to `Get-ChildItem` with filters.

[cyan]Common Usage:[/cyan]
  find [path...] [expression]

[cyan]Supported Expressions (basic):[/cyan]
  [path]          Starting directory (defaults to '.' if no other path-like arg given).
  -name <pattern> Filter by name (uses PS `-Filter`).
  -iname <pattern>Case-insensitive name filter (PS `-Filter` often case-insensitive).
  -type f         Find files (`-File` in PS).
  -type d         Find directories (`-Directory` in PS).
  --help, -h      Show this help message.

[cyan]Notes:[/cyan]
  - Basic translation. Advanced `find` features (e.g., -exec, -user, -mtime) are NOT supported.
  - `-Recurse` and `-ErrorAction SilentlyContinue` are used with `Get-ChildItem`.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    start_path = parsed_args.path if parsed_args.path is not None else '.'

    base_cmd = "Get-ChildItem"; params = [f"-Path {shlex.quote(start_path)}", "-Recurse", "-ErrorAction SilentlyContinue"]; post_cmds = []
    name_filter = None
    if parsed_args.name: name_filter = parsed_args.name
    elif parsed_args.iname: name_filter = parsed_args.iname
    if name_filter: params.append(f"-Filter {shlex.quote(name_filter)}")
    if parsed_args.type:
        if parsed_args.type == 'f': params.append("-File")
        elif parsed_args.type == 'd': params.append("-Directory")
    full_cmd = f"{base_cmd} {' '.join(params)}"
    if post_cmds: full_cmd += " | " + " | ".join(post_cmds) # post_cmds not currently used
    return full_cmd, False

# === Permissions ===
def translate_chmod(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='chmod', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for chmod')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-R', '--recursive', action='store_true')
    parser.add_argument('mode', nargs='?') # Optional for help
    parser.add_argument('files', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"chmod: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]chmod - Change file mode bits (approximated)[/bold magenta]
[cyan]Description:[/cyan]
  Changes file permissions. Mapped to PowerShell's `icacls`.
  [bold yellow]WARNING:[/bold yellow] Windows ACLs are fundamentally different from POSIX permissions.
  This translation is EXTREMELY limited, approximate, and often requires elevation.

[cyan]Common Usage:[/cyan]
  chmod [options] <mode> <file ...>

[cyan]Supported Modes (basic mapping):[/cyan]
  Symbolic (e.g., u+x, go-r): Approximated for user, group (Authenticated Users), other (Everyone).
  Numeric (e.g., 755): Very coarsely mapped to `icacls` grants.
  
[cyan]Supported Flags:[/cyan]
  -R, --recursive   Apply recursively (uses `icacls /T`).
  --help, -h        Show this help message.

[cyan]Notes:[/cyan]
  - `icacls` changes usually need Administrator privileges. Best avoided for precise POSIX semantics.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.mode or not parsed_args.files:
        return NO_EXEC_MARKER + "chmod: missing mode or file operand. Try 'chmod --help'.", False
    
    ui_manager.display_warning("chmod translation to icacls is limited/approximate. Elevation typically required.")
    mode_str = parsed_args.mode
    # files_relative = parsed_args.files # Keep original relative list if needed for display/error
    recursive_opt = "/T" if parsed_args.recursive else ""
    commands_templates = [] # Templates for icacls commands
    current_user_ps = "$(whoami)"
    group_sid_map = "Authenticated Users"
    other_sid_map = "Everyone"

    if re.fullmatch(r'^[0-7]{3,4}$', mode_str):
        numeric_mode = mode_str[-3:]
        owner_digit, group_digit, other_digit = [int(d) for d in numeric_mode]
        ui_manager.display_warning(f"Numeric chmod mode '{mode_str}' has a VERY approximate mapping to icacls.")
        perms_map = {7: "F", 6: "M", 5: "RX", 4: "R", 0: "N"} # N for no access (remove)
        
        def add_numeric_perms_template(digit, target_sid):
            perm_char = perms_map.get(digit)
            if perm_char and perm_char != "N":
                commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /grant {target_sid}:({perm_char})")
            elif perm_char == "N" or digit == 0 : # Explicitly remove if 0 or mapped to N
                commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /remove {target_sid}")
            # else: unmapped digit, could warn or ignore
        
        add_numeric_perms_template(owner_digit, current_user_ps)
        add_numeric_perms_template(group_digit, f"'{group_sid_map}'") # Quote SIDs with spaces
        add_numeric_perms_template(other_digit, f"'{other_sid_map}'")
    else: # Symbolic mode
        ops = re.findall(r'([ugoa]*)([+\-=])([rwxXstugo]*)', mode_str)
        if not ops:
            return NO_EXEC_MARKER + f"chmod: Invalid mode string structure: '{mode_str}'", False
        
        for who, op, perms_str in ops:
            if not who: who = 'a' # Default to 'a' if not specified (like +x)
            targets = set()
            if 'u' in who: targets.add(current_user_ps)
            if 'g' in who: targets.add(f"'{group_sid_map}'")
            if 'o' in who: targets.add(f"'{other_sid_map}'")
            if 'a' in who: targets.update([current_user_ps, f"'{group_sid_map}'", f"'{other_sid_map}'"])
            
            # Map r,w,x to icacls permissions. X is complex (execute only if dir or already executable).
            # Simplified: x -> RX.
            ps_perms_list = [] # Build list of simple perms like R, W, X
            if 'r' in perms_str: ps_perms_list.append("R")
            if 'w' in perms_str: ps_perms_list.append("W") 
            if 'x' in perms_str or 'X' in perms_str: ps_perms_list.append("X") # Treat X as x for simplicity

            effective_icacls_perm = ""
            has_r, has_w, has_x = 'R' in ps_perms_list, 'W' in ps_perms_list, 'X' in ps_perms_list

            if has_r and has_w and has_x: effective_icacls_perm = "F" # Full Control
            elif has_r and has_w: effective_icacls_perm = "M"         # Modify
            elif has_r and has_x: effective_icacls_perm = "RX"        # Read & Execute
            elif has_w and has_x: effective_icacls_perm = "(W,X)"     # Write, Execute
            elif has_r: effective_icacls_perm = "R"
            elif has_w: effective_icacls_perm = "W"                   # Write Data
            elif has_x: effective_icacls_perm = "X"                   # Execute File

            if not effective_icacls_perm and perms_str: # e.g. chmod +s (sticky bit etc.)
                ui_manager.display_warning(f"chmod: Permissions '{perms_str}' in mode '{who}{op}{perms_str}' are not fully translated to icacls.")
                continue # Skip this specific permission part

            for target_user_or_sid in targets:
                if op == '+':
                    if effective_icacls_perm:
                        commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /grant {target_user_or_sid}:({effective_icacls_perm})")
                elif op == '-':
                    if effective_icacls_perm: # Deny specific perms
                        commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /deny {target_user_or_sid}:({effective_icacls_perm})")
                    else: # e.g. u- (remove all for user)
                         commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /remove {target_user_or_sid}")
                elif op == '=': # Set exactly these permissions
                    # For '=', typically remove all explicit grants/denies for the target first, then grant the specified.
                    # This is simplified here; /reset is too broad.
                    commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /remove {target_user_or_sid}") # Attempt remove existing explicit ACEs
                    if effective_icacls_perm:
                        commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt} /grant {target_user_or_sid}:({effective_icacls_perm})")
                    # If effective_icacls_perm is empty (e.g. u=), the /remove above handles it.

    if not commands_templates:
        return NO_EXEC_MARKER + "chmod: mode did not translate to any actionable icacls commands.", False

    # Apply command templates to each file using its absolute path
    final_file_commands = []
    for f_path_relative in parsed_args.files:
        abs_f_path = os.path.abspath(f_path_relative)
        quoted_abs_f = shlex.quote(abs_f_path)
        for cmd_template in commands_templates:
            final_file_commands.append(cmd_template.format(file_placeholder=quoted_abs_f))
    
    if not final_file_commands: # Should be redundant if commands_templates check passed, but safety.
        return NO_EXEC_MARKER + "chmod: no executable commands generated for any file.", False
        
    return " ; ".join(final_file_commands), True # Assume elevation needed

def translate_chown(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='chown', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for chown')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-R', '--recursive', action='store_true')
    parser.add_argument('owner_group', nargs='?') # Optional for help
    parser.add_argument('files', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"chown: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]chown - Change file owner and group (approximated)[/bold magenta]
[cyan]Description:[/cyan]
  Changes file owner. Mapped to `icacls /setowner`. Group change is approximated by granting Full Control.
  [bold yellow]WARNING:[/bold yellow] Windows ownership and group concepts differ significantly from POSIX. 
  This translation requires Administrator privileges.

[cyan]Common Usage:[/cyan]
  chown [options] <user[:group]> <file ...>

[cyan]Supported Owner/Group Specification:[/cyan]
  `user`          Attempt to set owner to `user`.
  `user:group`    Set owner to `user` AND grant Full Control (F) to `group` (approximate).
  `user.group`    Same as `user:group`.

[cyan]Supported Flags:[/cyan]
  -R, --recursive   Apply recursively (uses `icacls /T /C`). `/T` applies to files and subfolders.
  --help, -h        Show this help message.

[cyan]Notes:[/cyan]
  - "Group" change is approximated by granting Full Control to the specified group SID. This is not a true POSIX group ownership change.
  - The user/group names must be recognizable by the Windows system (e.g., "Administrator", "BUILTIN\\Users", "DOMAIN\\UserName").
  - All operations require elevation.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.owner_group or not parsed_args.files:
        return NO_EXEC_MARKER + "chown: missing owner/group or file operand. Try 'chown --help'.", False

    ui_manager.display_warning("chown translation is approximate and requires elevation. Ensure user/group names are valid on Windows.")
    
    owner_spec = parsed_args.owner_group
    new_owner = owner_spec # Default: entire spec is the owner
    new_group = None

    if ':' in owner_spec:
        new_owner_part, new_group_part = owner_spec.split(':', 1)
        new_owner = new_owner_part if new_owner_part else None # Allow ":group" to mean no owner change
        new_group = new_group_part if new_group_part else None
    elif '.' in owner_spec: # Common alternative e.g. user.group
        new_owner_part, new_group_part = owner_spec.split('.', 1)
        new_owner = new_owner_part if new_owner_part else None
        new_group = new_group_part if new_group_part else None
    
    if new_owner == "": new_owner = None # Handle " " from split if :group was used

    if not new_owner and not new_group:
        return NO_EXEC_MARKER + "chown: Invalid owner/group specification.", False
        
    commands_templates = []
    recursive_opt_setowner = "/T /C" if parsed_args.recursive else "/C" # /T for setowner implies subitems. /C continues on error.
    recursive_opt_grant = "/T" if parsed_args.recursive else "" # For /grant, /T is enough for inheritance.

    if new_owner:
        # User must be a valid security principal (user or group) on the system
        # e.g., "Administrator", "BUILTIN\\Administrators", "DOMAIN\\User"
        commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt_setowner} /setowner {shlex.quote(new_owner)}")

    if new_group:
        ui_manager.display_warning(f"chown: Approximating group '{new_group}' change by granting Full Control (F) via icacls.")
        # (OI)(CI) for inheritance on directories if recursive
        inheritance_str = "(OI)(CI)" if parsed_args.recursive else "" # Object Inherit, Container Inherit
        commands_templates.append(f"icacls {{file_placeholder}} {recursive_opt_grant} /grant {shlex.quote(new_group)}:({inheritance_str}F)")

    if not commands_templates:
        return NO_EXEC_MARKER + "chown: No actions determined from owner/group spec.", False

    final_file_commands = []
    for f_path_relative in parsed_args.files:
        abs_f_path = os.path.abspath(f_path_relative)
        quoted_abs_f = shlex.quote(abs_f_path)
        for cmd_template in commands_templates:
            final_file_commands.append(cmd_template.format(file_placeholder=quoted_abs_f))
            
    if not final_file_commands:
        return NO_EXEC_MARKER + "chown: no executable commands generated for any file.", False

    return " ; ".join(final_file_commands), True # Elevation always assumed for chown
    
# === Text Processing ===
def translate_cat(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='cat', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for cat')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-n', '--number', action='store_true')
    parser.add_argument('files', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"cat: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]cat - Concatenate and display files[/bold magenta]
[cyan]Description:[/cyan]
  Displays file content. Mapped to `Get-Content`. Handles some special Linux paths.

[cyan]Common Usage:[/cyan]
  cat [options] [file ...]

[cyan]Supported Flags:[/cyan]
  -n, --number    Number all output lines.
  --help, -h      Show this help message.

[cyan]Special Paths (simulated):[/cyan]
  /etc/fstab, /etc/hosts, /etc/resolv.conf, /proc/cpuinfo, /proc/meminfo, etc.
  (`-n` flag ignored for these).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if len(parsed_args.files) == 1:
        normalized_path = parsed_args.files[0].lower().replace('\\', '/')
        if normalized_path in SPECIAL_CAT_PATHS:
            powershell_cmd, needs_elevation = SPECIAL_CAT_PATHS[normalized_path]
            if parsed_args.number: ui_manager.display_warning(f"cat: Flag '-n' ignored for special path '{parsed_args.files[0]}'")
            context_comment = f"# Showing Windows equivalent for: {parsed_args.files[0]}"
            final_cmd = f"Write-Host '{context_comment}' -ForegroundColor Gray; {powershell_cmd}" if not powershell_cmd.strip().startswith("Write-Host '# Windows") else powershell_cmd
            return final_cmd, needs_elevation
            
    base_cmd = "Get-Content"; params = []; post_cmds = []
    if parsed_args.files: # If files are specified after potential help processing
        params.extend([f"-LiteralPath {shlex.quote(f)}" for f in parsed_args.files])
        params.append("-ErrorAction SilentlyContinue")
    # If no files (e.g. 'cat -n' or just 'cat'), it reads from stdin (pipeline input for Get-Content)
    
    if parsed_args.number: post_cmds.append('$global:lineNumber = 0; Foreach-Object { $global:lineNumber++; Write-Host ("{0,6}  {1}" -f $global:lineNumber, $_) }')
    
    full_cmd = base_cmd # Start with base command
    if params: full_cmd += " " + ' '.join(params) # Add params if any
    if post_cmds: full_cmd = f"({full_cmd})" + " | " + " | ".join(post_cmds) if parsed_args.files else " | ".join(post_cmds) # Pipe if files or directly if stdin

    return full_cmd, False

def translate_grep(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='grep', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for grep')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-i', '--ignore-case', action='store_true')
    parser.add_argument('-v', '--invert-match', action='store_true')
    parser.add_argument('-n', '--line-number', action='store_true')
    parser.add_argument('-r','-R', '--recursive', action='store_true')
    parser.add_argument('pattern', nargs='?') # Optional for help
    parser.add_argument('files', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"grep: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]grep - Print lines matching a pattern[/bold magenta]
[cyan]Description:[/cyan]
  Searches PATTERN in FILEs or stdin. Mapped to `Select-String`.

[cyan]Common Usage:[/cyan]
  grep [options] PATTERN [FILE...]

[cyan]Supported Flags:[/cyan]
  -i, --ignore-case   Ignore case (`-CaseSensitive:$false`).
  -v, --invert-match  Select non-matching lines (`-NotMatch`).
  -n, --line-number   Print line number (default `Select-String` behavior).
  -r, -R, --recursive Recursive search (`Get-ChildItem -Recurse | Select-String`).
  --help, -h          Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.pattern:
        return NO_EXEC_MARKER + "grep: missing pattern. Try 'grep --help'.", False

    select_string_cmd = "Select-String"; ss_params = [f"-Pattern {shlex.quote(parsed_args.pattern)}"]
    ss_params.append("-CaseSensitive:$false" if parsed_args.ignore_case else "-CaseSensitive")
    if parsed_args.invert_match: ss_params.append("-NotMatch")
    # -n (line number) is default output for Select-String objects.
    
    result_cmd = ""
    if not parsed_args.files: result_cmd = f"{select_string_cmd} {' '.join(ss_params)}"
    elif parsed_args.recursive:
        gci_params = ["-Recurse", "-File", "-ErrorAction SilentlyContinue"]
        gci_params.extend([shlex.quote(f) for f in parsed_args.files])
        result_cmd = f"Get-ChildItem {' '.join(gci_params)} | {select_string_cmd} {' '.join(ss_params)}"
    else:
        ss_params.append("-LiteralPath"); ss_params.extend([shlex.quote(f) for f in parsed_args.files]); ss_params.append("-ErrorAction SilentlyContinue")
        result_cmd = f"{select_string_cmd} {' '.join(ss_params)}"
    return result_cmd, False

def translate_head_tail(cmd_name: str, args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False)
    parser.add_argument('--help', action='store_true', help=f'Show Swodnil help for {cmd_name}')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-n', '--lines', type=int, default=10)
    if cmd_name == 'tail': parser.add_argument('-f', '--follow', action='store_true')
    parser.add_argument('file', nargs='?', default=None)
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"{cmd_name}: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = f"""
[bold magenta]{cmd_name} - Output the first/last part of files[/bold magenta]
[cyan]Description:[/cyan]
  Prints first/last N lines. Mapped to `Get-Content` or `Select-Object`.

[cyan]Common Usage:[/cyan]
  {cmd_name} [options] [file...]

[cyan]Supported Flags:[/cyan]
  -n, --lines <N>   Print N lines (default 10).
  --help, -h        Show this help message.
"""
        if cmd_name == 'tail': help_string += "  -f, --follow      Output appended data (`Get-Content -Wait`). Cannot follow pipeline input.\n"
        help_string += """
[cyan]Notes:[/cyan]
  - Reads from stdin if no file specified.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    base_cmd = "Get-Content"; params = []
    if parsed_args.file: params.extend([f"-LiteralPath {shlex.quote(parsed_args.file)}", "-ErrorAction SilentlyContinue"])
    
    if not parsed_args.file: # Reading from pipeline
        selector_obj = "-First" if cmd_name == 'head' else "-Last"
        if cmd_name == 'tail' and parsed_args.follow: return NO_EXEC_MARKER + "tail -f: cannot follow pipeline input.", False
        return f"Select-Object {selector_obj} {parsed_args.lines}", False
    else: # Reading from file
        selector_gc = "-Head" if cmd_name == 'head' else "-Tail"
        params.append(f"{selector_gc} {parsed_args.lines}")
        if cmd_name == 'tail' and parsed_args.follow: params.append("-Wait")
        return f"{base_cmd} {' '.join(params)}", False

def translate_head(args: list[str]) -> tuple[str | None, bool]: return translate_head_tail('head', args)
def translate_tail(args: list[str]) -> tuple[str | None, bool]: return translate_head_tail('tail', args)


# === System Information & Management ===
def translate_hostname(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='hostname', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for hostname')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"hostname: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]hostname - Show system's host name[/bold magenta]
[cyan]Description:[/cyan]
  Prints system host name. Mapped to `$env:COMPUTERNAME`. (Setting hostname not supported).

[cyan]Common Usage:[/cyan]
  hostname

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: return NO_EXEC_MARKER + "hostname: does not support arguments.", False
    return 'Write-Host $env:COMPUTERNAME', False

def translate_uname(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='uname', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for uname')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-s', '--kernel-name', action='store_true')
    parser.add_argument('-n', '--nodename', action='store_true')
    parser.add_argument('-r', '--kernel-release', action='store_true')
    parser.add_argument('-v', '--kernel-version', action='store_true')
    parser.add_argument('-m', '--machine', action='store_true')
    parser.add_argument('-o', '--operating-system', action='store_true')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"uname: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]uname - Print system information[/bold magenta]
[cyan]Description:[/cyan]
  Prints system info using Python's `platform` module.

[cyan]Common Usage:[/cyan]
  uname [options]

[cyan]Supported Flags:[/cyan]
  (default)       Print kernel name ('Windows').
  -a, --all       Print all available information.
  -s              Print kernel name.
  -n              Print network node hostname.
  -r              Print kernel release.
  -v              Print kernel version.
  -m              Print machine hardware name.
  -o              Print operating system.
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    results = []; sys_system = platform.system(); sys_release = platform.release(); sys_version = platform.version(); sys_machine = platform.machine(); sys_node = platform.node()
    if not any([parsed_args.all, parsed_args.kernel_name, parsed_args.nodename, parsed_args.kernel_release, parsed_args.kernel_version, parsed_args.machine, parsed_args.operating_system]):
        parsed_args.kernel_name = True # Default if no flags
    if parsed_args.kernel_name or parsed_args.all: results.append(sys_system)
    if parsed_args.nodename or parsed_args.all: results.append(sys_node)
    if parsed_args.kernel_release or parsed_args.all: results.append(sys_release)
    if parsed_args.kernel_version or parsed_args.all: results.append(sys_version)
    if parsed_args.machine or parsed_args.all: results.append(sys_machine)
    if parsed_args.operating_system or parsed_args.all: (sys_system not in results) and results.append(sys_system)
    return f"Write-Host \"{' '.join(results)}\"", False

def translate_df(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='df', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for df')
    parser.add_argument('-H', '-h', '--human-readable', dest='human_readable', action='store_true') # Note: -H is for SI units in GNU df, -h for power-of-2. We map both to GiB/MiB etc.
    parser.add_argument('files', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"df: {e}", False

    if parsed_args.help: # Note: 'help_short' not defined as -h is for human-readable
        help_string = """
[bold magenta]df - Report file system disk space usage[/bold magenta]
[cyan]Description:[/cyan]
  Displays disk space usage. Mapped to `Get-PSDrive` or `Get-Volume`.

[cyan]Common Usage:[/cyan]
  df [options] [file...]

[cyan]Supported Flags:[/cyan]
  -h, -H, --human-readable  Print sizes in human-readable format (GiB, MiB).
  --help                    Show this help message.
  [file...]                 If specified, shows usage for volume containing file(s)
                            (uses `Get-Volume`, may need elevation).

[cyan]Notes:[/cyan]
  - Default uses `Get-PSDrive`. With file args, uses `Get-Volume` (may need elevation).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    base_cmd = "Get-PSDrive"; params = ["-PSProvider FileSystem"]; needs_elevation = False
    format_bytes_func = ("$FormatBytes = {param($bytes) if ($bytes -eq $null) {'N/A'} elseif ($bytes -ge 1GB) {{'{0:N2} GiB' -f ($bytes / 1GB)}} elseif ($bytes -ge 1MB) {{'{0:N1} MiB' -f ($bytes / 1MB)}} elseif ($bytes -ge 1KB) {{'{0:N1} KiB' -f ($bytes / 1KB)}} else {{'{0} B' -f $bytes}}}; ")
    properties_psdrive = ["Name", "@{N='Size';E={($_.Used + $_.Free)}}", "Used", "Free", "@{N='Use%';E={if (($_.Used + $_.Free) -gt 0) {[int]($_.Used / ($_.Used + $_.Free) * 100)} else {0} }}", "Root"]
    human_readable_properties_psdrive = ["Name", "@{N='Size';E={& $FormatBytes ($_.Used + $_.Free)}}", "@{N='Used';E={& $FormatBytes $_.Used}}", "@{N='Free';E={& $FormatBytes $_.Free}}", "@{N='Use%';E={if (($_.Used + $_.Free) -gt 0) {[int]($_.Used / ($_.Used + $_.Free) * 100)} else {0} }}", "Root"]
    select_props = properties_psdrive; prefix_cmd = ""
    if parsed_args.human_readable: select_props = human_readable_properties_psdrive; prefix_cmd = format_bytes_func
    if parsed_args.files:
        ui_manager.display_warning("df: Path filtering requires Get-Volume (may need elevation).")
        base_cmd = "Get-Volume"; params = []; needs_elevation = True
        params.extend([f"-FilePath {shlex.quote(f)}" for f in parsed_args.files])
        properties_vol = ["DriveLetter", "@{N='Size';E={$_.Size}}", "@{N='Used';E={($_.Size - $_.SizeRemaining)}}", "@{N='Avail';E={$_.SizeRemaining}}", "@{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}", "@{N='Mounted on';E={$_.Path}}"]
        human_readable_properties_vol = ["DriveLetter", "@{N='Size';E={& $FormatBytes $_.Size}}", "@{N='Used';E={& $FormatBytes ($_.Size - $_.SizeRemaining)}}", "@{N='Avail';E={& $FormatBytes $_.SizeRemaining}}", "@{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}", "@{N='Mounted on';E={$_.Path}}"]
        select_props = properties_vol
        if parsed_args.human_readable: select_props = human_readable_properties_vol; prefix_cmd = format_bytes_func
        else: prefix_cmd = ""
    format_cmd = f"| Select-Object {','.join(select_props)} | Format-Table -AutoSize"
    full_cmd = f"{prefix_cmd}{base_cmd} {' '.join(params)} {format_cmd}"
    return full_cmd, needs_elevation

def translate_ps(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='ps', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for ps')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    # For combined flags like 'aux', 'ax', '-ef'
    parser.add_argument('pos_args', nargs='*', help="Combined flags like 'aux', 'ax', or other arguments")
    # Specific flags if desired, though often combined in pos_args
    parser.add_argument('-e', '-A', dest='show_all_explicit', action='store_true')
    parser.add_argument('-f', dest='full_format_explicit', action='store_true')
    parser.add_argument('-u', dest='user_format_explicit', action='store_true')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"ps: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]ps - Report a snapshot of current processes[/bold magenta]
[cyan]Description:[/cyan]
  Displays process info. Mapped to `Get-Process`.

[cyan]Common Usage (heuristic mapping for combined flags):[/cyan]
  ps [options] (e.g., ps aux, ps -ef)

[cyan]Supported Options (heuristic mapping from combined flags like 'aux', 'ef'):[/cyan]
  `a`             Show all users' processes (effectively default for `Get-Process`).
  `x`             Show processes without tty (effectively default).
  `u`             User-oriented format (Username, PID, %CPU, %MEM, etc. Uses `-IncludeUserName`, may need elevation).
  `-e`, `-A`      Select all processes (same as `a`).
  `-f`            Full-format listing (UID, PID, PPID, etc. Uses `-IncludeUserName`, may need elevation).
  --help, -h      Show this help message.

[cyan]Notes:[/cyan]
  - `-IncludeUserName` for `u` or `-f` may require Administrator privileges.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    raw_flags_from_pos = "".join(parsed_args.pos_args)
    user_format_heuristic = parsed_args.user_format_explicit or 'u' in raw_flags_from_pos
    full_format_heuristic = parsed_args.full_format_explicit or 'f' in raw_flags_from_pos
    if 'x' in raw_flags_from_pos: ui_manager.display_info("ps: 'x' flag behavior is effectively default with Get-Process.")

    base_cmd = "Get-Process"; params = ["-ErrorAction SilentlyContinue"]; needs_elevation = False
    if user_format_heuristic:
        params.append("-IncludeUserName")
        properties = ["@{N='USER';E={$_.UserName}}", "@{N='PID';E={$_.Id}}", "@{N='CPU';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}", "@{N='MEM';E={if($_.WS -ne $null){[math]::Round($_.WS / (Get-CimInstance Win32_OperatingSystem).TotalVisibleMemorySize * 100, 1)}else{0}}}", "@{N='VSZ(MB)';E={[math]::Round($_.VM / 1MB)}}", "@{N='RSS(MB)';E={[math]::Round($_.WS / 1MB)}}", "@{N='START';E={$_.StartTime.ToString('HH:mm:ss')}}", "@{N='COMMAND';E={$_.Path}}"]
        format_cmd = f"| Format-Table {','.join(properties)} -AutoSize"; needs_elevation = True
    elif full_format_heuristic:
        params.append("-IncludeUserName")
        properties = ["@{N='UID';E={$_.UserName}}", "@{N='PID';E={$_.Id}}", "@{N='PPID';E={(Get-CimInstance Win32_Process -Filter ('ProcessId=' + $_.Id) -ErrorAction SilentlyContinue).ParentProcessId}}", "@{N='STIME';E={$_.StartTime.ToString('HH:mm')}}", "@{N='TIME';E={if($_.CPU -ne $null){$ts = [System.TimeSpan]::FromSeconds($_.CPU); '{0:D2}:{1:D2}:{2:D2}' -f $ts.Hours, $ts.Minutes, $ts.Seconds}else{'00:00:00'}}}", "@{N='CMD';E={$_.ProcessName + ' ' + $_.CommandLine}}"] # CommandLine may need elevation
        format_cmd = f"| Format-Table {','.join(properties)} -AutoSize"; needs_elevation = True
    else:
        properties = ["Id", "ProcessName", "@{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}", "@{N='WS(MB)';E={[math]::Round($_.WS / 1MB)}}"]
        format_cmd = f"| Select-Object {','.join(properties)} | Format-Table -AutoSize"
    return f"{base_cmd} {' '.join(params)} {format_cmd}", needs_elevation

def translate_kill(args: list[str]) -> tuple[str | None, bool]: # Handles kill and killall
    parser = NonExitingArgumentParser(prog='kill/killall', add_help=False) # Prog name set by caller in map
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for kill/killall')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-s', '--signal', default='TERM')
    parser.add_argument('-9', dest='force_kill', action='store_true')
    parser.add_argument('targets', nargs='*') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"kill/killall: {e}", False

    prog_name = "kill/killall" # Generic if not determined, could be passed in
    # Heuristic to guess original command if called via map
    if args and len(args) > 0 and args[-1] in TRANSLATION_MAP and args[-1].startswith("kill"):
        prog_name = args[-1]


    if parsed_args.help or parsed_args.help_short:
        help_string = f"""
[bold magenta]{prog_name} - Terminate processes[/bold magenta]
[cyan]Description:[/cyan]
  Terminates processes. Mapped to `Stop-Process`. `killall` targets by name.
  `kill` typically targets by PID.

[cyan]Common Usage:[/cyan]
  kill [options] <PID ...>
  killall [options] <name ...>

[cyan]Supported Options:[/cyan]
  -9                Force kill (SIGKILL equivalent, uses `Stop-Process -Force`).
  -s <signal>       Specify signal (mostly ignored; `-9` or `KILL` implies `-Force`).
  --help, -h        Show this help message.

[cyan]Notes:[/cyan]
  - Terminating certain processes may require Administrator privileges.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.targets:
        return NO_EXEC_MARKER + f"{prog_name}: missing operand. Try '{prog_name} --help'.", False

    # Determine if targets are PIDs (all digits) or names
    # This heuristic is for the combined kill/killall handler
    is_pid = all(t.isdigit() for t in parsed_args.targets)
    # If prog_name was specifically 'killall', assume names even if all digits.
    # This requires passing prog_name into translate_kill if map keys differ.
    # For now, simple heuristic:
    # if parser.prog == 'killall': is_pid = False # Override if explicitly killall
    # This parser.prog check is not easily done here as prog is set by caller.

    base_cmd = "Stop-Process"; params = ["-ErrorAction SilentlyContinue"]
    if is_pid : params.extend(["-Id"] + parsed_args.targets) # Assumes 'kill' behavior
    else: params.extend(["-Name"] + [shlex.quote(t) for t in parsed_args.targets]) # Assumes 'killall' or mixed
    
    if parsed_args.force_kill or parsed_args.signal.upper() in ['KILL', '9']: params.append("-Force")
    return f"{base_cmd} {' '.join(params)}", True # Assume elevation might be needed

def translate_top(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='top', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for top')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args) # Allow other args to be ignored
    except ValueError as e: return NO_EXEC_MARKER + f"top: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]top - Display processes (static snapshot)[/bold magenta]
[cyan]Description:[/cyan]
  Static list of current processes, sorted by CPU. Uses `Get-Process`.

[cyan]Common Usage:[/cyan]
  top

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments are ignored).

[cyan]Notes:[/cyan]
  - Not interactive like Linux `top`. Shows top 15 processes by CPU.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if remaining_args: ui_manager.display_warning("top: Arguments are ignored in this basic translation.")
    cmd = ("Get-Process -ErrorAction SilentlyContinue | Sort-Object CPU -Descending | Select-Object -First 15 "
           "Id, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, "
           "@{N='Mem(MB)';E={[math]::Round($_.WS / 1MB)}}, ProcessName "
           "| Format-Table -AutoSize")
    return cmd, False

def translate_id(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='id', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for id')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"id: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]id - Print user and group information[/bold magenta]
[cyan]Description:[/cyan]
  Prints current user identity. Mapped to `whoami /all /fo list`.

[cyan]Common Usage:[/cyan]
  id

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments are ignored).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if remaining_args: ui_manager.display_warning("id: Arguments are ignored, using 'whoami /all /fo list'.")
    return "whoami /all /fo list", False

# === Network ===
def translate_ifconfig(args: list[str]) -> tuple[str | None, bool]: # Also for 'ip'
    parser = NonExitingArgumentParser(prog='ifconfig/ip', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for ifconfig/ip')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('interface', nargs='?')
    # For 'ip addr' style commands
    parser.add_argument('addr_show', nargs='*') # Catches 'addr show' or 'addr' etc.
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"ifconfig/ip: {e}", False

    prog_name = "ifconfig/ip" # Could be refined if prog name is passed

    if parsed_args.help or parsed_args.help_short:
        help_string = f"""
[bold magenta]{prog_name} - Network interface configuration (display only)[/bold magenta]
[cyan]Description:[/cyan]
  Displays network interface info. Mapped to `ipconfig /all` or `Get-NetIPConfiguration`.
  `ip addr show` style commands also map to this. Setting parameters not supported.

[cyan]Common Usage:[/cyan]
  {prog_name} [interface]
  ip addr [show [interface]]

[cyan]Arguments:[/cyan]
  [interface]   If specified, shows details for that interface.

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    target_interface = parsed_args.interface
    # Handle 'ip addr show <interface>' or 'ip addr <interface>'
    if not target_interface and parsed_args.addr_show:
        # Check if last part of addr_show could be an interface name
        # This is heuristic. `ip addr` or `ip addr show` -> all interfaces
        # `ip addr show eth0` -> eth0. `ip addr eth0` -> eth0
        if len(parsed_args.addr_show) > 0 and parsed_args.addr_show[-1] not in ['addr', 'show']:
            target_interface = parsed_args.addr_show[-1]
        elif len(parsed_args.addr_show) == 1 and parsed_args.addr_show[0] not in ['addr', 'show']: # e.g. ip eth0
             target_interface = parsed_args.addr_show[0]


    if target_interface:
        iface = shlex.quote(target_interface)
        cmd = f"Get-NetIPConfiguration -InterfaceAlias {iface} -ErrorAction SilentlyContinue | Format-List; Get-NetAdapter -Name {iface} -ErrorAction SilentlyContinue | Format-List Status, LinkSpeed, MacAddress"
    else: cmd = "ipconfig /all" # Default for ifconfig or 'ip addr'
    return cmd, False

def translate_whois(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='whois', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for whois')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('domain', nargs='?') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"whois: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]whois - WHOIS directory service client[/bold magenta]
[cyan]Description:[/cyan]
  Looks up domain/IP info. Relies on external `whois.exe` in PATH.

[cyan]Common Usage:[/cyan]
  whois <domain_or_ip>

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.domain:
        return NO_EXEC_MARKER + "whois: missing domain operand. Try 'whois --help'.", False
    domain = shlex.quote(parsed_args.domain); ui_manager.console.print(f"[dim]Attempting 'whois {domain}'. Requires external 'whois.exe' in PATH.[/dim]");
    return f"whois {domain}", False # Assumes external whois.exe

def translate_dig(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='dig', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for dig')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    # Positional arguments for dig are complex to model perfectly in argparse for all cases.
    # We'll parse known options and treat remaining as name/type/@server.
    # This is a simplification.
    parser.add_argument('query_params', nargs='*')
    try: parsed_args_main = parser.parse_args(args) # Use parse_args to catch --help/-h
    except ValueError as e: return NO_EXEC_MARKER + f"dig: {e}", False

    if parsed_args_main.help or parsed_args_main.help_short:
        help_string = """
[bold magenta]dig - DNS lookup utility[/bold magenta]
[cyan]Description:[/cyan]
  Performs DNS lookups. Mapped to `Resolve-DnsName`.

[cyan]Common Usage (simplified parsing):[/cyan]
  dig [@server] <name> [type]
  (e.g., dig example.com MX, dig @8.8.8.8 example.com AAAA)

[cyan]Arguments & Options (basic mapping):[/cyan]
  `@server`       Specify DNS server (e.g., `@8.8.8.8`).
  `<name>`          The domain name to query.
  `[type]`        Query type (A, AAAA, MX, TXT, CNAME, NS, etc.). Defaults to A.
  --help, -h      Show this help message.

[cyan]Notes:[/cyan]
  - `Resolve-DnsName` used with `-CacheOnly:$false -DnsOnly`.
  - Argument parsing is basic; complex `dig` options are not supported.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    # Actual dig parsing from query_params
    q_params = parsed_args_main.query_params
    if not q_params: return NO_EXEC_MARKER + "dig: missing query parameters. Try 'dig --help'.", False
    
    name = None; qtype = 'A'; server = None; temp_q_params = list(q_params)

    if temp_q_params[0].startswith('@'): server = temp_q_params.pop(0)[1:]
    if not temp_q_params: return NO_EXEC_MARKER + "dig: missing name to query.", False
    name = temp_q_params.pop(0)
    if temp_q_params:
        potential_qtype = temp_q_params[0].upper()
        if potential_qtype in ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA', 'SRV', 'ANY']:
            qtype = potential_qtype; temp_q_params.pop(0)
    if temp_q_params: ui_manager.display_warning(f"dig: Ignoring unexpected arguments: {' '.join(temp_q_params)}")

    cmd = f"Resolve-DnsName -Name {shlex.quote(name)} -Type {qtype} -CacheOnly:$false -DnsOnly"
    if server: cmd += f" -Server {shlex.quote(server)}"
    return cmd, False

def translate_wget_curl(cmd_name: str, args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False)
    parser.add_argument('--help', action='store_true', help=f'Show Swodnil help for {cmd_name}')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-O', '--output-document', dest='output_file')
    parser.add_argument('-o', dest='output_file_curl_alias') # For curl
    parser.add_argument('-L', '--location', action='store_true')
    parser.add_argument('-H', '--header', action='append', default=[])
    parser.add_argument('-X', '--request', dest='method', default='GET')
    parser.add_argument('--insecure', '-k', action='store_true')
    parser.add_argument('url', nargs='?') # Optional for help
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"{cmd_name}: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = f"""
[bold magenta]{cmd_name} - Transfer data from or to a server[/bold magenta]
[cyan]Description:[/cyan]
  Downloads URL content. Mapped to `Invoke-WebRequest`.
  `curl` is also mapped here with limited flag support.

[cyan]Common Usage ({cmd_name}):[/cyan]
  {cmd_name} [options] <URL>

[cyan]Supported Flags:[/cyan]
  -O <file>           (wget) Write to file (`-OutFile`).
  -o <file>           (curl) Write to file (`-OutFile`).
  -L                  Follow redirects (default in `Invoke-WebRequest`).
  -H <header>         Pass custom header(s) (e.g., "Key: Value").
  -X <method>         HTTP method (GET, POST, etc.).
  --insecure, -k      Ignore SSL errors (`-SkipCertificateCheck`).
  --help, -h          Show this help message.

[cyan]Notes:[/cyan]
  - If no output file, content goes to stdout.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.url:
        return NO_EXEC_MARKER + f"{cmd_name}: missing URL. Try '{cmd_name} --help'.", False
    if remaining_args: ui_manager.display_warning(f"{cmd_name}: Ignoring unsupported arguments: {' '.join(remaining_args)}")

    output_file = parsed_args.output_file_curl_alias if parsed_args.output_file_curl_alias else parsed_args.output_file
    base_cmd = "Invoke-WebRequest"; params = [f"-Uri {shlex.quote(parsed_args.url)}", f"-Method {parsed_args.method.upper()}"]
    if parsed_args.insecure: params.append("-SkipCertificateCheck")
    if output_file: params.append(f"-OutFile {shlex.quote(output_file)}")
    else: params.append("-UseBasicParsing") # For stdout
    if parsed_args.header:
        headers_dict = {key.strip(): val.strip() for h in parsed_args.header if ':' in h for key, val in [h.split(':', 1)]}
        if headers_dict: header_ps_str = "@{" + "; ".join([f'"{k}"="{v}"' for k,v in headers_dict.items()]) + "}"; params.append(f"-Headers {header_ps_str}")
    post_cmd = "" if output_file else "| Select-Object -ExpandProperty Content"
    full_cmd = f"{base_cmd} {' '.join(params)} {post_cmd}"
    return full_cmd, False

def translate_wget(args: list[str]) -> tuple[str | None, bool]: return translate_wget_curl('wget', args)
def translate_curl(args: list[str]) -> tuple[str | None, bool]: return translate_wget_curl('curl', args)

# === Package Management & OS ===
def translate_apt(args: list[str]) -> tuple[str | None, bool]: # Also for yum, dnf, pacman, zypper
    # Heuristic for prog_name based on how TRANSLATION_MAP might be structured or if called directly
    # This is mainly for the help string.
    prog_name = "Package Manager (apt, yum, etc.)"
    # This is imperfect; shell_core would know the exact command typed.
    # For now, this generic name is used in help.

    parser = NonExitingArgumentParser(prog=prog_name, add_help=False) # prog set for potential error messages
    parser.add_argument('--help', action='store_true', help=f'Show Swodnil help for {prog_name}')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    
    # Subparsers for actual commands
    subparsers = parser.add_subparsers(dest='subcommand_actual', help='sub-command help')
    # Define subparsers for install, update, etc.
    # This gets complex if we want `apt --help` vs `apt install --help`.
    # For Swodnil, one `--help` for the whole `apt` translation is likely sufficient.
    # So, we parse --help first. If not help, then try to parse subcommands.

    # Tentative: Parse known args first to catch global --help/-h
    try:
        # Use parse_known_args to separate --help from subcommand and its args
        parsed_global_opts, remaining_sub_args = parser.parse_known_args(args)
    except ValueError as e: # Handles errors from parsing global options like --help
        return NO_EXEC_MARKER + f"{prog_name}: {e}", False

    if parsed_global_opts.help or parsed_global_opts.help_short:
        help_string = f"""
[bold magenta]{prog_name} -> winget Mapping[/bold magenta]
[cyan]Description:[/cyan]
  Manages software. Mapped to `winget`. Requires Administrator for most changes.

[cyan]Common Subcommands (Swodnil maps to `winget`):[/cyan]
  `update`                 -> `winget source update`
  `upgrade [pkg...]`       -> `winget upgrade [--all | pkg...]`
  `install <pkg...>`       -> `winget install <pkg...>`
  `remove <pkg...>`        -> `winget uninstall <pkg...>` (also for `purge`)
  `search <query...>`      -> `winget search <query...>`
  `show <pkg>`             -> `winget show <pkg>`
  `list [installed]`       -> `winget list`

[cyan]Supported Options (general):[/cyan]
  -y, --yes           Auto-confirm (`--accept-...-agreements --disable-interactivity`).
  --help, -h          Show this help message.

[cyan]Pacman Aliases Mapped:[/cyan]
  -Syu -> upgrade --all; -S -> install; -R[ns] -> remove; -Ss -> search; -Qs -> list
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    # If not help, now parse the subcommand and its arguments from remaining_sub_args
    # Re-initialize parser for subcommands
    parser_sub = NonExitingArgumentParser(prog=prog_name, add_help=False)
    subparsers_sub = parser_sub.add_subparsers(dest='subcommand', help='Sub-command help') # dest must be 'subcommand'
    subparsers_sub.add_parser('update'); upg = subparsers_sub.add_parser('upgrade'); upg.add_argument('packages', nargs='*'); upg.add_argument('-y', '--yes', action='store_true'); inst = subparsers_sub.add_parser('install'); inst.add_argument('packages', nargs='+'); inst.add_argument('-y', '--yes', action='store_true'); rem = subparsers_sub.add_parser('remove'); rem.add_argument('packages', nargs='+'); rem.add_argument('-y', '--yes', action='store_true'); purg = subparsers_sub.add_parser('purge'); purg.add_argument('packages', nargs='+'); purg.add_argument('-y', '--yes', action='store_true'); srch_sub = subparsers_sub.add_parser('search'); srch_sub.add_argument('query', nargs='+'); sh_sub = subparsers_sub.add_parser('show'); sh_sub.add_argument('package'); list_parser_sub = subparsers_sub.add_parser('list'); list_parser_sub.add_argument('packages', nargs='*')
    
    aliases = {'add': 'install', 'delete': 'remove', 'erase': 'remove', 'info': 'show'}
    processed_sub_args = list(remaining_sub_args) # Work with the sub-args

    # Alias processing for subcommands
    if processed_sub_args:
        potential_alias_cmd = processed_sub_args[0]
        if potential_alias_cmd in aliases: processed_sub_args[0] = aliases[potential_alias_cmd]
        # Pacman specific simple alias mapping (assuming prog_name gives a hint)
        # This is still imperfect without knowing the exact Linux command typed by user for TRANSLATION_MAP aliasing
        elif "pacman" in prog_name.lower(): # Check if it's likely pacman
            if potential_alias_cmd == '-Syu': processed_sub_args = ['upgrade']
            elif potential_alias_cmd == '-S': processed_sub_args = ['install'] + processed_sub_args[1:]
            elif potential_alias_cmd == '-Rns' or potential_alias_cmd == '-R': processed_sub_args = ['remove'] + processed_sub_args[1:]
            elif potential_alias_cmd == '-Ss': processed_sub_args = ['search'] + processed_sub_args[1:]
            elif potential_alias_cmd == '-Qs': processed_sub_args = ['list'] + processed_sub_args[1:]
            elif potential_alias_cmd == '-Q': processed_sub_args = ['list']
        elif any(cmd_n in prog_name.lower() for cmd_n in ["dnf", "yum"]) and " ".join(processed_sub_args).startswith("list installed"):
            processed_sub_args = ['list']
    
    if not processed_sub_args: # No subcommand provided after potential global --help
        return NO_EXEC_MARKER + f"{prog_name}: missing subcommand. Try '{prog_name} --help'.", False

    try:
        parsed_sub_cmd_args = parser_sub.parse_args(processed_sub_args)
    except ValueError as e: # Handles errors from parsing subcommand
        # Check if it was 'list installed' or similar common forms not caught by subparsers
        if "list" in " ".join(processed_sub_args): # Heuristic
            parsed_sub_cmd_args = argparse.Namespace(subcommand='list', packages=[p for p in processed_sub_args if p !='list' and p !='installed'])
        else:
            return NO_EXEC_MARKER + f"{prog_name} subcommand error: {e}. Try '{prog_name} --help'.", False

    base_cmd="winget"; subcmd=parsed_sub_cmd_args.subcommand; params=[]; accept=False; needs_elevation = False
    if subcmd == 'update': params.append("source update"); needs_elevation = True
    elif subcmd == 'upgrade':
        params.append("upgrade"); accept=getattr(parsed_sub_cmd_args,'yes',False)
        if parsed_sub_cmd_args.packages: params.extend([shlex.quote(p) for p in parsed_sub_cmd_args.packages])
        else: params.append("--all")
        needs_elevation = True
    elif subcmd == 'install': params.append("install"); params.extend([shlex.quote(p) for p in parsed_sub_cmd_args.packages]); accept=getattr(parsed_sub_cmd_args,'yes',False); needs_elevation = True
    elif subcmd in ['remove','purge']: params.append("uninstall"); params.extend([shlex.quote(p) for p in parsed_sub_cmd_args.packages]); accept=getattr(parsed_sub_cmd_args,'yes',False); needs_elevation = True
    elif subcmd == 'search': params.append("search"); params.append(shlex.quote(" ".join(parsed_sub_cmd_args.query)))
    elif subcmd == 'show': params.append("show"); params.append(shlex.quote(parsed_sub_cmd_args.package))
    elif subcmd == 'list':
        params.append("list")
        if hasattr(parsed_sub_cmd_args, 'packages') and parsed_sub_cmd_args.packages: params.extend([shlex.quote(p) for p in parsed_sub_cmd_args.packages])
    else: return f"winget {subcmd} # (Passthrough for unknown subcommand)", False # Should be caught by parser

    if accept: params.extend(["--accept-package-agreements", "--accept-source-agreements"])
    if subcmd not in ['search', 'show', 'list', 'update']: params.append("--disable-interactivity") # Avoid prompts from winget
    return f"{base_cmd} {' '.join(params)}", needs_elevation

def translate_do_release_upgrade_sim(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='do-release-upgrade', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"do-release-upgrade: {e}", False
    
    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]do-release-upgrade (simulated) - Upgrade OS[/bold magenta]
[cyan]Description:[/cyan]
  Simulates checking/installing Windows Updates via COM objects. Installation needs Admin.

[cyan]Common Usage:[/cyan]
  do-release-upgrade

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments are ignored).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: ui_manager.display_warning("do-release-upgrade: Arguments are ignored.")

    ps_check_cmd = "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateUpdateSearcher; Write-Host 'Searching for updates...'; try { $SearchResult = $UpdateSearcher.Search(\"IsInstalled=0 and Type='Software'\"); Write-Host (\"Found \" + $SearchResult.Updates.Count + \" updates.\"); return $SearchResult.Updates.Count; } catch { Write-Warning \"Failed to search for updates. Error: $($_.Exception.Message)\"; return -1; }"
    ps_install_cmd = "$ErrorActionPreference = 'Stop'; try { $UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateUpdateSearcher; $SearchResult = $UpdateSearcher.Search(\"IsInstalled=0 and Type='Software'\"); if ($SearchResult.Updates.Count -eq 0) { Write-Host 'No updates to install.'; exit 0; } Write-Host 'Updates to download:'; $UpdatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl; foreach ($update in $SearchResult.Updates) { Write-Host (\"  \" + $update.Title); $UpdatesToDownload.Add($update) | Out-Null; } if ($UpdatesToDownload.Count -gt 0) { Write-Host 'Downloading updates...'; $Downloader = $UpdateSession.CreateUpdateDownloader; $Downloader.Updates = $UpdatesToDownload; $DownloadResult = $Downloader.Download; if ($DownloadResult.ResultCode -ne 2) { Write-Error \"Download failed. Result code: $($DownloadResult.ResultCode)\"; exit 1; } Write-Host 'Updates downloaded. Installing...'; $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl; foreach ($update in $SearchResult.Updates) { if ($update.IsDownloaded) { $UpdatesToInstall.Add($update) | Out-Null } } if ($UpdatesToInstall.Count -gt 0) { $Installer = $UpdateSession.CreateUpdateInstaller; $Installer.Updates = $UpdatesToInstall; $InstallResult = $Installer.Install; Write-Host (\"Installation Result: \" + $InstallResult.ResultCode); if ($InstallResult.RebootRequired) { Write-Warning 'A reboot is required to complete the installation.'; } Write-Host 'Installation process finished.'; exit $InstallResult.ResultCode; } else { Write-Host 'No updates were successfully downloaded to install.'; exit 0; } } else { Write-Host 'No updates require downloading.'; exit 0; } } catch { Write-Error \"An error occurred during update installation: $($_.Exception.Message)\"; exit 1; }"
    ui_manager.display_info("Checking for Windows Updates...")
    stdout, stderr, code = _run_powershell_command_batch(ps_check_cmd)
    update_count = -1
    if code == 0 and stdout:
        try:
            match = re.search(r'Found (\d+) updates', stdout)
            if match: update_count = int(match.group(1))
            elif stdout.strip().isdigit(): update_count = int(stdout.strip())
        except: pass
    elif stderr: ui_manager.display_error(f"Update check failed: {stderr}"); return ps_install_cmd, True
    if update_count > 0:
        install = ui_manager.console.input(f"[bold yellow]{update_count} updates found. Install? (Requires Admin) (y/N): [/bold yellow]")
        if install.lower() == 'y': ui_manager.display_info("Attempting update installation..."); return ps_install_cmd, True
        else: ui_manager.display_info("Update installation cancelled."); return NO_EXEC_MARKER + "update cancelled", False
    elif update_count == 0: ui_manager.display_info("System is up-to-date.")
    return NO_EXEC_MARKER + "update check finished", False

# === User Management ===
def translate_passwd_guide(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='passwd', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"passwd: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]passwd - Change user password (guidance only)[/bold magenta]
[cyan]Description:[/cyan]
  Provides guidance on changing Windows password securely. Does not change passwords directly.

[cyan]Common Usage:[/cyan]
  passwd

[cyan]Guidance Provided:[/cyan]
  - Suggests Ctrl+Alt+Del or `net user <username> *` in Admin Prompt.
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: ui_manager.display_warning("passwd: Arguments are ignored.")

    ui_manager.display_warning("Swodnil cannot securely change passwords directly.") # This is part of the command's action
    ui_manager.display_info("To change your password:")
    ui_manager.display_info(" 1. Press Ctrl+Alt+Del and choose 'Change a password'.")
    ui_manager.display_info(" 2. OR, open an [bold]Administrator[/bold] Command Prompt or PowerShell and run:")
    username = os.getlogin(); ui_manager.console.print(f"    [cyan]net user {username} *[/cyan]")
    ui_manager.display_info("    (You will be prompted to enter the new password securely).")
    return NO_EXEC_MARKER + "passwd guide shown", False # Still NO_EXEC because it's a guide

# === Shell Internals / Environment ===
def translate_env_printenv(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='env/printenv', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"env/printenv: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]env, printenv - Print environment variables[/bold magenta]
[cyan]Description:[/cyan]
  Displays current environment variables. Mapped to `Get-ChildItem Env:`.

[cyan]Common Usage:[/cyan]
  env
  printenv

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments are ignored).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: ui_manager.display_warning(f"{parser.prog}: Arguments are ignored.")
    return "Get-ChildItem Env: | Sort-Object Name | Format-Table -AutoSize Name,Value", False

def translate_clear(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='clear', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"clear: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]clear - Clear the terminal screen[/bold magenta]
[cyan]Description:[/cyan]
  Clears terminal. Mapped to `Clear-Host`.

[cyan]Common Usage:[/cyan]
  clear

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: return NO_EXEC_MARKER + "clear: does not support arguments.", False
    return "Clear-Host", False

# === Simulated Commands ===
def _get_uptime() -> str: # Helper, no direct help
    if not psutil: return "N/A (psutil missing)"
    try: boot_time_timestamp = psutil.boot_time(); elapsed_seconds = time.time() - boot_time_timestamp; td = datetime.timedelta(seconds=elapsed_seconds); days = td.days; hours, remainder = divmod(td.seconds, 3600); minutes, _ = divmod(remainder, 60); uptime_str = (f"{days} day{'s' if days > 1 else ''}, " if days > 0 else "") + f"{hours:02}:{minutes:02}"; return uptime_str.strip(', ')
    except Exception: return "N/A"
def _get_package_count() -> str: # Helper
    stdout, _, code = _run_powershell_command_batch("winget list | Measure-Object")
    if code == 0 and stdout: match = re.search(r'Count\s+:\s+(\d+)', stdout); return f"{match.group(1)} (winget)" if match else "N/A"
    return "N/A"
def _get_gpu_info() -> str: # Helper
    stdout, _, code = _run_powershell_command_batch("(Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue).Name")
    if code == 0 and stdout: return stdout.splitlines()[0].strip() if stdout.strip() else "N/A"
    return "N/A"
def _get_winget_updates_count() -> int: # Helper
    stdout, _, code = _run_powershell_command_batch("try { $updates = winget upgrade | Select-String '^[^\\s]+'; return $updates.Count } catch { return -1 }")
    return int(stdout.strip()) if code == 0 and stdout and stdout.strip().isdigit() else -1
def _get_windows_updates_count() -> int: # Helper
    ps_cmd = "try { Import-Module PSWindowsUpdate -ErrorAction Stop -Scope CurrentUser -Force; return (Get-WindowsUpdate -MicrosoftUpdate).Count } catch { try { $session = (New-Object -ComObject Microsoft.Update.Session); $searcher = $session.CreateUpdateSearcher; $results = $searcher.Search(\"IsInstalled=0 and Type='Software'\"); return $results.Updates.Count } catch { return -1 } }"
    stdout, _, code = _run_powershell_command_batch(ps_cmd)
    return int(stdout.strip()) if code == 0 and stdout and stdout.strip().isdigit() else -1
def _get_pending_updates_count() -> tuple[int, int]: return (_get_winget_updates_count(), _get_windows_updates_count()) # Helper

def translate_neofetch_simulated(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='neofetch', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"neofetch (sim): {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]neofetch (simulated) - System information[/bold magenta]
[cyan]Description:[/cyan]
  Displays system info like Neofetch. Swodnil internal simulation.

[cyan]Common Usage:[/cyan]
  neofetch

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments are ignored).
[cyan]Notes:[/cyan]
  - Requires 'psutil' Python package.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: ui_manager.display_warning("neofetch (sim): Arguments are ignored.")
    if not psutil: return NO_EXEC_MARKER+"neofetch failed (psutil missing)", False
    
    ui_manager.console.print("\n[bold cyan]Swodnil System Info:[/bold cyan]")
    logo = ["╔══════════╦══════════╗","║██████████║██████████║","║██████████║██████████║","║██████████║██████████║","║██████████║██████████║","╠══════════╬══════════╣","║██████████║██████████║","║██████████║██████████║","║██████████║██████████║","║██████████║██████████║","╚══════════╩══════════╝"]; logo_color = "magenta"
    info = {};
    try: info['Hostname'] = platform.node()
    except: info['Hostname'] = "N/A"
    try: info['OS'] = f"{platform.system()} {platform.release()} ({platform.version()})"
    except: info['OS'] = "N/A"
    try: info['Uptime'] = _get_uptime()
    except: info['Uptime'] = "N/A"
    try: info['Packages'] = _get_package_count()
    except: info['Packages'] = "N/A"
    try: info['Terminal'] = f"Swodnil (PID:{os.getpid()})"
    except: info['Terminal'] = "N/A"
    try: info['CPU'] = platform.processor()
    except: info['CPU'] = "N/A"
    try: info['GPU'] = _get_gpu_info()
    except: info['GPU'] = "N/A"
    try: mem = psutil.virtual_memory(); info['Memory'] = f"{_format_bytes(mem.used)} / {_format_bytes(mem.total)} ({mem.percent}%)"
    except: info['Memory'] = "N/A"
    try:
        drive_letter = os.path.splitdrive(os.getcwd())[0] or 'C:'; drive_letter = drive_letter if drive_letter.endswith('\\') else drive_letter + '\\'
        disk = psutil.disk_usage(drive_letter); info[f'Storage({drive_letter})'] = f"{_format_bytes(disk.used)} / {_format_bytes(disk.total)} ({disk.percent}%)"
    except: info[f'Storage({os.path.splitdrive(os.getcwd())[0] or "C:"})'] = "N/A"
    try:
        winget_count, windows_count = _get_pending_updates_count(); update_parts = []
        if winget_count == 0: update_parts.append("Packages up to date")
        elif winget_count > 0: update_parts.append(f"[cyan]{winget_count} Packages Pending[/cyan]")
        else: update_parts.append("[dim]Packages check failed[/dim]")
        if windows_count == 0: update_parts.append("Windows up to date")
        elif windows_count > 0: update_parts.append(f"[cyan]{windows_count} Windows Updates Pending[/cyan]")
        else: update_parts.append("[dim]Windows check failed[/dim]")
        info['Updates'] = " | ".join(update_parts)
    except: info['Updates'] = "N/A"
    max_key_len = max(len(k) for k in info.keys()) if info else 0; output_lines = []
    info_items = list(info.items())
    for i in range(max(len(logo), len(info))):
        logo_part = f"[{logo_color}]{logo[i]}[/{logo_color}]" if i < len(logo) else " " * len(logo[0])
        info_part = ""; key_color="bold white"
        if i < len(info_items): key, value = info_items[i]; info_part = f"[{key_color}]{key.rjust(max_key_len)}[/]: {value}"
        output_lines.append(f" {logo_part}  {info_part}")
    ui_manager.console.print("\n".join(output_lines)); ui_manager.console.print()
    return SIMULATION_MARKER_PREFIX + "neofetch", False # This is a simulation, no PS command

def translate_cowsay_simulated(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='cowsay', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('message', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"cowsay (sim): {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]cowsay (simulated) - ASCII cow says a message[/bold magenta]
[cyan]Description:[/cyan]
  A talking cow simulation.

[cyan]Common Usage:[/cyan]
  cowsay [message...]

[cyan]Arguments:[/cyan]
  [message...]    Message for cow (defaults to "Moo?").
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    message = " ".join(parsed_args.message) if parsed_args.message else "Moo?"; max_width = 40
    lines = textwrap.wrap(message, width=max_width); bubble_width = max(len(line) for line in lines) if lines else 0
    bubble = [" " + "_" * (bubble_width + 2)];
    if not lines: bubble.append("< >")
    elif len(lines) == 1: bubble.append(f"< {lines[0].ljust(bubble_width)} >")
    else: bubble.append(f"/ {lines[0].ljust(bubble_width)} \\"); bubble.extend([f"| {lines[i].ljust(bubble_width)} |" for i in range(1, len(lines)-1)]); bubble.append(f"\\ {lines[-1].ljust(bubble_width)} /")
    bubble.append(" " + "-" * (bubble_width + 2)); cow = r"""
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||"""
    ui_manager.console.print("\n".join(bubble) + cow)
    return SIMULATION_MARKER_PREFIX + "cowsay", False

def translate_logangsay_simulated(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='logangsay', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('message', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"logangsay (sim): {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]logangsay (simulated) - Logan ASCII art says a message[/bold magenta]
[cyan]Description:[/cyan]
  Logan's custom ASCII art figure simulation.

[cyan]Common Usage:[/cyan]
  logangsay [message...]

[cyan]Arguments:[/cyan]
  [message...]    Message for Logan (defaults to "Yo!").
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    message = " ".join(parsed_args.message) if parsed_args.message else "Yo!"; max_width = 40
    lines = textwrap.wrap(message, width=max_width); bubble_width = max(len(line) for line in lines) if lines else 0
    bubble = [" " + "_" * (bubble_width + 2)]
    if not lines: bubble.append("< >")
    elif len(lines) == 1: bubble.append(f"< {lines[0].ljust(bubble_width)} >")
    else: bubble.append(f"/ {lines[0].ljust(bubble_width)} \\"); bubble.extend([f"| {lines[i].ljust(bubble_width)} |" for i in range(1, len(lines)-1)]); bubble.append(f"\\ {lines[-1].ljust(bubble_width)} /")
    bubble.append(" " + "-" * (bubble_width + 2))
    ui_manager.console.print("\n".join(bubble)); ui_manager.console.print(LOGAN_ART)
    return SIMULATION_MARKER_PREFIX + "logangsay", False

def translate_hollywood_simulated(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='hollywood', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    try: parsed_args, remaining_args = parser.parse_known_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"hollywood (sim): {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]hollywood (simulated) - Hacker-style console output[/bold magenta]
[cyan]Description:[/cyan]
  Fills console with scrolling green text. Ctrl+C to exit.

[cyan]Common Usage:[/cyan]
  hollywood

[cyan]Supported Flags:[/cyan]
  --help, -h      Show this help message.
  (Other arguments ignored).
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False
    if remaining_args: ui_manager.display_warning("hollywood (sim): Arguments are ignored.")

    ui_manager.console.print("[green]Entering Hollywood Mode... Press Ctrl+C to exit.[/green]"); time.sleep(0.5)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:'\",<.>/?\\|`~ "
    try:
        with ui_manager.console.capture(): # Suppress prompt during loop
             while True:
                line = "".join(random.choices(chars, k=random.randint(40, ui_manager.console.width - 1)))
                color = random.choice(["green", "bright_green", "dim green", "rgb(0,100,0)", "rgb(0,150,0)"])
                from rich.markup import escape # Ensure import
                ui_manager.console.print(f"[{color}]{escape(line)}", end='\n' if random.random() < 0.05 else '')
                time.sleep(random.uniform(0.005, 0.02))
    except KeyboardInterrupt: ui_manager.console.print("\n[green]...Exiting Hollywood Mode.[/green]")
    return SIMULATION_MARKER_PREFIX + "hollywood", False

def translate_which(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='which', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for which')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('command_name', nargs='?') # Optional for help
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"which: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]which - Locate a command[/bold magenta]
[cyan]Description:[/cyan]
  Shows full path of commands. Mapped to `Get-Command`.

[cyan]Common Usage:[/cyan]
  which <command_name>

[cyan]Arguments:[/cyan]
  <command_name>  Command to locate.
  --help, -h      Show this help message.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if not parsed_args.command_name:
        return NO_EXEC_MARKER + "which: missing command name. Try 'which --help'.", False
    command_name_str = shlex.quote(parsed_args.command_name)
    return f"Get-Command {command_name_str} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source", False

def translate_command(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='command', add_help=False)
    parser.add_argument('--help', action='store_true', help='Show Swodnil help for command')
    parser.add_argument('-h', dest='help_short', action='store_true', help='Alias for --help')
    parser.add_argument('-v', dest='v_flag', action='store_true') # For command -v
    parser.add_argument('command_to_find', nargs='?') # For command -v <cmd> or command --help
    parser.add_argument('remaining_args', nargs=argparse.REMAINDER) # For actual command execution
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: return NO_EXEC_MARKER + f"command: {e}", False

    if parsed_args.help or parsed_args.help_short:
        help_string = """
[bold magenta]command - Execute simple command or get command type[/bold magenta]
[cyan]Description:[/cyan]
  Swodnil supports `command -v <cmd>` (like `which`). Other uses treated as native.

[cyan]Supported Usage (Swodnil specific):[/cyan]
  command -v <command_name>   Prints command path/type.
  --help, -h                  Show this help message.

[cyan]Notes:[/cyan]
  - Other `command` invocations are passed to PowerShell.
"""
        return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip(), False

    if parsed_args.v_flag:
        if parsed_args.command_to_find:
            return translate_which([parsed_args.command_to_find]) # Pass as list to which
        else:
            return NO_EXEC_MARKER + "command -v: missing command name.", False
    
    # If not -v and not help, it's a native command execution attempt
    # We need to reconstruct the original command string for native execution
    # The `args` list originally passed to `translate_command` is what we want.
    # `parser.add_argument('remaining_args', nargs=argparse.REMAINDER)` helps, but
    # it's simpler to just pass the original `args` if no Swodnil-specific action is taken.
    # For `command <actual_command_and_its_args>`, we want to run `<actual_command_and_its_args>`
    # effectively stripping the leading `command`.
    # However, the Linux `command` built-in is for bypassing aliases/functions.
    # PowerShell's equivalent is more complex (e.g. `Get-Command -Type Application ... | Invoke-Expression`).
    # For Swodnil, if it's `command actual_cmd ...`, we'll treat `actual_cmd ...` as the new command.
    
    if parsed_args.command_to_find: # This is the actual command to run, e.g., `command ls -l`
        native_cmd_parts = [parsed_args.command_to_find] + parsed_args.remaining_args
        # ui_manager.display_warning(f"command: Treating '{' '.join(native_cmd_parts)}' as native execution.")
        return " ".join(native_cmd_parts), False # Let shell_core handle this as a new command line essentially
    
    # If just 'command' was typed (no -v, no --help, no actual command after it)
    return NO_EXEC_MARKER + "command: missing operand. Try 'command --help' or 'command -v <name>'.", False


# --- Command Map ---
TRANSLATION_MAP = {
    "ls": translate_ls, "cp": translate_cp, "mv": translate_mv, "rm": translate_rm,
    "mkdir": translate_mkdir, "pwd": translate_pwd, "touch": translate_touch,
    "find": translate_find, "df": translate_df,
    "chmod": translate_chmod, "chown": translate_chown,
    "cat": translate_cat, "grep": translate_grep, "head": translate_head, "tail": translate_tail,
    "hostname": translate_hostname, "uname": translate_uname, "ps": translate_ps,
    "kill": translate_kill, "killall": translate_kill, # translate_kill handles both
    "top": translate_top, "id": translate_id,
    "ifconfig": translate_ifconfig, "ip": translate_ifconfig,
    "whois": translate_whois, "dig": translate_dig,
    "wget": translate_wget, "curl": translate_curl,
    "env": translate_env_printenv, "printenv": translate_env_printenv, "clear": translate_clear,
    "apt": translate_apt, "apt-get": translate_apt, "dnf": translate_apt, "yum": translate_apt,
    "pacman": translate_apt, "zypper": translate_apt,
    "passwd": translate_passwd_guide,
    "do-release-upgrade": translate_do_release_upgrade_sim,
    "neofetch": translate_neofetch_simulated, "cowsay": translate_cowsay_simulated,
    "logangsay": translate_logangsay_simulated, "hollywood": translate_hollywood_simulated,
    "which": translate_which, "command": translate_command,
}

# --- Main Processing Function ---
def process_command(command: str, args: list[str]) -> tuple[str | None, bool]:
    cmd_lower = command.lower()
    handler = TRANSLATION_MAP.get(cmd_lower)

    if handler:
        try:
            # Handler will now parse its own args, including --help
            handler_output = handler(args) 

            if isinstance(handler_output, tuple) and len(handler_output) == 2 and isinstance(handler_output[1], bool):
                result, needs_elevation = handler_output
                if not (isinstance(result, str) or result is None):
                     ui_manager.display_error(f"Internal error: Translator for '{command}' returned invalid result type: {type(result)}")
                     return NO_EXEC_MARKER + "handler type error", False
                return result, needs_elevation
            else: # Should not happen if all handlers are updated
                ui_manager.display_warning(f"Internal warning: Translator for '{command}' did not return (result, bool) tuple. Got: {type(handler_output)}.")
                return str(handler_output) if handler_output is not None else None, False
        except Exception as e:
            ui_manager.display_error(f"Internal Swodnil error processing '{command}': {e}")
            import traceback; traceback.print_exc()
            return NO_EXEC_MARKER + "handler exception", False
    else: # Command not in TRANSLATION_MAP (native command)
        if args and (args[0] == "--help" or args[0] == "-h"):
            # For unknown commands, if --help is passed, provide a generic Swodnil note
            # and suggest trying Get-Help for PowerShell.
            help_string = f"""
[bold magenta]{command} --help (Native/Unknown Command)[/bold magenta]
[cyan]Description:[/cyan]
  `{command}` is not a Swodnil translated command.
  If it's a native Windows executable or PowerShell cmdlet, it might support `--help` directly,
  or you can try `Get-Help {shlex.quote(command)}` in PowerShell.

[cyan]Swodnil Action:[/cyan]
  Swodnil will attempt to run `Get-Help {shlex.quote(command)} -ErrorAction SilentlyContinue`.
  Alternatively, you can try running `{shlex.quote(command)} --help` directly if you suspect it's an EXE.
"""
            # Return the PowerShell Get-Help command for execution.
            # The help string is displayed by shell_core via the HELP_MARKER_PREFIX.
            return NO_EXEC_MARKER + HELP_MARKER_PREFIX + help_string.strip() + f"\n\n[cyan]Equivalent PS Help Command to try:[/cyan]\n  Get-Help {shlex.quote(command)} -ErrorAction SilentlyContinue", False
        return None, False # Native command, no Swodnil translation, no Swodnil help.

# --- Special Path Mappings for 'cat' (condensed for brevity, content unchanged) ---
SPECIAL_CAT_PATHS = {
    "/etc/fstab": (r"Write-Host '# Windows Volume Information (Simulated /etc/fstab)' -ForegroundColor Gray; Write-Host '# <file system>                              <mount point>   <type>     <options>       <dump> <pass>'; Get-Volume | Where-Object { $_.DriveLetter } | ForEach-Object { $fs = $_.Path; $mp = \"$($_.DriveLetter):\\\"; $type = if ($_.FileSystem) { $_.FileSystem } else { 'unknown' }; $options = 'defaults'; $dump = 0; $pass = 0; Write-Host (\"{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}\" -f $fs, $mp, $type, $options, $dump, $pass); }; Get-CimInstance Win32_PageFileSetting | ForEach-Object { $fs = $_.Name; $mp = 'swap'; $type = 'swap'; $options = 'defaults'; $dump = 0; $pass = 0; Write-Host (\"{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}\" -f $fs, $mp, $type, $options, $dump, $pass); }; Get-PSDrive -PSProvider FileSystem | Where-Object { $_.DisplayRoot -like '\\*' } | ForEach-Object { $fs = $_.DisplayRoot; $mp = \"$($_.Name):\\\"; $type = 'cifs'; $options = 'defaults'; $dump = 0; $pass = 0; Write-Host (\"{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}\" -f $fs, $mp, $type, $options, $dump, $pass); }", True),
    "/etc/hosts": (r'Get-Content -Path "$env:SystemRoot\System32\drivers\etc\hosts"', False),
    "/etc/resolv.conf": (r"Write-Host '# Windows DNS Configuration (Simulated /etc/resolv.conf)' -ForegroundColor Gray; Get-DnsClient | Select-Object -ExpandProperty ConnectionSpecificSuffix | Where-Object {$_} | ForEach-Object { Write-Host (\"search {0}\" -f $_); }; $globalSearch = (Get-DnsClientGlobalSetting).SuffixSearchList; if ($globalSearch) { Write-Host (\"search {0}\" -f ($globalSearch -join ' ')) }; Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.ServerAddresses} | ForEach-Object { Write-Host (\"# Interface $($_.InterfaceAlias) ($($_.InterfaceIndex))\" -ForegroundColor Gray); $_.ServerAddresses | ForEach-Object { Write-Host \"nameserver $_\" }; }", False),
    "/proc/cpuinfo": (r"Write-Host '# Windows CPU Information (Simulated /proc/cpuinfo)' -ForegroundColor Gray; $processors = Get-CimInstance Win32_Processor; $processorIndex = 0; foreach ($proc in $processors) { Write-Host \"processor`t: $processorIndex\"; Write-Host \"vendor_id`t: $($proc.Manufacturer)\"; Write-Host \"model name`t: $($proc.Name)\"; Write-Host \"cpu family`t: $($proc.Family)\"; Write-Host \"model`t`t: $($proc.Description)\"; Write-Host \"stepping`t: $($proc.Stepping)\"; Write-Host \"cpu MHz`t`t: $($proc.CurrentClockSpeed)\"; Write-Host \"cache size`t: $($proc.L2CacheSize) KB (L2) / $($proc.L3CacheSize) KB (L3)\"; Write-Host \"physical id`t: $($proc.SocketDesignation)\"; $cores = $proc.NumberOfCores; $logical = $proc.NumberOfLogicalProcessors; Write-Host \"cpu cores`t: $cores\"; Write-Host \"siblings`t: $logical\"; Write-Host \"flags`t`t: (Not directly available, see Get-ComputerInfo for features)\"; Write-Host \"\"; $processorIndex++; }", True),
    "/proc/meminfo": (r"Write-Host '# Windows Memory Information (Simulated /proc/meminfo)' -ForegroundColor Gray; $mem = Get-CimInstance Win32_OperatingSystem; $cs = Get-CimInstance Win32_ComputerSystem; $pm = Get-Counter '\Memory\Available KBytes'; $totalMB = [math]::Round($mem.TotalVisibleMemorySize / 1024); $freeMB = [math]::Round($mem.FreePhysicalMemory / 1024); $availMB = [math]::Round($pm.CounterSamples[0].CookedValue / 1024); Write-Host (\"MemTotal:`t{0,10} kB\" -f $mem.TotalVisibleMemorySize); Write-Host (\"MemFree:`t{0,10} kB\" -f $mem.FreePhysicalMemory); Write-Host (\"MemAvailable:`t{0,10} kB\" -f ($availMB * 1024)); $swapTotal = (Get-CimInstance Win32_PageFileUsage | Measure-Object -Property AllocatedBaseSize -Sum).Sum / 1KB; $swapUsed = (Get-CimInstance Win32_PageFileUsage | Measure-Object -Property CurrentUsage -Sum).Sum / 1KB; $swapFree = $swapTotal - $swapUsed; Write-Host (\"SwapTotal:`t{0,10} kB\" -f $swapTotal); Write-Host (\"SwapFree:`t{0,10} kB\" -f $swapFree); Write-Host (\"Buffers:`t{0,10} kB\" -f 0); Write-Host (\"Cached:`t`t{0,10} kB\" -f 0); Write-Host (\"Slab:`t`t{0,10} kB\" -f 0);", False),
    "/etc/os-release": (r"Write-Host '# Windows OS Information (Simulated /etc/os-release)' -ForegroundColor Gray; $os = Get-CimInstance Win32_OperatingSystem; $ci = Get-ComputerInfo; $name = $os.Caption; $id = $name -replace '[^a-zA-Z0-9]+', '' -replace 'Microsoft', '' | Out-String; $id = $id.Trim().ToLower(); Write-Host (\"NAME=`\"{0}`\"\" -f $name); Write-Host (\"VERSION=`\"{0} (Build {1})`\"\" -f $os.Version, $os.BuildNumber); Write-Host (\"ID={0}\" -f $id); Write-Host (\"VERSION_ID=`\"{0}`\"\" -f $os.Version); Write-Host (\"PRETTY_NAME=`\"{0}`\"\" -f $name); Write-Host (\"ANSI_COLOR=`\"0;34`\"\"); Write-Host (\"HOME_URL=`\"https://www.microsoft.com/windows/`\"\"); Write-Host (\"SUPPORT_URL=`\"https://support.microsoft.com/windows`\"\"); Write-Host (\"BUG_REPORT_URL=`\"https://support.microsoft.com/windows`\"\");", False),
    "/etc/lsb-release": (r"Write-Host '# Windows OS Information (Simulated /etc/lsb-release)' -ForegroundColor Gray; $os = Get-CimInstance Win32_OperatingSystem; $name = $os.Caption; $id = $name -replace '[^a-zA-Z0-9]+', '' -replace 'Microsoft', '' | Out-String; $id = $id.Trim().ToLower(); Write-Host (\"DISTRIB_ID={0}\" -f $id); Write-Host (\"DISTRIB_RELEASE={0}\" -f $os.Version); Write-Host (\"DISTRIB_CODENAME=Windows\"); Write-Host (\"DISTRIB_DESCRIPTION=`\"{0}`\"\" -f $name);", False),
    "/etc/passwd": ("'# Showing current user info via whoami. For full user list use: Get-LocalUser' -ForegroundColor Gray; whoami /user /fo list", False),
    "/etc/group": ("'# Showing current user groups via whoami. For full group list use: Get-LocalGroup' -ForegroundColor Gray; whoami /groups /fo list", False),
}

# --- Direct Execution Test Block (If needed) ---
if __name__ == "__main__":
    if not hasattr(ui_manager, 'console') or ui_manager.console is None:
         from rich.console import Console
         ui_manager.console = Console()

    # Test a few commands
    test_commands_for_help = [
        "ls --help", "cp -h", "apt --help", "unknowncmd --help", "cat -h"
    ]
    print("--- Testing --help Functionality (Direct Run) ---")
    for cmd_str in test_commands_for_help:
        print(f"\n[bold gold1 on navy_blue]>>> Testing: {cmd_str}[/bold gold1 on navy_blue]")
        parts = shlex.split(cmd_str) if cmd_str else [""]
        command = parts[0] if parts else ""
        if not command: continue
        args_list = parts[1:]
        
        result_tuple = process_command(command, args_list)
        
        if isinstance(result_tuple, tuple) and len(result_tuple) == 2:
            result, needs_elevation = result_tuple
            if isinstance(result, str) and result.startswith(NO_EXEC_MARKER):
                help_content_marker = result[len(NO_EXEC_MARKER):]
                if help_content_marker.startswith(HELP_MARKER_PREFIX):
                    actual_help_text = help_content_marker[len(HELP_MARKER_PREFIX):].strip()
                    from rich.panel import Panel
                    from rich.text import Text
                    ui_manager.console.print(Panel(Text.from_markup(actual_help_text), border_style="green", title=f"Help: {command}"))
                else:
                    print(f"  NON-EXEC (no help marker): {result}") # e.g. error message
            elif result is None and command.lower() not in TRANSLATION_MAP : # Native command without --help
                print(f"  NATIVE: To be handled by PowerShell directly for command '{command}'.")
            else: # Translated command to execute
                print(f"  COMMAND: {result} (Elevate: {needs_elevation})")
        else:
            print(f"  ERROR: Unexpected result from process_command: {result_tuple}")
