@echo off
:: Build script for Swodnil using PyInstaller
:: Places the final executable in build\Swodnil.exe and cleans up artifacts.

set SCRIPT_NAME=swodnil.py
set EXE_NAME=Swodnil
set ICON_PATH=assets/icon.ico

:: Define the TARGET directory for the final executable
set TARGET_BUILD_DIR=build

:: Define a TEMPORARY directory for PyInstaller's intermediate files
set TEMP_WORK_DIR=_pyinstaller_temp

title Building %EXE_NAME%...

echo Cleaning up previous target build directory and spec file...
if exist "%TARGET_BUILD_DIR%" rmdir /s /q "%TARGET_BUILD_DIR%"
if exist "%TEMP_WORK_DIR%" rmdir /s /q "%TEMP_WORK_DIR%"
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"

echo Starting PyInstaller build...

:: Run PyInstaller
:: --onefile: Bundle everything into a single .exe
:: --name: Specifies the name of the final executable and the .spec file
:: --icon: Specifies the application icon
:: --distpath: Specifies the output directory for the final executable (our target)
:: --workpath: Specifies where PyInstaller puts temporary build files (our temp dir)
:: --noconfirm: Overwrite output directory without asking (useful for reruns)
:: %SCRIPT_NAME%: The main Python script entry point
pyinstaller ^
    --onefile ^
    --name=%EXE_NAME% ^
    --icon=%ICON_PATH% ^
    --distpath=%TARGET_BUILD_DIR% ^
    --workpath=%TEMP_WORK_DIR% ^
    --noconfirm ^
    %SCRIPT_NAME%

:: Check if PyInstaller succeeded
if %ERRORLEVEL% neq 0 (
    echo ============================
    echo      BUILD FAILED!
    echo ============================
    echo PyInstaller returned error code %ERRORLEVEL%.
    echo Attempting partial cleanup...
    if exist "%TEMP_WORK_DIR%" rmdir /s /q "%TEMP_WORK_DIR%"
    if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"
    pause
    exit /b %ERRORLEVEL%
)

echo ============================
echo    BUILD SUCCESSFUL!
echo ============================
echo Executable created at: %TARGET_BUILD_DIR%\%EXE_NAME%.exe

:: Clean up intermediate files and spec file AFTER successful build
echo Cleaning up temporary build files and spec file...
if exist "%TEMP_WORK_DIR%" rmdir /s /q "%TEMP_WORK_DIR%"
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec"

echo.
echo Build process complete. Only the executable remains in the '%TARGET_BUILD_DIR%' folder.
pause