@echo off
REM Build the Windows release: two standalone executables under dist/
REM
REM   dist\digimon_randomize.exe      - headless CLI
REM   dist\digimon_randomize_gui.exe  - PyQt6 desktop app
REM
REM Requirements:
REM   * Python 3.11+ with the project installed in editable mode:
REM         pip install -e ".[gui]"
REM     (the [gui] extra pulls in PyQt6, which the GUI executable bundles)
REM   * pyinstaller on the PATH:
REM         pip install pyinstaller
REM   * 7-Zip at C:\Program Files\7-Zip\7za.exe (only needed for the
REM     final zip step; comment it out if you don't have it).

IF EXIST "dist" RMDIR /S /Q "dist"
IF EXIST "build" RMDIR /S /Q "build"

REM ----- CLI executable --------------------------------------------------
pyinstaller --clean --onefile --log-level ERROR digimon_randomize.py
IF ERRORLEVEL 1 GOTO :error

REM ----- GUI executable --------------------------------------------------
REM --windowed suppresses the console window on Windows so users get a
REM clean double-click experience.
pyinstaller --clean --onefile --windowed --log-level ERROR digimon_randomize_gui.py
IF ERRORLEVEL 1 GOTO :error

REM ----- Bundle README + Changelog alongside the executables -------------
COPY "README.md"    "dist\"
COPY "CHANGELOG.md" "dist\"

REM ----- Optional: zip the release ---------------------------------------
IF EXIST "C:\Program Files\7-Zip\7za.exe" (
    "C:\Program Files\7-Zip\7za.exe" a -tzip "dist\digimon_randomizer.zip" "dist\*"
)

ECHO.
ECHO Build complete. See dist\
EXIT /B 0

:error
ECHO.
ECHO Build failed.
EXIT /B 1
