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
                    ++++++++=+++=+=+===========================-------------------------------================+++++++++++++++**********###############%%#**                    
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
SIMULATION_MARKER_PREFIX = "#SIMULATION_EXEC:" # Marker for simulations that print directly
NO_EXEC_MARKER = "#NO_EXEC:" # Marker for commands that should not execute anything (e.g., failed translation, guide commands)

# --- Argument Parser Error Handling ---
class NonExitingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"Argument Error: {message}")
    def _print_message(self, message, file=None):
        # Suppress argparse default error printing
        pass

# --- Helper Functions ---
def _run_powershell_command(command: str, env: dict | None = None) -> tuple[str | None, str | None, int]:
    """Helper to run a PS command and return stdout, stderr, returncode."""
    try:
        process = subprocess.run(
            ['powershell', '-NoProfile', '-Command', command],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            shell=False, check=False, env=env # Pass environment if provided
        )
        return process.stdout.strip(), process.stderr.strip(), process.returncode
    except FileNotFoundError:
        return None, "PowerShell not found in PATH.", -1
    except Exception as e:
        return None, f"Failed to execute PowerShell command: {e}", -1

def _format_bytes(byte_count: int | None) -> str:
    """Convert bytes to human-readable format (GiB)."""
    if byte_count is None: return "N/A"
    if byte_count < 1024: return f"{byte_count} B"
    kib = byte_count / 1024
    if kib < 1024: return f"{kib:.1f} KiB"
    mib = kib / 1024
    if mib < 1024: return f"{mib:.1f} MiB"
    gib = mib / 1024
    return f"{gib:.2f} GiB"

# --- Translation Functions ---


# === File System ===
def translate_ls(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='ls', add_help=False)
    parser.add_argument('-l', action='store_true')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-R', '--recursive', action='store_true')
    parser.add_argument('-t', action='store_true') # Sort by time
    parser.add_argument('-S', action='store_true') # Sort by size
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('paths', nargs='*', default=['.']) # Default to current dir if no paths
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"ls: {e}"); return NO_EXEC_MARKER + "ls failed"
    base_cmd = "Get-ChildItem"; params = []; post_cmds = []
    params.extend([shlex.quote(p) for p in parsed_args.paths])
    if parsed_args.all: params.append("-Force")
    if parsed_args.recursive: params.append("-Recurse")

    sort_prop = None
    sort_desc = False
    if parsed_args.t: sort_prop = "LastWriteTime"
    if parsed_args.S: sort_prop = "Length"
    if sort_prop:
        sort_cmd = f"Sort-Object -Property {sort_prop}"
        # Default PS sort is ascending. Linux -t/-S default is descending.
        # -r reverses the sort direction.
        if not parsed_args.reverse: sort_desc = True
        if sort_desc: sort_cmd += " -Descending"
        post_cmds.append(sort_cmd)
    elif parsed_args.reverse: # Reverse default name sort
        post_cmds.append("Sort-Object -Property Name -Descending")

    if parsed_args.l:
         # Try a more detailed Format-Table similar to ls -l
         # Mode, Links(N/A), Owner, Group(N/A), Size, Date, Name
         format_expression = (
            '@{N="Mode";E={($_.Mode -replace "-","").PadRight(10)}}, '
            '@{N="Owner";E={(Get-Acl $_.FullName).Owner}}, '
            '@{N="Size";E={$_.Length}}, '
            '@{N="LastWriteTime";E={$_.LastWriteTime.ToString("MMM dd HH:mm")}}, '
            '@{N="Name";E={$_.Name}}'
         )
         post_cmds.append(f"Format-Table {format_expression} -AutoSize")
    # else: Default format is fine

    full_cmd = f"{base_cmd} {' '.join(params)}"
    if post_cmds: full_cmd += " | " + " | ".join(post_cmds)
    return full_cmd

def translate_cp(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='cp', add_help=False); parser.add_argument('-r', '-R', '--recursive', action='store_true'); parser.add_argument('-i', '--interactive', action='store_true'); parser.add_argument('-v', '--verbose', action='store_true'); parser.add_argument('-f', '--force', action='store_true'); parser.add_argument('source', nargs='+'); parser.add_argument('destination')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"cp: {e}"); return NO_EXEC_MARKER + "cp failed"
    base_cmd = "Copy-Item"; params = [];
    if parsed_args.recursive: params.append("-Recurse")
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    # Handle multiple sources to single destination directory
    if len(parsed_args.source) > 1 and not os.path.isdir(parsed_args.destination):
         ui_manager.display_error("cp: target must be a directory when copying multiple files")
         return NO_EXEC_MARKER + "cp failed: target not directory"
    params.extend([f"-Path {shlex.quote(src)}" for src in parsed_args.source])
    params.append(f"-Destination {shlex.quote(parsed_args.destination)}")
    return f"{base_cmd} {' '.join(params)}"

def translate_mv(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='mv', add_help=False); parser.add_argument('-i', '--interactive', action='store_true'); parser.add_argument('-v', '--verbose', action='store_true'); parser.add_argument('-f', '--force', action='store_true'); parser.add_argument('source'); parser.add_argument('destination')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"mv: {e}"); return NO_EXEC_MARKER + "mv failed"
    base_cmd = "Move-Item"; params = []
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    params.append(f"-Path {shlex.quote(parsed_args.source)}")
    params.append(f"-Destination {shlex.quote(parsed_args.destination)}")
    return f"{base_cmd} {' '.join(params)}"

def translate_rm(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='rm', add_help=False); parser.add_argument('-r', '-R', '--recursive', action='store_true'); parser.add_argument('-f', '--force', action='store_true'); parser.add_argument('-i', '--interactive', action='store_true'); parser.add_argument('-v', '--verbose', action='store_true'); parser.add_argument('files', nargs='+')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"rm: {e}"); return NO_EXEC_MARKER + "rm failed"
    base_cmd = "Remove-Item"; params = []
    if parsed_args.recursive: params.append("-Recurse")
    if parsed_args.force: params.append("-Force")
    elif parsed_args.interactive: params.append("-Confirm")
    if parsed_args.verbose: params.append("-Verbose")
    params.extend([shlex.quote(f) for f in parsed_args.files])
    # Basic safety check - don't easily allow removing C:\ or similar without -rf
    # This is not foolproof
    for f in parsed_args.files:
        abs_path = os.path.abspath(f)
        drive = os.path.splitdrive(abs_path)[0].upper() + "\\"
        if abs_path == drive and not (parsed_args.recursive and parsed_args.force):
            ui_manager.display_error(f"rm: Refusing to remove root directory '{abs_path}' without -rf")
            return NO_EXEC_MARKER + "rm protection"
    return f"{base_cmd} {' '.join(params)}"

def translate_mkdir(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='mkdir', add_help=False); parser.add_argument('-p', '--parents', action='store_true'); parser.add_argument('-v', '--verbose', action='store_true'); parser.add_argument('directories', nargs='+')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"mkdir: {e}"); return NO_EXEC_MARKER + "mkdir failed"
    base_cmd = "New-Item -ItemType Directory"; params = []
    if parsed_args.parents: params.append("-Force") # -Force creates parents
    if parsed_args.verbose: params.append("-Verbose")
    # New-Item can take multiple paths if separated, but let's stick to semicolon loop for clarity
    commands = [f"{base_cmd} {' '.join(params)} -Path {shlex.quote(directory)}" for directory in parsed_args.directories]
    return " ; ".join(commands)

def translate_pwd(args: list[str]) -> str | None:
    if args: ui_manager.display_error("pwd: does not support arguments."); return NO_EXEC_MARKER + "pwd failed"
    # Get-Location gives object, $PWD gives string directly often
    # return "Get-Location | Select-Object -ExpandProperty Path"
    return "Write-Host $PWD.Path" # Simpler, more direct

def translate_touch(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='touch', add_help=False); parser.add_argument('files', nargs='+')
    # TODO: Add flags like -t timestamp, -d date, -r reference_file
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"touch: {e}"); return NO_EXEC_MARKER + "touch failed"
    commands = []
    timestamp = "Get-Date" # Default to now
    # Add flag handling here if implementing time specification
    for file in parsed_args.files:
        quoted_file = shlex.quote(file)
        # Using New-Item is safer than Set-Content as it won't clear the file
        cmd = (f"if (-not (Test-Path {quoted_file})) {{ New-Item -Path {quoted_file} -ItemType File -Force | Out-Null }}; "
               f"(Get-Item {quoted_file}).LastWriteTime = ({timestamp})")
        commands.append(cmd)
    return " ; ".join(commands)

def translate_find(args: list[str]) -> str | None:
    """Translates basic find commands to Get-ChildItem."""
    parser = NonExitingArgumentParser(prog='find', add_help=False)
    parser.add_argument('path', nargs='?', default='.', help='Starting path')
    parser.add_argument('-name', help='Filter by name (wildcards allowed)')
    parser.add_argument('-iname', help='Case-insensitive name filter')
    parser.add_argument('-type', choices=['f', 'd'], help='Filter by type (f=file, d=directory)')
    # parser.add_argument('-print', action='store_true', help='Print names (default)') # Implicit
    # parser.add_argument('-delete', action='store_true') # Potentially dangerous, map to | Remove-Item
    # parser.add_argument('-exec', nargs='+') # Very complex to map securely

    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"find: {e}"); return NO_EXEC_MARKER + "find failed"

    base_cmd = "Get-ChildItem"
    params = [f"-Path {shlex.quote(parsed_args.path)}", "-Recurse"]
    post_cmds = []

    name_filter = None
    if parsed_args.name:
        name_filter = parsed_args.name
    elif parsed_args.iname:
        name_filter = parsed_args.iname # PS filter is case-insensitive by default

    if name_filter:
        params.append(f"-Filter {shlex.quote(name_filter)}") # Use -Filter for efficiency if possible

    if parsed_args.type:
        if parsed_args.type == 'f':
            params.append("-File")
        elif parsed_args.type == 'd':
            params.append("-Directory")

    # if parsed_args.delete:
    #    post_cmds.append("Remove-Item -Force -Recurse") # Be careful with this!

    full_cmd = f"{base_cmd} {' '.join(params)}"
    if post_cmds: full_cmd += " | " + " | ".join(post_cmds)
    return full_cmd

# === Permissions ===
def translate_chmod(args: list[str]) -> str | None:
    """Translates VERY basic chmod +/- modes to icacls."""
    # WARNING: Windows ACLs are fundamentally different from POSIX modes.
    # This translation is extremely limited and approximate.
    ui_manager.display_warning("chmod translation is limited and approximate due to ACL differences.")
    parser = NonExitingArgumentParser(prog='chmod', add_help=False)
    parser.add_argument('mode', help='Mode string (e.g., +x, u+w, 755 - limited support)')
    parser.add_argument('file', help='File or directory')
    try:
        parsed_args = parser.parse_args(args)
        mode = parsed_args.mode
        file = parsed_args.file
        quoted_file = shlex.quote(file)
    except ValueError as e:
        ui_manager.display_error(f"chmod: {e}"); return NO_EXEC_MARKER + "chmod failed"

    # Basic +/- mode mapping for current user (approximation)
    # Use icacls: /grant grants permissions, /deny denies, /remove removes grants/denies
    # Permissions: F=Full, M=Modify, RX=Read&Execute, R=Read, W=Write
    # User: Use '%USERNAME%' which PowerShell should expand, or BUILTIN\Users etc.

    commands = []
    # Extremely simplified mapping for +w / -w for current user
    if mode == '+w':
        # Grant Modify rights to current user
        commands.append(f'icacls {quoted_file} /grant "%USERNAME%":(M)')
    elif mode == '-w':
        # Deny Write rights to current user
        commands.append(f'icacls {quoted_file} /deny "%USERNAME%":(W)')
    # Simple +x mapping (Grant Read&Execute)
    elif mode == '+x':
        commands.append(f'icacls {quoted_file} /grant "%USERNAME%":(RX)')
    # Rudimentary numeric mode (only handles basic cases like 777, 755, 644 for owner/users group)
    # THIS IS HIGHLY APPROXIMATE AND LIKELY INSUFFICIENT FOR REAL USE CASES
    elif re.match(r'^[0-7]{3}$', mode):
        ui_manager.display_warning("Numeric chmod modes are poorly mapped to Windows ACLs.")
        owner_perm = int(mode[0])
        group_perm = int(mode[1]) # Map group to BUILTIN\Users
        # other_perm = int(mode[2]) # Hard to map 'other' reliably

        # Reset permissions first? icacls /reset ? (Dangerous)
        # Grant based on numbers (simplistic)
        owner_acl = []
        if owner_perm >= 4: owner_acl.append("R")
        if owner_perm >= 6: owner_acl.append("W")
        if owner_perm in [1, 3, 5, 7]: owner_acl.append("X")
        if owner_acl: commands.append(f'icacls {quoted_file} /grant "%USERNAME%":({"".join(owner_acl)})')

        users_acl = []
        if group_perm >= 4: users_acl.append("R")
        if group_perm >= 6: users_acl.append("W") # Often Modify is needed for write access
        if group_perm in [1, 3, 5, 7]: users_acl.append("X")
        if users_acl: commands.append(f'icacls {quoted_file} /grant "BUILTIN\\Users":({"".join(users_acl)})')

    else:
        ui_manager.display_error(f"chmod: Unsupported mode string '{mode}'. Only basic +/-w, +x and simple numeric modes partially supported.")
        return NO_EXEC_MARKER + "chmod mode unsupported"

    if not commands:
        ui_manager.display_error(f"chmod: Could not translate mode '{mode}'.")
        return NO_EXEC_MARKER + "chmod translation failed"

    # Add /T for recursion on directories? Maybe mimic -R flag?
    # parser.add_argument('-R', '--recursive', action='store_true')
    # if parsed_args.recursive and os.path.isdir(file):
    #    params.append("/T") # Add /T for recursion to each icacls command

    return " ; ".join(commands)

def translate_chown(args: list[str]) -> str | None:
    ui_manager.display_error("chown: Changing ownership is complex and differs significantly on Windows.")
    ui_manager.display_info("Use 'icacls <file> /setowner <user>' or Get-Acl/Set-Acl in PowerShell (may require admin rights).")
    return NO_EXEC_MARKER + "chown not supported"

# === Text Processing ===
def translate_cat(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='cat', add_help=False)
    parser.add_argument('-n', '--number', action='store_true', help='Number output lines')
    parser.add_argument('files', nargs='*') # Allow reading from stdin if no files
    try:
        parsed_args = parser.parse_args(args)
    except ValueError as e:
        ui_manager.display_error(f"cat: {e}")
        return NO_EXEC_MARKER + "cat failed", False # Return tuple

    # --- Check for Special Path Handling ---
    if len(parsed_args.files) == 1:
        normalized_path = parsed_args.files[0].lower().replace('\\', '/')
        if normalized_path in SPECIAL_CAT_PATHS:
            powershell_cmd_tuple = SPECIAL_CAT_PATHS[normalized_path]
            powershell_cmd, needs_elevation = powershell_cmd_tuple

            if parsed_args.number:
                ui_manager.display_warning(f"cat: Flag '-n' ignored when displaying equivalent for '{parsed_args.files[0]}'")

            # Context comment handling (same as before)
            context_comment = f"# Showing Windows equivalent for: {parsed_args.files[0]}"
            if not powershell_cmd.strip().startswith("Write-Host '# Windows"):
                 final_cmd = f"Write-Host '{context_comment}' -ForegroundColor Gray; {powershell_cmd}"
            else:
                 final_cmd = powershell_cmd

            return final_cmd, needs_elevation # Return tuple

    # --- Default Behavior (Get-Content or Stdin) ---
    base_cmd = "Get-Content"
    params = []
    post_cmds = []

    if not parsed_args.files:
        pass # Relies on PowerShell's pipeline input for Get-Content
    else:
        params.extend([f"-LiteralPath {shlex.quote(f)}" for f in parsed_args.files])
        params.append("-ErrorAction SilentlyContinue")

    if parsed_args.number:
        post_cmds.append('$global:lineNumber = 0; Foreach-Object { $global:lineNumber++; Write-Host ("{0,6}  {1}" -f $global:lineNumber, $_) }')

    full_cmd = f"{base_cmd} {' '.join(params)}"
    if post_cmds:
        full_cmd += " | " + " | ".join(post_cmds)

    return full_cmd, False # Default cat does not need elevation

# === Text Processing ===

def translate_grep(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='grep', add_help=False); parser.add_argument('-i', '--ignore-case', action='store_true'); parser.add_argument('-v', '--invert-match', action='store_true'); parser.add_argument('-n', '--line-number', action='store_true'); parser.add_argument('-r','-R', '--recursive', action='store_true'); parser.add_argument('pattern'); parser.add_argument('files', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"grep: {e}"); return NO_EXEC_MARKER + "grep failed", False

    select_string_cmd = "Select-String"
    ss_params = [f"-Pattern {shlex.quote(parsed_args.pattern)}"]
    (parsed_args.ignore_case) and ss_params.append("-CaseSensitive:$false") or ss_params.append("-CaseSensitive")
    if parsed_args.invert_match: ss_params.append("-NotMatch")
    # -n is handled implicitly by Select-String object output, format if needed

    result_cmd = ""
    if not parsed_args.files:
        # Handle stdin - assume input piped to Select-String
        result_cmd = f"{select_string_cmd} {' '.join(ss_params)}"
    elif parsed_args.recursive:
        # Use Get-ChildItem | Select-String for recursion
        gci_params = ["-Recurse", "-File", "-ErrorAction SilentlyContinue"] # Search only files, ignore errors on GCI
        # Need to quote file paths if they are patterns for GCI
        gci_params.extend([shlex.quote(f) for f in parsed_args.files])
        result_cmd = f"Get-ChildItem {' '.join(gci_params)} | {select_string_cmd} {' '.join(ss_params)}"
    else:
        # Search specific files
        ss_params.append("-LiteralPath") # Use LiteralPath for safety
        ss_params.extend([shlex.quote(f) for f in parsed_args.files])
        # Add error action to Select-String as well for missing files
        ss_params.append("-ErrorAction SilentlyContinue")
        result_cmd = f"{select_string_cmd} {' '.join(ss_params)}"

    return result_cmd, False # grep doesn't typically need elevation


def translate_head_tail(cmd_name: str, args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False); parser.add_argument('-n', '--lines', type=int, default=10); (cmd_name == 'tail') and parser.add_argument('-f', '--follow', action='store_true'); parser.add_argument('file', nargs='?', default=None) # Allow stdin
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed", False

    base_cmd = "Get-Content"; params = []
    if parsed_args.file:
        params.append(f"-LiteralPath {shlex.quote(parsed_args.file)}")
        params.append("-ErrorAction SilentlyContinue") # Handle file not found
    # else: assumes reading from pipeline/stdin

    selector = "-First" if cmd_name == 'head' else "-Last" # Use -First/-Last for pipeline compatibility
    # selector = "-Head" if cmd_name == 'head' else "-Tail" # These work better directly with Get-Content file path

    # Decide which selector to use based on whether input is likely piped or from file
    if not parsed_args.file:
        # Likely pipeline input, use -First / -Last
        selector = "-First" if cmd_name == 'head' else "-Last"
        # Build the command differently for pipeline
        if cmd_name == 'tail' and parsed_args.follow:
            ui_manager.display_error("tail -f: cannot follow pipeline input.")
            return NO_EXEC_MARKER + "tail -f failed", False
        return f"Select-Object {selector} {parsed_args.lines}", False
    else:
        # File input, use -Head / -Tail directly on Get-Content
        selector = "-Head" if cmd_name == 'head' else "-Tail"
        params.append(f"{selector} {parsed_args.lines}")
        if cmd_name == 'tail' and parsed_args.follow:
             params.append("-Wait")
        return f"{base_cmd} {' '.join(params)}", False

def translate_head(args: list[str]) -> tuple[str | None, bool]: return translate_head_tail('head', args)
def translate_tail(args: list[str]) -> tuple[str | None, bool]: return translate_head_tail('tail', args)

# === System Information & Management ===
def translate_hostname(args: list[str]) -> tuple[str | None, bool]:
    if args: ui_manager.display_error("hostname: does not support arguments."); return NO_EXEC_MARKER + "hostname failed", False
    return 'Write-Host $env:COMPUTERNAME', False

def translate_uname(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='uname', add_help=False); parser.add_argument('-a', '--all', action='store_true'); parser.add_argument('-s', '--kernel-name', action='store_true'); parser.add_argument('-n', '--nodename', action='store_true'); parser.add_argument('-r', '--kernel-release', action='store_true'); parser.add_argument('-v', '--kernel-version', action='store_true'); parser.add_argument('-m', '--machine', action='store_true'); parser.add_argument('-o', '--operating-system', action='store_true')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"uname: {e}"); return NO_EXEC_MARKER + "uname failed", False
    results = []; sys_system = platform.system(); sys_release = platform.release(); sys_version = platform.version(); sys_machine = platform.machine(); sys_node = platform.node()
    if not any([parsed_args.all, parsed_args.kernel_name, parsed_args.nodename, parsed_args.kernel_release, parsed_args.kernel_version, parsed_args.machine, parsed_args.operating_system]): parsed_args.kernel_name = True
    if parsed_args.kernel_name or parsed_args.all: results.append(sys_system)
    if parsed_args.nodename or parsed_args.all: results.append(sys_node)
    if parsed_args.kernel_release or parsed_args.all: results.append(sys_release)
    if parsed_args.kernel_version or parsed_args.all: results.append(sys_version)
    if parsed_args.machine or parsed_args.all: results.append(sys_machine)
    if parsed_args.operating_system or parsed_args.all: (sys_system not in results) and results.append(sys_system)
    return f"Write-Host \"{' '.join(results)}\"", False

def translate_df(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='df', add_help=False); parser.add_argument('-h', '--human-readable', action='store_true'); parser.add_argument('files', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"df: {e}"); return NO_EXEC_MARKER + "df failed", False

    # Get-Volume might need elevation for certain details, Get-PSDrive usually doesn't
    # Let's try Get-PSDrive first as it's less likely to require elevation
    base_cmd = "Get-PSDrive"
    params = ["-PSProvider FileSystem"]
    needs_elevation = False # Assume false for Get-PSDrive

    # Format-Bytes helper function (defined within the command string)
    format_bytes_func = (
        "$FormatBytes = {param($bytes) if ($bytes -eq $null) {'N/A'} elseif ($bytes -ge 1GB) {{'{0:N2} GiB' -f ($bytes / 1GB)}} "
        "elseif ($bytes -ge 1MB) {{'{0:N1} MiB' -f ($bytes / 1MB)}} elseif ($bytes -ge 1KB) {{'{0:N1} KiB' -f ($bytes / 1KB)}} "
        "else {{'{0} B' -f $bytes}}}; "
    )

    # Define properties to select and format
    properties = [
        "Name",
        "@{N='Size';E={($_.Used + $_.Free)}}",
        "Used",
        "Free",
        "@{N='Use%';E={if (($_.Used + $_.Free) -gt 0) {[int]($_.Used / ($_.Used + $_.Free) * 100)} else {0} }}",
        "Root" # Mountpoint
    ]
    human_readable_properties = [
        "Name",
        "@{N='Size';E={& $FormatBytes ($_.Used + $_.Free)}}",
        "@{N='Used';E={& $FormatBytes $_.Used}}",
        "@{N='Free';E={& $FormatBytes $_.Free}}",
        "@{N='Use%';E={if (($_.Used + $_.Free) -gt 0) {[int]($_.Used / ($_.Used + $_.Free) * 100)} else {0} }}",
        "Root" # Mountpoint
    ]

    select_props = properties
    prefix_cmd = ""
    if parsed_args.human_readable:
        select_props = human_readable_properties
        prefix_cmd = format_bytes_func

    if parsed_args.files:
        # Get-PSDrive doesn't take file paths directly. Get volume for path, then drive name.
        # This makes it more complex. Fallback to Get-Volume which is simpler but needs elevation.
        ui_manager.display_warning("df: Path filtering currently requires Get-Volume (may need elevation).")
        base_cmd = "Get-Volume"
        params = [] # Reset params for Get-Volume
        params.extend([f"-FilePath {shlex.quote(f)}" for f in parsed_args.files])
        needs_elevation = True # Get-Volume likely needs elevation
        # Adjust properties for Get-Volume output
        properties_vol = [
             "DriveLetter",
             "@{N='Size';E={$_.Size}}",
             "@{N='Used';E={($_.Size - $_.SizeRemaining)}}",
             "@{N='Avail';E={$_.SizeRemaining}}", # Available on Windows is SizeRemaining
             "@{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}",
             "@{N='Mounted on';E={$_.Path}}" # Path is the mount point
        ]
        human_readable_properties_vol = [
             "DriveLetter",
             "@{N='Size';E={& $FormatBytes $_.Size}}",
             "@{N='Used';E={& $FormatBytes ($_.Size - $_.SizeRemaining)}}",
             "@{N='Avail';E={& $FormatBytes $_.SizeRemaining}}",
             "@{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}",
             "@{N='Mounted on';E={$_.Path}}"
        ]
        select_props = properties_vol
        if parsed_args.human_readable:
             select_props = human_readable_properties_vol
             prefix_cmd = format_bytes_func
        else:
             prefix_cmd = "" # No helper needed if not human readable

    format_cmd = f"| Select-Object {','.join(select_props)} | Format-Table -AutoSize"
    full_cmd = f"{prefix_cmd}{base_cmd} {' '.join(params)} {format_cmd}"

    return full_cmd, needs_elevation


def translate_ps(args: list[str]) -> tuple[str | None, bool]:
    """Translates ps to Get-Process."""
    parser = NonExitingArgumentParser(prog='ps', add_help=False)
    parser.add_argument('ax', nargs='?', help='Common combined flag ax')
    parser.add_argument('-e', '-A', action='store_true', help='Select all processes')
    parser.add_argument('-f', action='store_true', help='Full format listing (more details)')
    parser.add_argument('-u', action='store_true', help='User-oriented format (show user)')
    parser.add_argument('x', nargs='?', help='Ignored x flag often used with a')

    raw_args_str = "".join(args)
    show_all = '-e' in raw_args_str or '-A' in raw_args_str or 'a' in raw_args_str
    full_format = '-f' in raw_args_str
    user_format = '-u' in raw_args_str

    base_cmd = "Get-Process"
    params = ["-ErrorAction SilentlyContinue"] # Ignore errors for processes that disappear
    format_cmd = "| Format-Table -AutoSize" # Default table

    properties = ["Id", "ProcessName"] # Minimal default
    if full_format or user_format:
        properties = ["Id", "Handles", "CPU", "SI", "WS", "ProcessName"]
    if user_format:
        # Getting username can require elevation or be slow. Use IncludeUserName parameter.
        params.append("-IncludeUserName")
        properties = ["UserName", "Id", "CPU", "StartTime", "ProcessName"]
        format_cmd = "| Format-Table UserName, Id, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='START';E={$_.StartTime.ToString('HH:mm')}}, ProcessName -AutoSize"
        needs_elevation = True # IncludeUserName often needs elevation
        return f"{base_cmd} {' '.join(params)} {format_cmd}", needs_elevation
    elif full_format:
        properties = ["Id", "Handles", "CPU", "WS", "Path"]
        format_cmd = "| Format-Table Id, Handles, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='WS(MB)';E={[math]::Round($_.WS / 1MB)}}, Path -AutoSize"

    if not full_format and not user_format:
         properties = ["Id", "ProcessName", "CPU", "WS"]
         format_cmd = "| Format-Table Id, ProcessName, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='WS(MB)';E={[math]::Round($_.WS / 1MB)}} -AutoSize"

    # Default ps doesn't need elevation unless -u is used
    return f"{base_cmd} {' '.join(params)} | Select-Object {','.join(properties)} {format_cmd}", False


def translate_kill(args: list[str]) -> tuple[str | None, bool]:
    """Translates kill/killall to Stop-Process."""
    parser = NonExitingArgumentParser(prog='kill/killall', add_help=False)
    parser.add_argument('-s', '--signal', default='TERM', help='Signal name/number (ignored, maps to Stop-Process)')
    parser.add_argument('-9', dest='force_kill', action='store_true', help='Force kill (SIGKILL, maps to -Force)')
    parser.add_argument('targets', nargs='+', help='Process IDs or names (for killall)')
    try:
        parsed_args = parser.parse_args(args)
        is_pid = all(t.isdigit() for t in parsed_args.targets)
    except ValueError as e:
        ui_manager.display_error(f"kill/killall: {e}"); return NO_EXEC_MARKER + "kill failed", False

    base_cmd = "Stop-Process"
    params = ["-ErrorAction SilentlyContinue"] # Don't stop script if one process fails

    if is_pid:
        params.append("-Id")
        params.extend(parsed_args.targets)
    else:
        params.append("-Name")
        params.extend([shlex.quote(t) for t in parsed_args.targets])

    if parsed_args.force_kill or parsed_args.signal in ['KILL', '9']:
        params.append("-Force")

    # Stop-Process might need elevation to kill certain processes (e.g., system processes, other users')
    needs_elevation = True # Assume elevation might be needed

    return f"{base_cmd} {' '.join(params)}", needs_elevation


def translate_top(args: list[str]) -> tuple[str | None, bool]:
    """Translates top to a static Get-Process snapshot sorted by CPU."""
    if args: ui_manager.display_warning("top: Arguments are ignored in this basic translation.")
    # Get-Process itself doesn't need elevation, but sorting by CPU and getting details is fine non-elevated.
    cmd = (
        "Get-Process -ErrorAction SilentlyContinue | Sort-Object CPU -Descending | Select-Object -First 15 "
        "Id, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, "
        "@{N='Mem(MB)';E={[math]::Round($_.WS / 1MB)}}, ProcessName "
        "| Format-Table -AutoSize"
    )
    return cmd, False

def translate_id(args: list[str]) -> tuple[str | None, bool]:
    """Translates id to whoami (basic user info)."""
    if args: ui_manager.display_warning("id: Arguments are ignored, using 'whoami /all'.")
    # Use whoami /all for more detail like groups, closer to Linux id
    return "whoami /all /fo list", False # /fo list for readability

# === Network ===
def translate_ifconfig(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='ifconfig', add_help=False); parser.add_argument('interface', nargs='?')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"ifconfig: {e}"); return NO_EXEC_MARKER + "ifconfig failed", False
    # Get-Net* cmdlets usually don't need elevation for read operations
    if parsed_args.interface:
        iface = shlex.quote(parsed_args.interface)
        cmd = f"Get-NetIPConfiguration -InterfaceAlias {iface} -ErrorAction SilentlyContinue | Format-List; Get-NetAdapter -Name {iface} -ErrorAction SilentlyContinue | Format-List Status, LinkSpeed, MacAddress"
    else:
        # ipconfig /all is generally better than Get-NetIPConfiguration for overall view
        cmd = "ipconfig /all"
        # Get-NetIPConfiguration | Format-List works too but less comprehensive than ipconfig /all
        # cmd = "Get-NetIPConfiguration -ErrorAction SilentlyContinue | Format-List"
    return cmd, False

def translate_whois(args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog='whois', add_help=False); parser.add_argument('domain')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"whois: {e}"); return NO_EXEC_MARKER + "whois failed", False
    domain = shlex.quote(parsed_args.domain); ui_manager.console.print(f"[dim]Attempting 'whois {domain}'. Requires external 'whois.exe' in PATH.[/dim]");
    # Assume external whois doesn't need elevation
    return f"whois {domain}", False

def translate_dig(args: list[str]) -> tuple[str | None, bool]:
    try:
        if not args: raise ValueError("Missing name")
        name = args[0]; qtype = 'A'; server = None
        idx = 1
        while idx < len(args):
            arg_upper = args[idx].upper()
            if arg_upper.startswith('@'): server = args[idx][1:]; idx += 1
            elif arg_upper in ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA', 'SRV', 'ANY']: qtype = arg_upper; idx += 1
            else: break # Assume rest is part of name if not recognized? Risky. For now, stop here.
    except ValueError as e: ui_manager.display_error(f"dig: {e}"); return NO_EXEC_MARKER + "dig failed", False

    cmd = f"Resolve-DnsName -Name {shlex.quote(name)} -Type {qtype} -CacheOnly:$false -DnsOnly"
    if server: cmd += f" -Server {shlex.quote(server)}"
    # Resolve-DnsName doesn't need elevation
    return cmd, False

def translate_wget_curl(cmd_name: str, args: list[str]) -> tuple[str | None, bool]:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False)
    parser.add_argument('-O', '--output-document', dest='output_file')
    parser.add_argument('-o', '--output', dest='output_file') # Common alias
    parser.add_argument('-L', '--location', action='store_true', help='Follow redirects (default in IWR)')
    parser.add_argument('-H', '--header', action='append', default=[], help='Add custom header (Key:Value)')
    parser.add_argument('-X', '--request', dest='method', default='GET', help='HTTP method (GET, POST, etc.)')
    parser.add_argument('--insecure', '-k', action='store_true', help='Ignore SSL errors')
    parser.add_argument('url')
    try:
        parsed_args, remaining_args = parser.parse_known_args(args)
        if remaining_args:
             ui_manager.display_warning(f"{cmd_name}: Ignoring unsupported arguments: {' '.join(remaining_args)}")
    except ValueError as e:
        ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed", False

    base_cmd = "Invoke-WebRequest"
    params = [f"-Uri {shlex.quote(parsed_args.url)}", f"-Method {parsed_args.method.upper()}"]

    if parsed_args.insecure:
        params.append("-SkipCertificateCheck")

    if parsed_args.output_file:
        params.append(f"-OutFile {shlex.quote(parsed_args.output_file)}")
    else:
        params.append("-UseBasicParsing") # Gets content more directly for stdout

    if parsed_args.header:
        headers_dict = {}
        for h in parsed_args.header:
            if ':' in h:
                key, val = h.split(':', 1)
                headers_dict[key.strip()] = val.strip()
            else: # Handle flags like -H "HeaderOnly" - Needs thought, maybe ignore for now
                pass
        if headers_dict:
             header_ps_str = "@{" + "; ".join([f'"{k}"="{v}"' for k,v in headers_dict.items()]) + "}"
             params.append(f"-Headers {header_ps_str}")

    # If no output file, pipe content to stdout
    post_cmd = ""
    if not parsed_args.output_file:
        # IWR with UseBasicParsing puts content in $response.Content
        # So we pipe the whole response object and expand content
        post_cmd = "| Select-Object -ExpandProperty Content"

    full_cmd = f"{base_cmd} {' '.join(params)} {post_cmd}"
    # Network requests don't need elevation
    return full_cmd, False

def translate_wget(args: list[str]) -> tuple[str | None, bool]: return translate_wget_curl('wget', args)
def translate_curl(args: list[str]) -> tuple[str | None, bool]: return translate_wget_curl('curl', args)

# === Package Management & OS ===
def translate_apt(args: list[str]) -> tuple[str | None, bool]:
    # Assume the previous robust apt parser implementation is here...
    parser = NonExitingArgumentParser(prog='apt/apt-get/dnf/yum/pacman/zypper', add_help=False); subparsers = parser.add_subparsers(dest='subcommand', help='Sub-command help')
    subparsers.add_parser('update'); upg = subparsers.add_parser('upgrade'); upg.add_argument('packages', nargs='*'); inst = subparsers.add_parser('install'); inst.add_argument('packages', nargs='+'); inst.add_argument('-y', '--yes', action='store_true'); rem = subparsers.add_parser('remove'); rem.add_argument('packages', nargs='+'); rem.add_argument('-y', '--yes', action='store_true'); purg = subparsers.add_parser('purge'); purg.add_argument('packages', nargs='+'); purg.add_argument('-y', '--yes', action='store_true'); srch = subparsers.add_parser('search'); srch.add_argument('query', nargs='+'); sh = subparsers.add_parser('show'); sh.add_argument('package')
    # Add aliases
    aliases = {'add': 'install', '-S': 'install', 'delete': 'remove', 'erase': 'remove', 'list': 'list', 'info': 'show'} # Added list/info

    cmd_name = parser.prog.split('/')[0] # Get original command name

    # Pre-process args for aliases like pacman -S etc.
    processed_args = list(args) # Make a copy
    if processed_args:
        potential_alias = processed_args[0]
        if potential_alias in aliases:
            processed_args[0] = aliases[potential_alias] # Replace alias with standard subcommand
        elif cmd_name == 'pacman' and potential_alias == '-Syu': # Handle common combo
            processed_args = ['upgrade'] # Treat -Syu as upgrade --all
        elif cmd_name == 'pacman' and potential_alias == '-S':
            processed_args = ['install'] + processed_args[1:]
        elif cmd_name == 'pacman' and potential_alias == '-R':
            processed_args = ['remove'] + processed_args[1:]
        elif cmd_name == 'pacman' and potential_alias == '-Ss':
            processed_args = ['search'] + processed_args[1:]
        # Add more specific mappings for other package managers if needed

    try:
        if not processed_args or processed_args[0] not in subparsers.choices and processed_args[0] != 'list': # Allow list as special case
            subcmd_guess = processed_args[0] if processed_args else ''
            ui_manager.display_error(f"{cmd_name}: Unknown or missing subcommand: '{subcmd_guess}'");
            return "winget --help", False # Show winget help
        # Handle 'list' command separately if needed, or add it to parser
        if processed_args[0] == 'list':
             # winget list doesn't usually need elevation
             return "winget list", False
        # Proceed with parsing if subcommand is recognized
        parsed_args = parser.parse_args(processed_args)
    except ValueError as e: ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed", False

    base_cmd="winget"; subcmd=parsed_args.subcommand; params=[]; accept=False
    needs_elevation = False # Default, most winget read commands are fine

    if subcmd == 'update':
        params.append("source update") # Updating sources might need elevation sometimes? Assume false for now.
    elif subcmd == 'upgrade':
        params.append("upgrade"); accept=getattr(parsed_args,'yes',False);
        if parsed_args.packages: params.extend([shlex.quote(p) for p in parsed_args.packages])
        else: params.append("--all")
        needs_elevation = True # Upgrading packages needs elevation
    elif subcmd == 'install':
        params.append("install"); params.extend([shlex.quote(p) for p in parsed_args.packages]); accept=getattr(parsed_args,'yes',False)
        needs_elevation = True # Installing packages needs elevation
    elif subcmd in ['remove','purge']:
        params.append("uninstall"); params.extend([shlex.quote(p) for p in parsed_args.packages]); accept=getattr(parsed_args,'yes',False)
        needs_elevation = True # Uninstalling packages needs elevation
    elif subcmd == 'search':
        params.append("search"); params.append(shlex.quote(" ".join(parsed_args.query)))
    elif subcmd == 'show':
        params.append("show"); params.append(shlex.quote(parsed_args.package))
    else:
        # Should not be reached if parsing worked
        return f"winget {subcmd} # (Passthrough)", False

    if accept: params.extend(["--accept-package-agreements", "--accept-source-agreements"])

    # Add verbose flag maybe?
    params.append("--disable-interactivity") # Useful for scripting winget

    return f"{base_cmd} {' '.join(params)}", needs_elevation


# --- Update do_release_upgrade_sim to return tuple ---
def translate_do_release_upgrade_sim(args: list[str]) -> tuple[str | None, bool]:
    """Simulates checking for/installing Windows Updates. Installation requires elevation."""
    ps_check_cmd = """
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session;
        $UpdateSearcher = $UpdateSession.CreateUpdateSearcher();
        Write-Host "Searching for updates...";
        try {
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'");
            Write-Host ("Found " + $SearchResult.Updates.Count + " updates.");
            return $SearchResult.Updates.Count;
        } catch {
            Write-Warning "Failed to search for updates. Error: $($_.Exception.Message)";
            return -1;
        }
    """
    ps_install_cmd = """
        # Define the install logic within a ScriptBlock for Start-Process
        # This whole block will be executed elevated.
        $ErrorActionPreference = 'Stop'; # Exit script on error inside block
        try {
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session;
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher();
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'");

            if ($SearchResult.Updates.Count -eq 0) {
                Write-Host "No updates to install."; exit 0;
            }
            Write-Host "Updates to download:";
            $UpdatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl;
            foreach ($update in $SearchResult.Updates) {
                Write-Host ("  " + $update.Title);
                $UpdatesToDownload.Add($update) | Out-Null;
            }
            if ($UpdatesToDownload.Count -gt 0) {
                Write-Host "Downloading updates...";
                $Downloader = $UpdateSession.CreateUpdateDownloader();
                $Downloader.Updates = $UpdatesToDownload;
                $DownloadResult = $Downloader.Download();
                if ($DownloadResult.ResultCode -ne 2) { # 2 means Succeeded
                    Write-Error "Download failed. Result code: $($DownloadResult.ResultCode)"; exit 1;
                }
                Write-Host "Updates downloaded. Installing...";
                $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl;
                foreach ($update in $SearchResult.Updates) {
                    if ($update.IsDownloaded) { $UpdatesToInstall.Add($update) | Out-Null }
                }
                if ($UpdatesToInstall.Count -gt 0) {
                    $Installer = $UpdateSession.CreateUpdateInstaller();
                    $Installer.Updates = $UpdatesToInstall;
                    # Note: Installation might require reboot and take a long time.
                    $InstallResult = $Installer.Install();
                    Write-Host ("Installation Result: " + $InstallResult.ResultCode); # 2=OK, 3=OK_Reboot, 4=Fail, 5=Cancel
                    if ($InstallResult.RebootRequired) {
                        Write-Warning "A reboot is required to complete the installation.";
                    }
                    Write-Host "Installation process finished.";
                    exit $InstallResult.ResultCode; # Return result code
                } else {
                    Write-Host "No updates were successfully downloaded to install."; exit 0;
                }
            } else { Write-Host "No updates require downloading."; exit 0; }
        } catch {
            Write-Error "An error occurred during update installation: $($_.Exception.Message)";
            exit 1; # Indicate failure
        }
        # Add a pause if running interactively to see output
        # Read-Host -Prompt "Press Enter to close window"
    """

    ui_manager.display_info("Checking for Windows Updates using built-in COM object...")
    stdout, stderr, code = _run_powershell_command(ps_check_cmd) # Check runs non-elevated
    update_count = -1
    if code == 0 and stdout:
        # ui_manager.display_output(stdout, stderr) # Output is noisy, just use parsed count
        try:
            match = re.search(r'Found (\d+) updates', stdout)
            if match: update_count = int(match.group(1))
            else: # Handle case where PS returns only the number
                 if stdout.strip().isdigit(): update_count = int(stdout.strip())
        except Exception: pass
    elif stderr:
        ui_manager.display_error(f"Update check failed: {stderr}")
        return NO_EXEC_MARKER + "update check failed", False

    needs_elevation = False
    return_marker = NO_EXEC_MARKER + "update check finished"

    if update_count > 0:
        install = ui_manager.console.input(f"[bold yellow]{update_count} updates found. Do you want to attempt installation? (Requires Admin) (y/N): [/bold yellow]")
        if install.lower() == 'y':
            ui_manager.display_info("Attempting to install updates via elevated PowerShell...")
            ui_manager.display_warning("A UAC prompt will appear. Output will be in a separate window.")
            # Return the install script and signal elevation needed
            return ps_install_cmd, True
        else:
            ui_manager.display_info("Update installation cancelled.")
            return return_marker, False # No elevation needed for cancel
    elif update_count == 0:
        ui_manager.display_info("System is up-to-date.")
    # else: Error occurred during check, handled above

    return return_marker, needs_elevation # Return tuple

# === User Management ===
def translate_passwd_guide(args: list[str]) -> tuple[str | None, bool]:
    """Guides the user to change password securely."""
    ui_manager.display_warning("Swodnil cannot securely change passwords directly.")
    ui_manager.display_info("To change your password:")
    ui_manager.display_info(" 1. Press Ctrl+Alt+Del and choose 'Change a password'.")
    ui_manager.display_info(" 2. OR, open an [bold]Administrator[/bold] Command Prompt or PowerShell and run:")
    username = os.getlogin() # Get current username
    ui_manager.console.print(f"    [cyan]net user {username} *[/cyan]")
    ui_manager.display_info("    (You will be prompted to enter the new password securely).")

    # Don't attempt to elevate for the guide itself
    return NO_EXEC_MARKER + "passwd guide shown", False

# === Shell Internals / Environment ===
def translate_env_printenv(args: list[str]) -> tuple[str | None, bool]:
    """Translates env/printenv to display current environment."""
    # Use shell_environment from shell_core ideally, but fallback to PS
    return "Get-ChildItem Env: | Sort-Object Name | Format-Table -AutoSize Name,Value", False

def translate_clear(args: list[str]) -> tuple[str | None, bool]:
    if args: ui_manager.display_error("clear: does not support arguments."); return NO_EXEC_MARKER + "clear failed", False
    return "Clear-Host", False

# === Simulated Commands (Ensure they return tuple) ===
# --- Neofetch Simulation Helpers (Placeholders/Simple Implementations) ---
def _get_uptime() -> str:
    if not psutil: return "N/A (psutil missing)"
    try:
        boot_time_timestamp = psutil.boot_time()
        elapsed_seconds = time.time() - boot_time_timestamp
        td = datetime.timedelta(seconds=elapsed_seconds)
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = ""
        if days > 0: uptime_str += f"{days} day{'s' if days > 1 else ''}, "
        uptime_str += f"{hours:02}:{minutes:02}:{seconds:02}"
        return uptime_str.strip(', ')
    except Exception as e:
        return f"N/A (Error: {e})"

def _get_package_count() -> str:
     stdout, stderr, code = _run_powershell_command("winget list | Measure-Object")
     if code == 0 and stdout:
         match = re.search(r'Count\s+:\s+(\d+)', stdout)
         if match:
             return f"{match.group(1)} (winget)"
     return "N/A" # Fallback

def _get_gpu_info() -> str:
     stdout, stderr, code = _run_powershell_command("(Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue).Name")
     if code == 0 and stdout:
         return stdout.splitlines()[0].strip() if stdout.strip() else "N/A"
     return "N/A" # Fallback

def _get_pending_updates_count() -> int:
     ps_check_cmd = """
        try {
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session;
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher();
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'");
            return $SearchResult.Updates.Count;
        } catch { return -1 }
     """
     stdout, stderr, code = _run_powershell_command(ps_check_cmd)
     if code == 0 and stdout and stdout.strip().isdigit():
         return int(stdout.strip())
     return -1 # Indicate error

def translate_neofetch_simulated(args: list[str]) -> tuple[str | None, bool]:
    # ... (neofetch simulation logic using helpers - unchanged) ...
    # ... MAKE SURE IT RETURNS SIMULATION MARKER and False for elevation ...
    if not psutil: ui_manager.display_error("Neofetch simulation requires 'psutil': pip install psutil"); return NO_EXEC_MARKER+"neofetch failed", False
    # ... (rest of the info gathering logic) ...
    # Example from previous step:
    ui_manager.console.print("\n[bold cyan]Swodnil System Info:[/bold cyan]")
    logo = ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"]; logo_color = "magenta"
    info = {}
    try: info['Hostname'] = platform.node()
    except Exception: info['Hostname'] = "N/A"
    try: info['OS'] = f"{platform.system()} {platform.release()} ({platform.version()})"
    except Exception: info['OS'] = "N/A"
    try: info['Uptime'] = _get_uptime() # Use helper
    except Exception as e: info['Uptime'] = f"N/A (Err:{e})"
    try: info['Packages'] = _get_package_count() # Use helper
    except Exception as e: info['Packages'] = f"N/A (Err:{e})"
    try: info['Terminal'] = f"Swodnil (PID:{os.getpid()})" # Removed version for simplicity
    except Exception: info['Terminal'] = "N/A"
    try: info['CPU'] = platform.processor()
    except Exception: info['CPU'] = "N/A"
    try: info['GPU'] = _get_gpu_info() # Use helper
    except Exception as e: info['GPU'] = f"N/A (Err:{e})"
    try: mem = psutil.virtual_memory(); info['Memory'] = f"{_format_bytes(mem.used)} / {_format_bytes(mem.total)} ({mem.percent}%)"
    except Exception as e: info['Memory'] = f"N/A (Err:{e})"
    try:
        drive_letter = os.path.splitdrive(os.getcwd())[0] or 'C:' # Use current drive or default to C:
        if not drive_letter.endswith('\\'): drive_letter += '\\'
        disk = psutil.disk_usage(drive_letter)
        info[f'Storage({drive_letter})'] = f"{_format_bytes(disk.used)} / {_format_bytes(disk.total)} ({disk.percent}%)"
    except Exception as e: info[f'Storage({drive_letter})'] = f"N/A (Err:{e})" # Use drive letter determined above
    try:
        updates_count = _get_pending_updates_count() # Use helper
        if updates_count > 0: info['Updates'] = f"[yellow]{updates_count} Pending[/yellow]"
        elif updates_count == 0: info['Updates'] = "System up-to-date"
        else: info['Updates'] = "[dim]N/A (Check failed)[/dim]"
    except Exception as e: info['Updates'] = f"N/A (Err:{e})"

    max_key_len = max(len(k) for k in info.keys()) if info else 0; output_lines = []
    info_items = list(info.items())
    for i in range(max(len(logo), len(info))):
        logo_part = f"[{logo_color}]{logo[i]}[/{logo_color}]" if i < len(logo) else " " * len(logo[0])
        info_part = ""; key_color="bold white"
        if i < len(info_items): key, value = info_items[i]; info_part = f"[{key_color}]{key.rjust(max_key_len)}[/]: {value}"
        output_lines.append(f" {logo_part}  {info_part}")
    ui_manager.console.print("\n".join(output_lines)); ui_manager.console.print()

    return SIMULATION_MARKER_PREFIX + "neofetch", False

def translate_cowsay_simulated(args: list[str]) -> tuple[str | None, bool]:
    # ... (cowsay simulation logic - unchanged) ...
    message = " ".join(args) if args else "Moo?"; max_width = 40
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
    # ... (logansay simulation logic - unchanged) ...
    message = " ".join(args) if args else "Yo!"
    max_width = 40
    lines = textwrap.wrap(message, width=max_width)
    bubble_width = max(len(line) for line in lines) if lines else 0
    bubble = [" " + "_" * (bubble_width + 2)]
    if not lines: bubble.append("< >")
    elif len(lines) == 1: bubble.append(f"< {lines[0].ljust(bubble_width)} >")
    else: bubble.append(f"/ {lines[0].ljust(bubble_width)} \\"); bubble.extend([f"| {lines[i].ljust(bubble_width)} |" for i in range(1, len(lines)-1)]); bubble.append(f"\\ {lines[-1].ljust(bubble_width)} /")
    bubble.append(" " + "-" * (bubble_width + 2))
    ui_manager.console.print("\n".join(bubble))
    ui_manager.console.print(LOGAN_ART)
    return SIMULATION_MARKER_PREFIX + "logangsay", False


def translate_hollywood_simulated(args: list[str]) -> tuple[str | None, bool]:
    ui_manager.console.print("[green]Entering Hollywood Mode... Press Ctrl+C to exit.[/green]"); time.sleep(0.5)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:'\",<.>/?\\|`~ "
    try:
        with ui_manager.console.capture(): # Suppress prompt etc during loop
             while True:
                line = "".join(random.choices(chars, k=random.randint(40, ui_manager.console.width - 1)))
                color = random.choice(["green", "bright_green", "dim green", "rgb(0,100,0)", "rgb(0,150,0)"])
                ui_manager.console.print(f"[{color}]{line}", end='\n' if random.random() < 0.05 else '')
                time.sleep(random.uniform(0.005, 0.02))
    except KeyboardInterrupt: ui_manager.console.print("\n[green]...Exiting Hollywood Mode.[/green]")
    return SIMULATION_MARKER_PREFIX + "hollywood", False

# --- Add translate_which and translate_command returning tuple ---
def translate_which(args: list[str]) -> tuple[str | None, bool]:
    """Translates which to Get-Command."""
    if not args:
        ui_manager.display_error("which: missing command name")
        return NO_EXEC_MARKER + "which failed", False
    command_name = shlex.quote(args[0])
    return f"Get-Command {command_name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source", False

def translate_command(args: list[str]) -> tuple[str | None, bool]:
    """Handles specific 'command' subcommands like 'command -v'."""
    if args and args[0] == '-v':
        if len(args) > 1:
            return translate_which(args[1:])
        else:
            ui_manager.display_error("command -v: missing command name")
            return NO_EXEC_MARKER + "command -v failed", False
    else:
        ui_manager.display_warning(f"command: Unsupported arguments {' '.join(args)}. Treating as native.")
        return None, False # Let shell_core handle it natively

# --- Command Map ---
# Ensure all values are functions defined above that return the tuple (str|None, bool)
TRANSLATION_MAP = {
    # Filesystem
    "ls": translate_ls, "cp": translate_cp, "mv": translate_mv, "rm": translate_rm,
    "mkdir": translate_mkdir, "pwd": translate_pwd, "touch": translate_touch,
    "find": translate_find, "df": translate_df,
    "chmod": translate_chmod, "chown": translate_chown, # chown returns guide message
    # Text
    "cat": translate_cat, "grep": translate_grep, "head": translate_head, "tail": translate_tail,
    # System Info / Process Mgmt
    "hostname": translate_hostname, "uname": translate_uname, "ps": translate_ps,
    "kill": translate_kill, "killall": translate_kill,
    "top": translate_top,
    "id": translate_id,
    # Network
    "ifconfig": translate_ifconfig, "whois": translate_whois, "dig": translate_dig,
    "wget": translate_wget, "curl": translate_curl,
    # Environment / Shell
    "env": translate_env_printenv, "printenv": translate_env_printenv,
    "clear": translate_clear,
    # Package Management Aliases -> translate_apt
    "apt": translate_apt, "apt-get": translate_apt, "dnf": translate_apt, "yum": translate_apt,
    "pacman": translate_apt, "zypper": translate_apt,
    # User Management (Guide)
    "passwd": translate_passwd_guide,
    # OS Updates (Simulation)
    "do-release-upgrade": translate_do_release_upgrade_sim,
    # Simulated Fun Commands
    "neofetch": translate_neofetch_simulated,
    "cowsay": translate_cowsay_simulated,
    "logangsay": translate_logangsay_simulated,
    "hollywood": translate_hollywood_simulated,
    # Which/command -v support
    "which": translate_which,
    "command": translate_command,
}


# --- Main Processing Function ---
# Updated to handle and return tuple
def process_command(command: str, args: list[str]) -> tuple[str | None, bool]:
    """
    Main entry point for command translation/simulation.
    Returns a tuple: (result_string | None, needs_elevation: bool)
    """
    cmd_lower = command.lower()
    handler = TRANSLATION_MAP.get(cmd_lower)
    needs_elevation = False # Default to False

    if handler:
        try:
            # Expect handler to return (result, needs_elevation) tuple
            handler_output = handler(args)

            # Validate the output type
            if isinstance(handler_output, tuple) and len(handler_output) == 2 and isinstance(handler_output[1], bool):
                result, needs_elevation = handler_output
                # Further check if result is string or None
                if not (isinstance(result, str) or result is None):
                     ui_manager.display_error(f"Internal error: Translator for '{command}' returned invalid result type: {type(result)}")
                     return NO_EXEC_MARKER + "handler type error", False
            else:
                # Handle legacy translators or error case where handler didn't return the expected tuple
                ui_manager.display_warning(f"Internal warning: Translator for '{command}' did not return expected (result, bool) tuple. Got: {type(handler_output)}. Assuming no elevation needed.")
                result = str(handler_output) if handler_output is not None else None # Attempt conversion
                needs_elevation = False

            return result, needs_elevation
        except Exception as e:
            ui_manager.display_error(f"Internal Swodnil error processing '{command}': {e}")
            import traceback; traceback.print_exc() # More debugging info
            return NO_EXEC_MARKER + "handler exception", False # Return tuple on error
    else:
        # Command not found in map -> treat as native, no elevation needed by default
        return None, False # Return tuple

# --- Direct Execution Test Block ---
if __name__ == "__main__":
    # Example tests - adjust as needed
    test_commands = [
        "ls -lart", "cp -r source dest", "rm -rf testdir", "mkdir -p a/b/c", "find . -name '*.py'",
        "grep -i error log.txt", "head -n 5 file", "tail -f log", "hostname", "uname -a",
        "ps aux", "kill 1234", "killall notepad", "df -h", "apt install vscode -y", "dnf update",
        "pacman -S vim", "passwd", "do-release-upgrade", "neofetch", "cowsay test 123", "logangsay hi",
        "hollywood", "cat /etc/fstab", "cat /proc/cpuinfo", "which ls", "command -v grep"
    ]
    # Set up console for testing
    if not hasattr(ui_manager, 'console') or ui_manager.console is None:
         from rich.console import Console
         ui_manager.console = Console()

    print("--- Running Translator Tests (Output: Tuple(Result, NeedsElevation)) ---")
    for cmd_str in test_commands:
        print("-" * 20); print(f"Testing: {cmd_str}")
        parts = shlex.split(cmd_str) if cmd_str else [""]
        command = parts[0] if parts else ""
        if not command: continue
        args_list = parts[1:]
        result_tuple = process_command(command, args_list)
        print(f"  Result Tuple: {result_tuple}")
        if isinstance(result_tuple, tuple) and len(result_tuple)==2:
            result, needs_elevation = result_tuple
            print(f"  Needs Elevation: {needs_elevation}")
            if isinstance(result, str) and result.startswith(SIMULATION_MARKER_PREFIX): print("  -> Simulation Triggered")
            elif isinstance(result, str) and result.startswith(NO_EXEC_MARKER): print("  -> Execution Blocked")
            elif isinstance(result, str): print("  -> PowerShell Command Generated")
            elif result is None and command.lower() not in TRANSLATION_MAP: print("  -> Native Command")
            else: print("  -> Translation/Simulation Failed or Unexpected Result")
        else:
             print("  -> ERROR: process_command did not return expected tuple")
# --- Special Path Mappings for 'cat' ---
# Maps lowercase Linux paths to PowerShell commands providing equivalent info
SPECIAL_CAT_PATHS = {
    # Filesystem Table Equivalent (/etc/fstab)
    "/etc/fstab": (r"""
        Write-Host '# Windows Volume Information (Simulated /etc/fstab)' -ForegroundColor Gray;
        Write-Host '# <file system>                              <mount point>   <type>     <options>       <dump> <pass>';

        # Local volumes with drive letters
        Get-Volume | Where-Object { $_.DriveLetter } | ForEach-Object {
            $fs = $_.Path; # GUID Path like \\?\Volume{...}\
            $mp = "$($_.DriveLetter):\";
            $type = if ($_.FileSystem) { $_.FileSystem } else { 'unknown' };
            $options = 'defaults'; # Simplified placeholder
            $dump = 0;
            $pass = 0;
            Write-Host ("{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}" -f $fs, $mp, $type, $options, $dump, $pass);
        };

        # Page file (swap equivalent) - may list multiple if configured
        Get-CimInstance Win32_PageFileSetting | ForEach-Object {
            $fs = $_.Name; # e.g., C:\pagefile.sys
            $mp = 'swap';
            $type = 'swap';
            $options = 'defaults';
            $dump = 0;
            $pass = 0;
            Write-Host ("{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}" -f $fs, $mp, $type, $options, $dump, $pass);
        };

        # Mapped network drives (using Get-PSDrive)
        Get-PSDrive -PSProvider FileSystem | Where-Object { $_.DisplayRoot -like '\\*' } | ForEach-Object {
             $fs = $_.DisplayRoot; # UNC Path like \\server\share
             $mp = "$($_.Name):\"; # Drive Letter
             $type = 'cifs'; # Assuming CIFS/SMB
             $options = 'defaults'; # Could check persistence? Get-SmbMapping needed
             $dump = 0;
             $pass = 0;
             Write-Host ("{0,-45} {1,-15} {2,-10} {3,-15} {4} {5}" -f $fs, $mp, $type, $options, $dump, $pass);
        }
    """, True),

    # Hosts File (Actual Path) - Remains the same, shows real content
    "/etc/hosts": (r'Get-Content -Path "$env:SystemRoot\System32\drivers\etc\hosts"', False),

    # DNS Resolver Info (/etc/resolv.conf)
    "/etc/resolv.conf": (r"""
        Write-Host '# Windows DNS Configuration (Simulated /etc/resolv.conf)' -ForegroundColor Gray;
        # Get search list per interface (often empty on clients)
        Get-DnsClient | Select-Object -ExpandProperty ConnectionSpecificSuffix | Where-Object {$_} | ForEach-Object {
             Write-Host ("search {0}" -f $_);
        };
        # Get global search list
        $globalSearch = (Get-DnsClientGlobalSetting).SuffixSearchList;
        if ($globalSearch) { Write-Host ("search {0}" -f ($globalSearch -join ' ')) };

        # Get DNS Servers per interface (IPv4)
        Get-DnsClientServerAddress -AddressFamily IPv4 | Where-Object {$_.ServerAddresses} | ForEach-Object {
            Write-Host ("# Interface $($_.InterfaceAlias) ($($_.InterfaceIndex))" -ForegroundColor Gray);
            $_.ServerAddresses | ForEach-Object { Write-Host "nameserver $_" };
        }
    """, False),

    # CPU Info (/proc/cpuinfo)
    "/proc/cpuinfo": (r"""
        Write-Host '# Windows CPU Information (Simulated /proc/cpuinfo)' -ForegroundColor Gray;
        $processors = Get-CimInstance Win32_Processor;
        $processorIndex = 0;
        foreach ($proc in $processors) {
            Write-Host "processor`t: $processorIndex";
            Write-Host "vendor_id`t: $($proc.Manufacturer)";
            Write-Host "model name`t: $($proc.Name)";
            Write-Host "cpu family`t: $($proc.Family)"; # Needs mapping to Linux numbers if possible
            Write-Host "model`t`t: $($proc.Description)"; # Often contains more detail
            Write-Host "stepping`t: $($proc.Stepping)";
            Write-Host "cpu MHz`t`t: $($proc.CurrentClockSpeed)"; # MaxSpeed might be more stable?
            Write-Host "cache size`t: $($proc.L2CacheSize) KB (L2) / $($proc.L3CacheSize) KB (L3)";
            Write-Host "physical id`t: $($proc.SocketDesignation)";
            # Siblings/cores require more complex calculation using logical processors info
            $cores = $proc.NumberOfCores;
            $logical = $proc.NumberOfLogicalProcessors;
            Write-Host "cpu cores`t: $cores";
            Write-Host "siblings`t: $logical"; # This is total logical per package usually
            Write-Host "flags`t`t: (Not directly available, see Get-ComputerInfo for features)";
            Write-Host ""; # Separator between processors
            $processorIndex++;
        }
    """, True),

    # Memory Info (/proc/meminfo)
    "/proc/meminfo": (r"""
        Write-Host '# Windows Memory Information (Simulated /proc/meminfo)' -ForegroundColor Gray;
        $mem = Get-CimInstance Win32_OperatingSystem;
        $cs = Get-CimInstance Win32_ComputerSystem;
        $pm = Get-Counter '\Memory\Available KBytes'; # Physical Memory Available

        $totalMB = [math]::Round($mem.TotalVisibleMemorySize / 1024);
        $freeMB = [math]::Round($mem.FreePhysicalMemory / 1024);
        $availMB = [math]::Round($pm.CounterSamples[0].CookedValue / 1024); # Available is often more useful than Free

        Write-Host ("MemTotal:`t{0,10} kB" -f $mem.TotalVisibleMemorySize);
        Write-Host ("MemFree:`t{0,10} kB" -f $mem.FreePhysicalMemory); # Free = Unused
        Write-Host ("MemAvailable:`t{0,10} kB" -f ($availMB * 1024)); # Available = Free + Cache/Buffers usable by apps

        # Swap information is complex (multiple page files possible)
        $swapTotal = (Get-CimInstance Win32_PageFileUsage | Measure-Object -Property AllocatedBaseSize -Sum).Sum / 1KB;
        $swapUsed = (Get-CimInstance Win32_PageFileUsage | Measure-Object -Property CurrentUsage -Sum).Sum / 1KB;
        $swapFree = $swapTotal - $swapUsed;
        Write-Host ("SwapTotal:`t{0,10} kB" -f $swapTotal);
        Write-Host ("SwapFree:`t{0,10} kB" -f $swapFree);

        # Other common fields (placeholders or N/A)
        Write-Host ("Buffers:`t{0,10} kB" -f 0); # Not directly equivalent/easily obtained
        Write-Host ("Cached:`t`t{0,10} kB" -f 0); # System Cache is complex, Get-Counter '\Memory\Cache Bytes' exists
        Write-Host ("Slab:`t`t{0,10} kB" -f 0); # N/A
    """, False),

    # OS / Distribution Info (/etc/os-release)
    "/etc/os-release": (r"""
        Write-Host '# Windows OS Information (Simulated /etc/os-release)' -ForegroundColor Gray;
        $os = Get-CimInstance Win32_OperatingSystem;
        $ci = Get-ComputerInfo; # Get-ComputerInfo is slower but provides more structured info

        $name = $os.Caption;
        # Try to create a simpler ID
        $id = $name -replace '[^a-zA-Z0-9]+', '' -replace 'Microsoft', '' | Out-String;
        $id = $id.Trim().ToLower();

        Write-Host ("NAME=`"{0}`"" -f $name);
        Write-Host ("VERSION=`"{0} (Build {1})`"" -f $os.Version, $os.BuildNumber);
        Write-Host ("ID={0}" -f $id);
        # Attempt VERSION_ID (like 22H2) - requires parsing or specific registry keys, complex. Placeholder:
        Write-Host ("VERSION_ID=`"{0}`"" -f $os.Version);
        Write-Host ("PRETTY_NAME=`"{0}`"" -f $name);
        Write-Host ("ANSI_COLOR=`"0;34`""); # Blue for Windows?
        Write-Host ("HOME_URL=`"https://www.microsoft.com/windows/`"");
        Write-Host ("SUPPORT_URL=`"https://support.microsoft.com/windows`"");
        Write-Host ("BUG_REPORT_URL=`"https://support.microsoft.com/windows`"");
    """, False),
    "/etc/lsb-release": (r"""
        Write-Host '# Windows OS Information (Simulated /etc/lsb-release)' -ForegroundColor Gray;
        $os = Get-CimInstance Win32_OperatingSystem;
        $name = $os.Caption;
        # Try to create a simpler ID
        $id = $name -replace '[^a-zA-Z0-9]+', '' -replace 'Microsoft', '' | Out-String;
        $id = $id.Trim().ToLower();

        Write-Host ("DISTRIB_ID={0}" -f $id);
        Write-Host ("DISTRIB_RELEASE={0}" -f $os.Version);
        Write-Host ("DISTRIB_CODENAME=Windows"); # Placeholder
        Write-Host ("DISTRIB_DESCRIPTION=`"{0}`"" -f $name);
    """, False),

    # User Info (/etc/passwd) - Guide remains best approach due to complexity/security
    "/etc/passwd": ("'# Showing current user info via whoami. For full user list use: Get-LocalUser' -ForegroundColor Gray; whoami /user /fo list", False),
    # Group Info (/etc/group) - Guide remains best approach
    "/etc/group": ("'# Showing current user groups via whoami. For full group list use: Get-LocalGroup' -ForegroundColor Gray; whoami /groups /fo list", False),
}