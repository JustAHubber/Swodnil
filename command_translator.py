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
        return NO_EXEC_MARKER + "cat failed"

    # --- Check for Special Path Handling ---
    if len(parsed_args.files) == 1:
        normalized_path = parsed_args.files[0].lower().replace('\\', '/')
        if normalized_path in SPECIAL_CAT_PATHS:
            powershell_cmd = SPECIAL_CAT_PATHS[normalized_path]
            if parsed_args.number:
                ui_manager.display_warning(f"cat: Flag '-n' ignored when displaying equivalent for '{parsed_args.files[0]}'")
            # Add context comment (already included in most scripts above, but keep for others)
            context_comment = f"# Showing Windows equivalent for: {parsed_args.files[0]}"
            # Check if the script already adds its own comment
            if not powershell_cmd.strip().startswith("Write-Host '# Windows"):
                 return f"Write-Host '{context_comment}' -ForegroundColor Gray; {powershell_cmd}"
            else:
                 return powershell_cmd # Script handles its own context message

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

    return full_cmd

def translate_grep(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='grep', add_help=False); parser.add_argument('-i', '--ignore-case', action='store_true'); parser.add_argument('-v', '--invert-match', action='store_true'); parser.add_argument('-n', '--line-number', action='store_true'); parser.add_argument('-r','-R', '--recursive', action='store_true'); parser.add_argument('pattern'); parser.add_argument('files', nargs='*')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"grep: {e}"); return NO_EXEC_MARKER + "grep failed"

    select_string_cmd = "Select-String"
    ss_params = [f"-Pattern {shlex.quote(parsed_args.pattern)}"]
    (parsed_args.ignore_case) and ss_params.append("-CaseSensitive:$false") or ss_params.append("-CaseSensitive")
    if parsed_args.invert_match: ss_params.append("-NotMatch")
    # -n is handled implicitly by Select-String object output, format if needed

    if not parsed_args.files:
        # Handle stdin - assume input piped to Select-String
        return f"{select_string_cmd} {' '.join(ss_params)}"
    elif parsed_args.recursive:
        # Use Get-ChildItem | Select-String for recursion
        gci_params = ["-Recurse", "-File"] # Search only files
        # Need to quote file paths if they are patterns for GCI
        gci_params.extend([shlex.quote(f) for f in parsed_args.files])
        return f"Get-ChildItem {' '.join(gci_params)} | {select_string_cmd} {' '.join(ss_params)}"
    else:
        # Search specific files
        ss_params.append("-Path")
        ss_params.extend([shlex.quote(f) for f in parsed_args.files])
        return f"{select_string_cmd} {' '.join(ss_params)}"

def translate_head_tail(cmd_name: str, args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False); parser.add_argument('-n', '--lines', type=int, default=10); (cmd_name == 'tail') and parser.add_argument('-f', '--follow', action='store_true'); parser.add_argument('file', nargs='?', default=None) # Allow stdin
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed"

    base_cmd = "Get-Content"; params = []
    if parsed_args.file: params.append(shlex.quote(parsed_args.file))
    # else: assumes reading from pipeline/stdin

    selector = "-Head" if cmd_name == 'head' else "-Tail"
    params.append(f"{selector} {parsed_args.lines}")

    if cmd_name == 'tail' and parsed_args.follow:
        if not parsed_args.file:
             ui_manager.display_error(f"tail -f: requires a file argument, cannot follow stdin.")
             return NO_EXEC_MARKER + "tail -f failed"
        params.append("-Wait")

    return f"{base_cmd} {' '.join(params)}"

def translate_head(args: list[str]) -> str | None: return translate_head_tail('head', args)
def translate_tail(args: list[str]) -> str | None: return translate_head_tail('tail', args)

# === System Information & Management ===
def translate_hostname(args: list[str]) -> str | None:
    if args: ui_manager.display_error("hostname: does not support arguments."); return NO_EXEC_MARKER + "hostname failed"
    # Environment variable is most direct
    return 'Write-Host $env:COMPUTERNAME'

def translate_uname(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='uname', add_help=False); parser.add_argument('-a', '--all', action='store_true'); parser.add_argument('-s', '--kernel-name', action='store_true'); parser.add_argument('-n', '--nodename', action='store_true'); parser.add_argument('-r', '--kernel-release', action='store_true'); parser.add_argument('-v', '--kernel-version', action='store_true'); parser.add_argument('-m', '--machine', action='store_true'); parser.add_argument('-o', '--operating-system', action='store_true')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"uname: {e}"); return NO_EXEC_MARKER + "uname failed"
    results = []; sys_system = platform.system(); sys_release = platform.release(); sys_version = platform.version(); sys_machine = platform.machine(); sys_node = platform.node()
    if not any([parsed_args.all, parsed_args.kernel_name, parsed_args.nodename, parsed_args.kernel_release, parsed_args.kernel_version, parsed_args.machine, parsed_args.operating_system]): parsed_args.kernel_name = True
    if parsed_args.kernel_name or parsed_args.all: results.append(sys_system)
    if parsed_args.nodename or parsed_args.all: results.append(sys_node)
    if parsed_args.kernel_release or parsed_args.all: results.append(sys_release)
    if parsed_args.kernel_version or parsed_args.all: results.append(sys_version)
    if parsed_args.machine or parsed_args.all: results.append(sys_machine)
    if parsed_args.operating_system or parsed_args.all: (sys_system not in results) and results.append(sys_system)
    return f"Write-Host \"{' '.join(results)}\""

def translate_df(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='df', add_help=False); parser.add_argument('-h', '--human-readable', action='store_true'); parser.add_argument('files', nargs='*')
    # Add -T to show filesystem type? Get-Volume includes it.
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"df: {e}"); return NO_EXEC_MARKER + "df failed"
    base_cmd = "Get-Volume"; params = [];
    # Use Get-PSDrive for potentially more linux-like output? It shows Used/Free.
    # base_cmd = "Get-PSDrive"
    # params = ["-PSProvider FileSystem"] # Filter for filesystem drives

    format_cmd = "| Format-Table DriveLetter, FileSystemLabel, @{N='Size';E={$_.Size}}, @{N='Free';E={$_.SizeRemaining}}, @{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}"
    if parsed_args.files:
        # Get-Volume supports -FilePath, Get-PSDrive doesn't directly
        params.extend([f"-FilePath {shlex.quote(f)}" for f in parsed_args.files])
    if parsed_args.human_readable:
        format_cmd = "| Format-Table DriveLetter, FileSystemLabel, @{N='Size';E={Format-Bytes $_.Size}}, @{N='Free';E={Format-Bytes $_.SizeRemaining}}, @{N='Use%';E={if($_.Size -gt 0){[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}else{0}}}"
        # Define Format-Bytes helper function in PS scope if needed, or do calculation directly
        format_cmd = ("$FormatBytes = {param($bytes) if ($bytes -ge 1GB) {{'{0:N2} GiB' -f ($bytes / 1GB)}} elseif ($bytes -ge 1MB) {{'{0:N1} MiB' -f ($bytes / 1MB)}} elseif ($bytes -ge 1KB) {{'{0:N1} KiB' -f ($bytes / 1KB)}} else {{'{0} B' -f $bytes}}};"
                      f"{base_cmd} {' '.join(params)} | Format-Table DriveLetter, FileSystemLabel, @{{N='Size';E={{& $FormatBytes $_.Size}}}}, @{{N='Free';E={{& $FormatBytes $_.SizeRemaining}}}}, @{{N='Use%';E={{if($_.Size -gt 0){{[int]((($_.Size - $_.SizeRemaining)/$_.Size)*100)}}else{{0}}}}}}")
        return format_cmd # Return early as it includes helper func definition

    return f"{base_cmd} {' '.join(params)} {format_cmd}"

def translate_ps(args: list[str]) -> str | None:
    """Translates ps to Get-Process."""
    parser = NonExitingArgumentParser(prog='ps', add_help=False)
    parser.add_argument('ax', nargs='?', help='Common combined flag ax') # Treat 'ax' specially
    parser.add_argument('-e', '-A', action='store_true', help='Select all processes') # Default Get-Process
    parser.add_argument('-f', action='store_true', help='Full format listing (more details)')
    parser.add_argument('-u', action='store_true', help='User-oriented format (show user)')
    parser.add_argument('x', nargs='?', help='Ignored x flag often used with a') # Treat 'x' specially if combined like 'aux'

    # Simplistic handling for common combined flags like 'ax', 'aux', 'ef'
    raw_args_str = "".join(args)
    show_all = '-e' in raw_args_str or '-A' in raw_args_str or 'a' in raw_args_str
    full_format = '-f' in raw_args_str
    user_format = '-u' in raw_args_str

    # Base command
    base_cmd = "Get-Process"
    params = []
    format_cmd = "| Format-Table -AutoSize" # Default table

    # Select properties based on flags
    properties = ["Id", "ProcessName"] # Minimal default
    if full_format or user_format:
        properties = ["Id", "Handles", "CPU", "SI", "WS", "ProcessName"] # Default PS view
    if user_format:
        # Getting username requires another call or calculated property
        # Let's add StartTime and maybe CPU time for 'user' oriented view
        # Get-Process | Select-Object Id, UserName (needs calc), CPU, StartTime ...
        # Simplification: use default properties but maybe format differently
        properties = ["Id", "CPU", "StartTime", "ProcessName"] # Simplified user view
        format_cmd = "| Format-Table Id, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='START';E={$_.StartTime.ToString('HH:mm')}}, ProcessName -AutoSize"
    elif full_format:
        # Add more details like Path
        properties = ["Id", "Handles", "CPU", "WS", "Path"]
        format_cmd = "| Format-Table Id, Handles, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='WS(MB)';E={[math]::Round($_.WS / 1MB)}}, Path -AutoSize"

    # If no specific format requested, use standard detailed view
    if not full_format and not user_format:
         properties = ["Id", "ProcessName", "CPU", "WS"] # A reasonable default
         format_cmd = "| Format-Table Id, ProcessName, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, @{N='WS(MB)';E={[math]::Round($_.WS / 1MB)}} -AutoSize"


    return f"{base_cmd} {' '.join(params)} | Select-Object {','.join(properties)} {format_cmd}"

def translate_top(args: list[str]) -> str | None:
    """Translates top to a static Get-Process snapshot sorted by CPU."""
    # top doesn't usually take file args, ignore args for basic translation
    if args:
        ui_manager.display_warning("top: Arguments are ignored in this basic translation.")

    # Get processes, sort by CPU descending, take top 15, format nicely
    # Select properties relevant to 'top' (ID, Name, CPU, Memory(WS))
    cmd = (
        "Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 "
        "Id, @{N='CPU(s)';E={if($_.CPU -ne $null){[math]::Round($_.CPU,2)}else{0}}}, "
        "@{N='Mem(MB)';E={[math]::Round($_.WS / 1MB)}}, ProcessName "
        "| Format-Table -AutoSize"
    )
    return cmd

def translate_id(args: list[str]) -> str | None:
    """Translates id to whoami (basic user info)."""
    if args:
        ui_manager.display_warning("id: Arguments are ignored, using 'whoami'.")
    # whoami provides the basic username, similar to the primary part of id output.
    # Use 'whoami /all' for more detail closer to Linux 'id' (SID, groups)
    # Let's start simple:
    return "whoami"

def translate_kill(args: list[str]) -> str | None:
    """Translates kill/killall to Stop-Process."""
    # kill [-s signal] pid...
    # killall name...
    # Stop-Process [-Id] pid... | -Name name... [-Force]
    parser = NonExitingArgumentParser(prog='kill/killall', add_help=False)
    parser.add_argument('-s', '--signal', default='TERM', help='Signal name/number (ignored, maps to Stop-Process)')
    parser.add_argument('-9', dest='force_kill', action='store_true', help='Force kill (SIGKILL, maps to -Force)')
    parser.add_argument('targets', nargs='+', help='Process IDs or names (for killall)')
    # Determine if it's kill (pids) or killall (names) based on command name later
    try:
        parsed_args = parser.parse_args(args)
        # Crude check: if targets look like numbers, assume PID, else assume name
        is_pid = all(t.isdigit() for t in parsed_args.targets)
    except ValueError as e:
        ui_manager.display_error(f"kill/killall: {e}"); return NO_EXEC_MARKER + "kill failed"

    base_cmd = "Stop-Process"
    params = []

    if is_pid:
        params.append("-Id")
        params.extend(parsed_args.targets)
    else:
        # Assumed killall or kill by name (less common for kill)
        params.append("-Name")
        params.extend([shlex.quote(t) for t in parsed_args.targets])

    if parsed_args.force_kill or parsed_args.signal in ['KILL', '9']:
        params.append("-Force")

    # Ignore other signal types as Stop-Process doesn't map them

    return f"{base_cmd} {' '.join(params)}"


# === Network ===
def translate_ifconfig(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='ifconfig', add_help=False); parser.add_argument('interface', nargs='?')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"ifconfig: {e}"); return NO_EXEC_MARKER + "ifconfig failed"
    if parsed_args.interface: iface = shlex.quote(parsed_args.interface); return f"Get-NetIPConfiguration -InterfaceAlias {iface} | Format-List; Get-NetAdapter -Name {iface} | Format-List Status, LinkSpeed, MacAddress"
    else: return "ipconfig /all"

def translate_whois(args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog='whois', add_help=False); parser.add_argument('domain')
    try: parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"whois: {e}"); return NO_EXEC_MARKER + "whois failed"
    domain = shlex.quote(parsed_args.domain); ui_manager.console.print(f"[dim]Attempting 'whois {domain}'. Requires external 'whois.exe' in PATH.[/dim]"); return f"whois {domain}"

def translate_dig(args: list[str]) -> str | None:
    try:
        if not args: raise ValueError("Missing name")
        name = args[0]; qtype = 'A'
        if len(args) > 1 and args[1].upper() in ['A', 'AAAA', 'MX', 'TXT', 'CNAME', 'NS', 'SOA', 'SRV', 'ANY']: qtype = args[1].upper()
    except ValueError as e: ui_manager.display_error(f"dig: {e}"); return NO_EXEC_MARKER + "dig failed"
    return f"Resolve-DnsName -Name {shlex.quote(name)} -Type {qtype} -CacheOnly:$false -DnsOnly" # DnsOnly for closer dig behavior

def translate_wget_curl(cmd_name: str, args: list[str]) -> str | None:
    parser = NonExitingArgumentParser(prog=cmd_name, add_help=False)
    parser.add_argument('-O', '--output-document', dest='output_file')
    parser.add_argument('-o', '--output', dest='output_file') # Common alias
    parser.add_argument('-L', '--location', action='store_true', help='Follow redirects (default in IWR)')
    parser.add_argument('-H', '--header', action='append', default=[], help='Add custom header (Key:Value)')
    parser.add_argument('-X', '--request', dest='method', default='GET', help='HTTP method (GET, POST, etc.)')
    parser.add_argument('url')
    try:
        # Use parse_known_args for flexibility if unhandled args exist
        parsed_args, remaining_args = parser.parse_known_args(args)
        if remaining_args:
             ui_manager.display_warning(f"{cmd_name}: Ignoring unsupported arguments: {' '.join(remaining_args)}")
    except ValueError as e:
        ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed"

    base_cmd = "Invoke-WebRequest"
    params = [f"-Uri {shlex.quote(parsed_args.url)}", f"-Method {parsed_args.method.upper()}"]

    # IWR follows redirects by default, -L is implicit unless -MaximumRedirection 0 is set

    if parsed_args.output_file:
        params.append(f"-OutFile {shlex.quote(parsed_args.output_file)}")
    else:
        # Mimic curl default outputting to stdout? IWR outputs object.
        # Use -UseBasicParsing to get content more directly? Or select content.
        # Let's select content for now.
        params.append("-UseBasicParsing") # Gets content more directly

    if parsed_args.header:
        headers_dict = {}
        for h in parsed_args.header:
            if ':' in h:
                key, val = h.split(':', 1)
                headers_dict[key.strip()] = val.strip()
        if headers_dict:
             header_ps_str = "@{" + "; ".join([f'"{k}"="{v}"' for k,v in headers_dict.items()]) + "}"
             params.append(f"-Headers {header_ps_str}")

    # If no output file, pipe content to stdout
    post_cmd = ""
    if not parsed_args.output_file:
        post_cmd = "| Select-Object -ExpandProperty Content"

    return f"{base_cmd} {' '.join(params)} {post_cmd}"

def translate_wget(args: list[str]) -> str | None: return translate_wget_curl('wget', args)
def translate_curl(args: list[str]) -> str | None: return translate_wget_curl('curl', args)

# === Package Management & OS ===
def translate_apt(args: list[str]) -> str | None:
    # Assume the previous robust apt parser implementation is here...
    # (Code omitted for brevity)
    parser = NonExitingArgumentParser(prog='apt/apt-get/dnf/yum/pacman/zypper', add_help=False); subparsers = parser.add_subparsers(dest='subcommand', help='Sub-command help')
    subparsers.add_parser('update'); upg = subparsers.add_parser('upgrade'); upg.add_argument('packages', nargs='*'); inst = subparsers.add_parser('install'); inst.add_argument('packages', nargs='+'); inst.add_argument('-y', '--yes', action='store_true'); rem = subparsers.add_parser('remove'); rem.add_argument('packages', nargs='+'); rem.add_argument('-y', '--yes', action='store_true'); purg = subparsers.add_parser('purge'); purg.add_argument('packages', nargs='+'); purg.add_argument('-y', '--yes', action='store_true'); srch = subparsers.add_parser('search'); srch.add_argument('query', nargs='+'); sh = subparsers.add_parser('show'); sh.add_argument('package')
    # Add aliases used by other package managers if needed (e.g., 'install' vs 'add')
    # pacman -S -> install
    # zypper install -> install
    cmd_name = parser.prog.split('/')[0] # Get original command name for messages/logic if needed

    # Basic mapping for pacman -S etc? Need smarter argument parsing.
    # Simple approach: assume subcommand names match apt for now.
    if cmd_name == 'pacman' and args and args[0] == '-S':
        args = ['install'] + args[1:] # Map pacman -S to install

    try:
        # Handle case where args are empty or don't start with a known subcommand
        if not args or args[0] not in subparsers.choices:
            # Try common aliases?
            if args and args[0] == 'list': subcmd_guess = 'list' # winget list
            elif args and args[0] in ['add', '-S']: subcmd_guess = 'install' # Map add/-S to install
            elif args and args[0] in ['delete', 'erase']: subcmd_guess = 'remove' # Map delete/erase to remove
            else: subcmd_guess = args[0] if args else ''
            # Map to winget equivalent if possible, else show help
            if subcmd_guess == 'list': return "winget list"
            ui_manager.display_error(f"{cmd_name}: Unknown or missing subcommand: '{subcmd_guess}'"); return "winget --help"
        # Proceed with parsing if subcommand is recognized
        parsed_args = parser.parse_args(args)
    except ValueError as e: ui_manager.display_error(f"{cmd_name}: {e}"); return NO_EXEC_MARKER + f"{cmd_name} failed"

    base_cmd="winget"; subcmd=parsed_args.subcommand; params=[]; accept=False
    if subcmd == 'update': params.append("source update")
    elif subcmd == 'upgrade': params.append("upgrade"); accept=getattr(parsed_args,'yes',False); (parsed_args.packages) and params.extend([shlex.quote(p) for p in parsed_args.packages]) or params.append("--all")
    elif subcmd == 'install': params.append("install"); params.extend([shlex.quote(p) for p in parsed_args.packages]); accept=getattr(parsed_args,'yes',False)
    elif subcmd in ['remove','purge']: params.append("uninstall"); params.extend([shlex.quote(p) for p in parsed_args.packages]); accept=getattr(parsed_args,'yes',False)
    elif subcmd == 'search': params.append("search"); params.append(shlex.quote(" ".join(parsed_args.query)))
    elif subcmd == 'show': params.append("show"); params.append(shlex.quote(parsed_args.package))
    else: return f"winget {subcmd} # (Passthrough)"
    if accept: params.extend(["--accept-package-agreements", "--accept-source-agreements"])
    return f"{base_cmd} {' '.join(params)}"


def translate_do_release_upgrade_sim(args: list[str]) -> str | None:
    """Simulates checking for/installing Windows Updates."""
    ui_manager.display_info("Checking for Windows Updates using built-in COM object...")
    # PowerShell commands to check, download, install updates
    ps_check_cmd = """
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
        Write-Host "Searching for updates..."
        try {
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'") # Basic software updates
            Write-Host ("Found " + $SearchResult.Updates.Count + " updates.")
            return $SearchResult.Updates.Count # Return count to Python side if needed
        } catch {
            Write-Warning "Failed to search for updates. Error: $($_.Exception.Message)"
            return -1 # Indicate error
        }
    """
    ps_install_cmd = """
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
        $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'")

        if ($SearchResult.Updates.Count -eq 0) {
            Write-Host "No updates to install."
            exit 0
        }

        Write-Host "Updates to download:"
        $UpdatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
        foreach ($update in $SearchResult.Updates) {
            Write-Host ("  " + $update.Title)
            $UpdatesToDownload.Add($update) | Out-Null
        }

        if ($UpdatesToDownload.Count -gt 0) {
            Write-Host "Downloading updates..."
            $Downloader = $UpdateSession.CreateUpdateDownloader()
            $Downloader.Updates = $UpdatesToDownload
            $DownloadResult = $Downloader.Download()

            if ($DownloadResult.ResultCode -ne 2) { # 2 means Succeeded
                Write-Error "Download failed. Result code: $($DownloadResult.ResultCode)"
                exit 1
            }

            Write-Host "Updates downloaded. Installing..."
            $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
            foreach ($update in $SearchResult.Updates) {
                 if ($update.IsDownloaded) { $UpdatesToInstall.Add($update) | Out-Null }
            }

            if ($UpdatesToInstall.Count -gt 0) {
                 $Installer = $UpdateSession.CreateUpdateInstaller()
                 $Installer.Updates = $UpdatesToInstall
                 # Note: Installation might require reboot and take a long time.
                 # This script runs synchronously. Consider async or just triggering install.
                 $InstallResult = $Installer.Install()

                 Write-Host ("Installation Result: " + $InstallResult.ResultCode) # 2 = Succeeded, 3 = Succeeded with errors, 4 = Failed, 5 = Canceled
                 if ($InstallResult.RebootRequired) {
                     Write-Warning "A reboot is required to complete the installation."
                 }
                 Write-Host "Installation process finished."
                 exit $InstallResult.ResultCode # Return result code
            } else {
                 Write-Host "No updates were successfully downloaded to install."
                 exit 0
            }
        } else {
             Write-Host "No updates require downloading."
             exit 0
        }
    """

    stdout, stderr, code = _run_powershell_command(ps_check_cmd)
    update_count = -1
    if code == 0 and stdout:
        ui_manager.display_output(stdout, stderr)
        try:
            # Extract count if possible (simple approach)
            match = re.search(r'Found (\d+) updates', stdout)
            if match: update_count = int(match.group(1))
        except Exception: pass # Ignore parsing errors
    elif stderr:
        ui_manager.display_error(f"Update check failed: {stderr}")
        return NO_EXEC_MARKER + "update check failed"

    if update_count > 0:
        install = ui_manager.console.input(f"[bold yellow]{update_count} updates found. Do you want to attempt installation? (y/N): [/bold yellow]")
        if install.lower() == 'y':
            ui_manager.display_info("Attempting to download and install updates via PowerShell...")
            ui_manager.display_warning("This may take a long time and might require a reboot.")
            # Run the install script (this will block Swodnil until done)
            stdout_inst, stderr_inst, code_inst = _run_powershell_command(ps_install_cmd)
            if stdout_inst: ui_manager.display_output(stdout_inst, None)
            if stderr_inst: ui_manager.display_output(None, stderr_inst)
            if code_inst != 0 and code_inst != 2: # Allow success code 2
                 ui_manager.display_error(f"Update installation finished with errors or failure (Code: {code_inst}).")
            else:
                 ui_manager.display_info("Update installation process completed.")
        else:
            ui_manager.display_info("Update installation cancelled.")
    elif update_count == 0:
        ui_manager.display_info("System is up-to-date.")
    # else: Error occurred during check

    return NO_EXEC_MARKER + "update check finished" # Don't execute anything else


# === User Management ===
def translate_passwd_guide(args: list[str]) -> str | None:
    """Guides the user to change password securely."""
    ui_manager.display_warning("Swodnil cannot securely change passwords directly.")
    ui_manager.display_info("To change your password:")
    ui_manager.display_info(" 1. Press Ctrl+Alt+Del and choose 'Change a password'.")
    ui_manager.display_info(" 2. OR, open an [bold]Administrator[/bold] Command Prompt or PowerShell and run:")
    username = os.getlogin() # Get current username
    ui_manager.console.print(f"    [cyan]net user {username} *[/cyan]")
    ui_manager.display_info("    (You will be prompted to enter the new password securely).")

    # Optionally, try to launch an elevated cmd for the user
    # try_launch = ui_manager.console.input("Do you want to try launching an elevated command prompt now? (y/N): ")
    # if try_launch.lower() == 'y':
    #     cmd_to_run = f'cmd /c "net user {username} * & pause"'
    #     elevate_cmd = f'powershell -Command "Start-Process cmd -ArgumentList \'/c net user {username} * & pause\' -Verb RunAs"'
    #     ui_manager.display_info("Attempting to request Administrator privileges...")
    #     stdout, stderr, code = _run_powershell_command(elevate_cmd)
    #     if code != 0:
    #         ui_manager.display_error(f"Failed to launch elevated prompt: {stderr}")

    return NO_EXEC_MARKER + "passwd guide shown"


# === Shell Internals / Environment ===
def translate_env_printenv(args: list[str]) -> str | None:
    """Translates env/printenv to display current environment."""
    # This should ideally be handled by shell_core displaying its managed environment.
    # For now, fallback to Get-ChildItem Env:
    return "Get-ChildItem Env: | Sort-Object Name | Format-Table -AutoSize Name,Value"

def translate_clear(args: list[str]) -> str | None:
    if args: ui_manager.display_error("clear: does not support arguments."); return NO_EXEC_MARKER + "clear failed"
    return "Clear-Host"

# === Simulated Commands ===
def translate_neofetch_simulated(args: list[str]) -> str | None:
    if not psutil: ui_manager.display_error("Neofetch requires 'psutil': pip install psutil"); return NO_EXEC_MARKER+"neofetch failed"
    ui_manager.console.print("\n[bold cyan]Swodnil System Info:[/bold cyan]")
    logo = ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"]; logo_color = "magenta"
    info = {}
    try: info['Hostname'] = platform.node()
    except Exception: info['Hostname'] = "N/A"
    try: info['OS'] = f"{platform.system()} {platform.release()} ({platform.version()})"
    except Exception: info['OS'] = "N/A"
    try: info['Uptime'] = _get_uptime() # Use helper
    except Exception: info['Uptime'] = "N/A"
    try: info['Packages'] = _get_package_count() # Use helper
    except Exception: info['Packages'] = "N/A"
    try: info['Terminal'] = f"Swodnil 0.2 (PID:{os.getpid()})" # Increment version :)
    except Exception: info['Terminal'] = "N/A"
    try: info['CPU'] = platform.processor()
    except Exception: info['CPU'] = "N/A"
    try: info['GPU'] = _get_gpu_info() # Use helper
    except Exception: info['GPU'] = "N/A"
    try: mem = psutil.virtual_memory(); info['Memory'] = f"{_format_bytes(mem.used)} / {_format_bytes(mem.total)} ({mem.percent}%)"
    except Exception: info['Memory'] = "N/A"
    try: disk = psutil.disk_usage('C:'); info['Storage(C:)'] = f"{_format_bytes(disk.used)} / {_format_bytes(disk.total)} ({disk.percent}%)"
    except Exception: info['Storage(C:)'] = "N/A"
    try: updates = _get_pending_updates_count(); info['Updates'] = f"[yellow]{updates} Pending[/yellow]" if updates > 0 else "No"
    except Exception: info['Updates'] = "N/A"

    max_key_len = max(len(k) for k in info.keys()); output_lines = []
    info_items = list(info.items())
    for i in range(max(len(logo), len(info))):
        logo_part = f"[{logo_color}]{logo[i]}[/{logo_color}]" if i < len(logo) else " " * len(logo[0])
        info_part = ""; key_color="bold white"
        if i < len(info_items): key, value = info_items[i]; info_part = f"[{key_color}]{key.rjust(max_key_len)}[/]: {value}"
        output_lines.append(f" {logo_part}  {info_part}")
    ui_manager.console.print("\n".join(output_lines)); ui_manager.console.print()
    return SIMULATION_MARKER_PREFIX + "neofetch" # Return simulation marker

def translate_cowsay_simulated(args: list[str]) -> str | None:
    message = " ".join(args) if args else "Moo?"; max_width = 40
    lines = textwrap.wrap(message, width=max_width); bubble_width = max(len(line) for line in lines) if lines else 0
    bubble = [" " + "_" * (bubble_width + 2)];
    if len(lines) == 1: bubble.append(f"< {lines[0].ljust(bubble_width)} >")
    else: bubble.append(f"/ {lines[0].ljust(bubble_width)} \\"); bubble.extend([f"| {lines[i].ljust(bubble_width)} |" for i in range(1, len(lines)-1)]); bubble.append(f"\\ {lines[-1].ljust(bubble_width)} /")
    bubble.append(" " + "-" * (bubble_width + 2)); cow = r"""
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||"""
    ui_manager.console.print("\n".join(bubble) + cow)
    return SIMULATION_MARKER_PREFIX + "cowsay"

def translate_logangsay_simulated(args: list[str]) -> str | None:
    """Displays a message with custom Logan ASCII art."""
    message = " ".join(args) if args else "Yo!" # Changed default message
    max_width = 40 # Keep consistent with cowsay bubble width or adjust as needed

    # --- Speech Bubble Logic (same as cowsay) ---
    lines = textwrap.wrap(message, width=max_width)
    bubble_width = max(len(line) for line in lines) if lines else 0

    bubble = [" " + "_" * (bubble_width + 2)] # Top border

    if not lines: # Handle empty message case explicitly
        bubble.append("< >")
    elif len(lines) == 1:
        # Single line message
        bubble.append(f"< {lines[0].ljust(bubble_width)} >")
    else:
        # Multi-line message
        bubble.append(f"/ {lines[0].ljust(bubble_width)} \\") # Top line
        bubble.extend([f"| {lines[i].ljust(bubble_width)} |" for i in range(1, len(lines)-1)]) # Middle lines
        bubble.append(f"\\ {lines[-1].ljust(bubble_width)} /") # Bottom line

    bubble.append(" " + "-" * (bubble_width + 2)) # Bottom border
    # --- End Speech Bubble Logic ---

    # Print the bubble, then the custom art
    ui_manager.console.print("\n".join(bubble))
    ui_manager.console.print(LOGAN_ART) # Use the custom art defined above

    # Return the simulation marker for logangsay
    return SIMULATION_MARKER_PREFIX + "logangsay"

def translate_hollywood_simulated(args: list[str]) -> str | None:
    ui_manager.console.print("[green]Entering Hollywood Mode... Press Ctrl+C to exit.[/green]"); time.sleep(0.5)
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{};:'\",<.>/?\\|`~ "
    try:
        with ui_manager.console.capture(): # Suppress prompt etc during loop
             while True:
                line = "".join(random.choices(chars, k=random.randint(40, ui_manager.console.width - 1)))
                color = random.choice(["green", "bright_green", "dim green", "rgb(0,100,0)", "rgb(0,150,0)"])
                ui_manager.console.print(f"[{color}]{line}", end='\n' if random.random() < 0.05 else '') # Occasionally add newline
                time.sleep(random.uniform(0.005, 0.02))
    except KeyboardInterrupt: ui_manager.console.print("\n[green]...Exiting Hollywood Mode.[/green]")
    return SIMULATION_MARKER_PREFIX + "hollywood"

# --- Command Map ---
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
    "kill": translate_kill, "killall": translate_kill, # Map killall to kill translator
    "top": translate_top, # Static snapshot
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
    "apt do-release-upgrade": translate_do_release_upgrade_sim, # Simulate standard updates
    # Simulated Fun Commands
    "neofetch": translate_neofetch_simulated,
    "cowsay": translate_cowsay_simulated,
    "logangsay": translate_logangsay_simulated,
    "hollywood": translate_hollywood_simulated,
}

# --- Main Processing Function ---
def process_command(command: str, args: list[str]) -> str | None:
    """ Main entry point for command translation/simulation. """
    cmd_lower = command.lower()
    # Handle specific case 'command -v' -> 'which'
    if cmd_lower == "command" and args and args[0] == "-v":
        handler = TRANSLATION_MAP.get("which")
        if handler and len(args) > 1: return handler(args[1:])
        else: ui_manager.display_error("command -v: missing command name"); return NO_EXEC_MARKER + "cmd -v failed"

    handler = TRANSLATION_MAP.get(cmd_lower)
    if handler:
        try:
            result = handler(args) # Returns PowerShell string, SIMULATION_*, NO_EXEC_*, or None on internal error
            return result
        except Exception as e:
            ui_manager.display_error(f"Internal Swodnil error processing '{command}': {e}")
            # import traceback; traceback.print_exc() # Uncomment for debugging tracebacks
            return NO_EXEC_MARKER + "handler exception" # Prevent execution on internal error
    else:
        # Command not found in map -> treat as native
        return None

# --- Direct Execution Test Block ---
if __name__ == "__main__":
    # Example tests - more can be added
    test_commands = [
        "ls -lart", "cp -r source dest", "rm -rf testdir", "mkdir -p a/b/c", "find . -name '*.py'",
        "grep -i error log.txt", "head -n 5 file", "tail -f log", "hostname", "uname -a",
        "ps aux", "kill 1234", "killall notepad", "df -h", "apt install vscode -y", "dnf update",
        "pacman -S vim", "passwd", "apt do-release-upgrade", "neofetch", "cowsay test 123"
    ]
    # Set up console for testing
    if not hasattr(ui_manager, 'console') or ui_manager.console is None:
         from rich.console import Console
         ui_manager.console = Console()

    print("--- Running Translator Tests ---")
    for cmd_str in test_commands:
        print("-" * 20); print(f"Testing: {cmd_str}")
        parts = shlex.split(cmd_str) if cmd_str else [""]
        command = parts[0] if parts else ""
        if not command: continue
        args_list = parts[1:]
        result = process_command(command, args_list)
        print(f"  Result: {result}")
        if isinstance(result, str) and result.startswith(SIMULATION_MARKER_PREFIX):
            print("  -> Simulation Triggered")
        elif isinstance(result, str) and result.startswith(NO_EXEC_MARKER):
            print("  -> Execution Blocked")
        elif isinstance(result, str):
            print("  -> PowerShell Command Generated")
        elif result is None and command.lower() not in TRANSLATION_MAP:
            print("  -> Native Command")
        else:
            print("  -> Translation/Simulation Failed or Unexpected Result")

# --- Special Path Mappings for 'cat' ---
# Maps lowercase Linux paths to PowerShell commands providing equivalent info
SPECIAL_CAT_PATHS = {
    # Filesystem Table Equivalent (/etc/fstab)
    "/etc/fstab": r"""
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
    """,

    # Hosts File (Actual Path) - Remains the same, shows real content
    "/etc/hosts": r'Get-Content -Path "$env:SystemRoot\System32\drivers\etc\hosts"',

    # DNS Resolver Info (/etc/resolv.conf)
    "/etc/resolv.conf": r"""
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
    """,

    # CPU Info (/proc/cpuinfo)
    "/proc/cpuinfo": r"""
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
    """,

    # Memory Info (/proc/meminfo)
    "/proc/meminfo": r"""
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
    """,

    # OS / Distribution Info (/etc/os-release)
    "/etc/os-release": r"""
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
    """,
    "/etc/lsb-release": r"""
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
    """,

    # User Info (/etc/passwd) - Guide remains best approach due to complexity/security
    "/etc/passwd": "'# Showing current user info via whoami. For full user list use: Get-LocalUser' -ForegroundColor Gray; whoami /user /fo list",
    # Group Info (/etc/group) - Guide remains best approach
    "/etc/group": "'# Showing current user groups via whoami. For full group list use: Get-LocalGroup' -ForegroundColor Gray; whoami /groups /fo list",
}