# Faster Whisper Global Dictation & API

An OS-level, high-speed, local dictation tool and transcription API powered by `faster-whisper`.

## Features
- **Global Dictation**: Press `` ` `` (backtick) to record speech and automatically paste transcribed text into any application.
- **Always-Hot API**: A local FastAPI server keeps the model in VRAM for near-instant transcription.
- **Context Menu Integration**: Right-click `.mp4` or `.wav` files in Windows Explorer to transcribe them directly to your clipboard.
- **Privacy-First**: Everything runs 100% locally on your machine.

## Pre-requisites
1.  **NVIDIA GPU**: Highly recommended for CUDA acceleration.
2.  **FFmpeg**: Must be installed and added to your System PATH.
3.  **Python 3.10+**: Recommended.

## Setup Instructions

### 1. Create Environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the API Server
The API must be running for any transcription to work. Use the provided keep-alive script:
```powershell
.\Start-WhisperAPI.ps1
```

### 3. Usage
- **Global Listener**: Run `python background_listener.py`. Use the backtick key to start/stop dictation.
- **Windows Context Menu**: 
  - Open PowerShell as **Administrator**.
  - Modify the paths in the following command to match your installation and run it:
    ```powershell
    $BaseDir = "C:\PATH\TO\Faster_Whisper_API"
    $PythonW = "$BaseDir\.venv\Scripts\pythonw.exe"
    $Script = "$BaseDir\transcribe_file.py"
    $Command = "$PythonW $Script `"%1`""
    $Key = "Registry::HKEY_CLASSES_ROOT\*\shell\TranscribeToClipboard"
    New-Item -Path $Key -Force
    Set-ItemProperty -Path $Key -Name "MUIVerb" -Value "Transcribe to Clipboard"
    Set-ItemProperty -Path $Key -Name "Icon" -Value "shell32.dll,301"
    New-Item -Path "$Key\command" -Value $Command -Force
    ```

## Project Structure
- `whisper_api.py`: The FastAPI server holding the model.
- `background_listener.py`: Global hotkey listener (backtick).
- `transcribe_file.py`: Helper for individual file transcription (context menu).
- `Start-WhisperAPI.ps1`: Robust loop to keep the API server running.
- `requirements.txt`: Project dependencies.
