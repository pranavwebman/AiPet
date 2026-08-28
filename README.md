# AIPet - Interactive AI Desktop Pet for Windows

**AIPet** is a fully functional, interactive desktop AI companion for Windows. The pet lives directly on your Windows desktop as a transparent, always-on-top, draggable character. It communicates with vision-capable multi-modal LLM models (powered by NVIDIA NIM API), analyzes your active window or screen upon request, and performs controlled computer interactions with human-in-the-loop safety confirmation.

---

## Key Features

* **Desktop Pet Interface**: Transparent, borderless, always-on-top window that sits on your Windows desktop.
* **Mouse Interactions & Animations**: Drag to move across multi-monitor displays, click to open chat, right-click for context menu. Features state-based animations (`idle`, `hover`, `clicked`, `thinking`, `talking`, `happy`, `confused`, `error`, `sleeping`).
* **NVIDIA NIM AI Client**: Non-blocking asynchronous API calls to NVIDIA NIM vision models (`meta/llama-3.2-11b-vision-instruct`).
* **Explicit Screen Analysis**: Capture full screen or active application window on command with OCR support (`mss`, `PIL`, `pytesseract`).
* **Controlled Computer Automation**: Programmatic mouse movement, clicks, scrolling, text typing, key presses, hotkeys, and window focusing (`ctypes`/`user32`).
* **Safety First**: Permission manager enforcing explicit confirmation dialogs before executing any consequential computer action.
* **System Tray & Windows Startup**: System tray integration and clean Windows Registry startup registration (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).
* **Persistent SQLite Storage**: Remembers conversation history and user configuration (`%APPDATA%/AIPet/`).
* **Standalone Windows Executable**: Bundled with PyInstaller without requiring a terminal console window or dev environment.

---

## Project Architecture

```
AIPet/
├── app/
│   ├── ai/               # AI client, vision prompt builder, and action planner
│   │   ├── client.py
│   │   ├── conversation.py
│   │   ├── tools.py
│   │   └── vision.py
│   ├── assets/           # Generated PNG frames and icons
│   │   ├── generate_assets.py
│   │   ├── icon.ico
│   │   └── pet_*.png
│   ├── automation/       # Computer control (mouse, keyboard, windows)
│   │   ├── action_executor.py
│   │   ├── keyboard.py
│   │   ├── mouse.py
│   │   ├── ui_automation.py
│   │   └── windows.py
│   ├── core/             # Configuration, logging, events, permissions, exceptions
│   │   ├── config.py
│   │   ├── events.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   └── permissions.py
│   ├── memory/           # SQLite database and conversation store
│   │   ├── conversation_store.py
│   │   └── database.py
│   ├── pet/              # Pet window, state animation engine, behaviors
│   │   ├── animation.py
│   │   ├── behavior.py
│   │   ├── movement.py
│   │   └── pet_window.py
│   ├── startup/          # Windows Registry startup integration
│   │   └── windows_startup.py
│   ├── ui/               # Interactive chat, settings window, dialogs, system tray
│   │   ├── chat_window.py
│   │   ├── dialogs.py
│   │   ├── settings_window.py
│   │   └── tray.py
│   └── vision/           # Screen capture, active window detection, OCR
│       ├── active_window.py
│       ├── image_processor.py
│       ├── ocr.py
│       └── screen_capture.py
├── tests/                # Automated pytest suite
│   └── test_aipet.py
├── aipet.spec            # PyInstaller packaging configuration
├── build.bat             # One-click Windows build script
├── main.py               # Main application entrypoint
└── README.md
```

---

## Requirements & Installation

### Development Prerequisites

* **Python 3.12+**
* **Windows 10/11** (or Linux with Xvfb/offscreen for testing)
* Optional: **Tesseract OCR** installed on Windows for local OCR extraction.

### Installation

1. Clone or download the repository:
   ```bash
   git clone https://github.com/your-org/AIPet.git
   cd AIPet
   ```

2. Install Python dependencies:
   ```bash
   pip install PySide6 mss Pillow requests pyinstaller pytest pytest-qt numpy opencv-python-headless pytesseract
   ```

3. Ensure asset files are generated:
   ```bash
   python app/assets/generate_assets.py
   ```

---

## Setting Up NVIDIA NIM API Key

1. Obtain an API key from [NVIDIA Build / NVIDIA NIM](https://build.nvidia.com/).
2. Launch AIPet:
   ```bash
   python main.py
   ```
3. Open **Settings** (via Right Click on Pet -> Settings or System Tray -> Settings).
4. Navigate to the **AI Model** tab.
5. Enter your NVIDIA API key (`nvapi-...`).
6. Click **Save & Apply**.

---

## Running Automated Tests

Run the test suite using `pytest`:

```bash
python -m pytest tests/
```

---

## Packaging into Standalone Windows EXE

To package AIPet into a single standalone Windows executable without a console window:

Run the included build batch file on Windows:
```cmd
build.bat
```

Or execute PyInstaller directly:
```cmd
pyinstaller --clean aipet.spec
```

The packaged executable and required files will be placed in `dist/AIPet/AIPet.exe`.

---

## Major User Flow Verification

1. **Launch Application**: Run `python main.py` or double-click `AIPet.exe`.
2. **Desktop Pet**: The floating pet window appears on desktop with frameless transparent background.
3. **Dragging**: Click and hold left mouse button to drag the pet around the screen.
4. **Chat Interface**: Left-click the pet to open the chat window or press `Ctrl+Alt+Space`.
5. **AI Response**: Send a message to get real responses from NVIDIA NIM API.
6. **Screen Analysis**: Click "📷 Look Screen" in chat or select "Analyze Screen" from the pet right-click context menu.
7. **Computer Control**: Request an action (e.g. "Click on coordinates x=500, y=300"). AIPet presents a **Security Confirmation Dialog** before executing consequential actions.
8. **Settings & Persistence**: Configure settings (such as "Start with Windows") and confirm they persist across app restarts in `%APPDATA%/AIPet/config/settings.json`.
9. **System Tray**: Minimize or manage the application from the Windows System Tray icon.

---

## License

MIT License.
