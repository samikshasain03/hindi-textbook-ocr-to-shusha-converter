# Start the app with this project's Python environment.
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    throw "Run setup.ps1 first to create the project environment."
}
& ".\.venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1
