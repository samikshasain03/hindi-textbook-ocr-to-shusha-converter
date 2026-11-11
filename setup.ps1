# Run once to prepare this project. Re-running it is safe.
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

# Keep Python packages inside this project rather than installing them globally.
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Python could not create .venv. Install Python 3.11 or newer and try again." }
}
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Python packages could not be installed. Check your internet connection and try again." }

# Tesseract is a separate program. Use an existing install if one is present.
$taskTesseractPaths = @(
    $env:TESSERACT_CMD,
    (Join-Path $env:ProgramFiles "Tesseract-OCR\tesseract.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Tesseract-OCR\tesseract.exe")
)
$taskTesseractCommand = Get-Command tesseract -ErrorAction SilentlyContinue
if ($taskTesseractCommand) { $taskTesseractPaths += $taskTesseractCommand.Source }
$taskTesseractFound = $taskTesseractPaths | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
if (-not $taskTesseractFound) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "Install Tesseract using the Windows link at https://tesseract-ocr.github.io/tessdoc/Installation.html, then run setup.ps1 again."
    }
    Write-Host "Installing Tesseract. Windows may ask you to approve its installer."
    winget install --id UB-Mannheim.TesseractOCR --exact --source winget
    if ($LASTEXITCODE -ne 0) { throw "Tesseract installation did not finish. Install it and run setup.ps1 again." }
}

# Download the official Hindi model into the project, where ocr.py will find it.
New-Item -ItemType Directory -Force -Path tessdata | Out-Null
$taskModelPath = Join-Path $PSScriptRoot "tessdata\hin.traineddata"
if (-not (Test-Path -LiteralPath $taskModelPath) -or (Get-Item -LiteralPath $taskModelPath).Length -lt 1000000) {
    Write-Host "Downloading the Hindi OCR model..."
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/tesseract-ocr/tessdata_best/main/hin.traineddata" -OutFile "$taskModelPath.download"
    if ((Get-Item -LiteralPath "$taskModelPath.download").Length -lt 1000000) {
        throw "The Hindi model download was incomplete. Run setup.ps1 again."
    }
    Move-Item -LiteralPath "$taskModelPath.download" -Destination $taskModelPath -Force
}

# Confirm that Python can see both the engine and Hindi model.
& ".\.venv\Scripts\python.exe" -c "from ocr import get_ocr_status; result = get_ocr_status(); print(result['message']); raise SystemExit(0 if result['ready'] else 1)"
if ($LASTEXITCODE -ne 0) { throw "OCR setup needs attention. Follow the message above, then run setup.ps1 again." }
Write-Host "Setup complete. Run: powershell -ExecutionPolicy Bypass -File .\start.ps1"
