# 🎥 YTDownloader4K - YouTube Video Downloader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-red)](https://github.com/yt-dlp/yt-dlp)

A powerful, user-friendly YouTube video downloader with a graphical interface built with Python. Download videos in multiple qualities or extract audio only - all with a simple, intuitive GUI.

![Application Preview](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

<div align="center">

## 📥 Quick Download

### **[⬇️ Download YTDownloader4k.exe (Windows)](https://github.com/ZabaHD4K/DescargadorYT/raw/main/YTDownloader4k.exe)**

**✨ No installation required • Works on any Windows PC • Auto-update notifications**

[Download Source Code](#-installation)

</div>

---

## ✨ Features

- 🎬 **Multiple Quality Options**: Maximum quality, 720p, or audio-only (MP3)
- 🎵 **Audio Extraction**: Download and convert to MP3 with high quality
- 🔄 **Auto-Update Notifications**: Alerts you when new versions are available with direct download link
- 💾 **Smart Downloads**: Automatically saves to your Downloads folder
- 🖥️ **User-Friendly GUI**: Clean, intuitive interface built with Tkinter
- 🌍 **Geo-Bypass**: Attempts to bypass geographical restrictions
- ⚡ **Fast & Reliable**: Powered by yt-dlp with retry mechanisms
- 📦 **Portable & Standalone**: No installation needed - just download and run!
- 🪟 **Universal Windows Support**: Works on Windows 7, 8, 10, and 11 without any dependencies

---

## 📋 Table of Contents

- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [System Requirements](#-system-requirements)
- [Building Executable](#-building-executable)
- [Project Structure](#-project-structure)
- [License](#-license)
- [Contributing](#-contributing)

---

## 🔧 How It Works

### Application Flow Diagram

```mermaid
graph TD
    A[Application Start] --> B[Check & Update Libraries]
    B --> C{Updates Available?}
    C -->|Yes| D[Update yt-dlp]
    C -->|No| E[Launch Main GUI]
    D --> E
    E --> F[User Enters YouTube URL]
    F --> G[User Selects Quality]
    G --> H[Click Download Button]
    H --> I{Validate URL}
    I -->|Invalid| J[Show Warning]
    I -->|Valid| K[Configure Download Options]
    K --> L[Start Download]
    L --> M{Download Success?}
    M -->|Yes| N[Show Success Message]
    M -->|No| O[Show Error Message]
    J --> F
    N --> P[File Saved to Downloads]
    O --> F
```

### Download Process Architecture

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant YT-DLP
    participant FFmpeg
    participant FileSystem

    User->>GUI: Enter YouTube URL
    User->>GUI: Select Quality
    User->>GUI: Click Download
    GUI->>GUI: Validate Input
    GUI->>YT-DLP: Request Video/Audio
    YT-DLP->>YT-DLP: Fetch Media Streams
    
    alt Video + Audio
        YT-DLP->>YT-DLP: Download Video Stream
        YT-DLP->>YT-DLP: Download Audio Stream
        YT-DLP->>FFmpeg: Merge Streams
        FFmpeg->>FileSystem: Save MP4 File
    else Audio Only
        YT-DLP->>YT-DLP: Download Audio Stream
        YT-DLP->>FFmpeg: Convert to MP3
        FFmpeg->>FileSystem: Save MP3 File
    end
    
    FileSystem->>GUI: Confirm Save
    GUI->>User: Show Success Message
```

### Auto-Update Process

```mermaid
sequenceDiagram
    participant App
    participant GitHub
    participant User

    App->>GitHub: Check latest release version
    GitHub-->>App: Return latest version info
    
    alt New Version Available
        App->>User: Show update dialog
        User->>App: Click "Update"
        App->>GitHub: Download new .exe
        GitHub-->>App: Send new executable
        App->>App: Replace old .exe
        App->>App: Restart application
    else No Update
        App->>App: Continue normally
    end
```

### Quality Selection Logic

```mermaid
flowchart LR
    A[Quality Selection] --> B{User Choice}
    B -->|Maximum Quality| C[bestvideo+bestaudio/best]
    B -->|720p| D[video≤720p+bestaudio]
    B -->|Audio Only| E[bestaudio only]
    
    C --> F[Merge to MP4]
    D --> F
    E --> G[Convert to MP3]
    
    F --> H[Save to Downloads]
    G --> H
```

---

## 💻 Installation

### 🪟 Windows Users (Easiest - Recommended)

**No installation required!** Just download and run:

1. **[⬇️ Download YTDownloader4k.exe](https://github.com/ZabaHD4K/DescargadorYT/raw/main/dist/YTDownloader4k.exe)**
2. **Double-click** to run
3. **Start downloading!**

✅ **Everything is included**: Python, yt-dlp, FFmpeg, and all dependencies are bundled inside the executable.  
✅ **Works immediately** on Windows 7/8/10/11 without installing anything.  
✅ **Portable**: Run it from anywhere - USB drive, desktop, or any folder.  
✅ **No admin rights needed**: Works on restricted computers.

---

### 🐍 Advanced: Install from Source

Only for developers or advanced users who want to run from Python source code.

#### Prerequisites

**Note:** These are only needed if running from Python source. The Windows .exe has everything included!

Before installation, ensure you have:

1. **Python 3.7 or higher** installed
2. **FFmpeg** installed on your system

#### Installing FFmpeg

**Windows:**
```powershell
# Using winget
winget install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

### Install from Source

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/YTDownloader4k.git
cd YTDownloader4k
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python descargador.py
```

---

## 🔄 Auto-Update Feature

The application includes **update notification functionality**:

### How It Works

1. **On Startup**: The app checks GitHub's `version.txt` for the latest version
2. **Version Comparison**: Compares your version with the latest available
3. **Update Notification**: If a new version exists, you'll see a dialog with:
   - ✅ **Download Update**: Opens your browser to download the new .exe
   - ⏭️ **Skip**: Continue with current version
4. **Simple Update**: Download the new .exe and replace the old one
5. **Library Updates**: Your dependencies (`yt-dlp`) are also kept up-to-date automatically

### Benefits

- 🔔 **Stay informed** - Know when updates are available
- 🛡️ **Bug fixes** - Get security and stability improvements
- ✨ **New features** - Access the latest functionality
- 📦 **User control** - You decide when to update

**Note**: Update notifications only work with the compiled executable (.exe), not when running from Python source.

---

## 🚀 Usage

### Quick Start (Windows - No Installation Required!)

1. **[Download YTDownloader4k.exe](https://github.com/ZabaHD4K/DescargadorYT/raw/main/dist/YTDownloader4k.exe)**
2. **Double-click** the downloaded file (no installation needed!)
3. **Enter** a YouTube URL
4. **Select** your desired quality
5. **Click Download**
6. **Done!** Find your file in the Downloads folder

**That's it!** The app works immediately on any Windows PC without installing Python, FFmpeg, or any dependencies. Everything is included in the single executable.

### Running from Source (Advanced Users)

```bash
python descargador.py
```

### Using the Executable (Windows)

**Quick Download:**
1. **[Click here to download YTDownloader4k.exe](https://github.com/ZabaHD4K/DescargadorYT/raw/main/YTDownloader4k.exe)** directly from this repo
2. Run `YTDownloader4k.exe` - **no installation required!**
3. The app will notify you if updates are available
4. Enter a YouTube URL
5. Select your desired quality
6. Click **Download**
7. Find your file in the **Downloads** folder

**✅ Works on any Windows without installation** - All dependencies are bundled inside the .exe file

### GUI Overview

```
┌─────────────────────────────────────────┐
│   Descargador de YouTube                │
│                                         │
│   Introduce la URL del video:          │
│   ┌───────────────────────────────────┐ │
│   │ https://youtube.com/watch?v=...   │ │
│   └───────────────────────────────────┘ │
│                                         │
│   Selecciona calidad:                   │
│   ┌───────────────────────────────────┐ │
│   │ Máxima calidad (video + audio)  ▼│ │
│   └───────────────────────────────────┘ │
│                                         │
│          ┌─────────────┐               │
│          │  Descargar  │               │
│          └─────────────┘               │
│                                         │
│   Los archivos se guardarán en tu      │
│   carpeta de Descargas                  │
└─────────────────────────────────────────┘
```

### Quality Options Explained

| Option | Description | File Type | Use Case |
|--------|-------------|-----------|----------|
| **Máxima calidad** | Best available video + audio quality | MP4 | High-quality archival, 4K viewing |
| **720p** | 720p video + high-quality audio | MP4 | Balanced quality/size, everyday use |
| **Solo audio (MP3)** | Audio only, converted to MP3 | MP3 | Music, podcasts, audio-only content |

---

## 🖥️ System Requirements

### For Windows Executable (Recommended)
- **OS**: Windows 7, 8, 10, or 11 (32-bit or 64-bit)
- **RAM**: 512 MB minimum
- **Storage**: 100 MB + space for downloads
- **Internet**: Stable connection required
- **NO INSTALLATION REQUIRED** - Everything is bundled in the .exe

### For Running from Source (Advanced)
- **OS**: Windows 7+, macOS 10.12+, or Linux
- **Python**: 3.7 or higher
- **RAM**: 512 MB
- **Storage**: 100 MB + space for downloads
- **Internet**: Stable connection required

### Recommended Requirements
- **OS**: Windows 10+, macOS 11+, or recent Linux
- **Python**: 3.9 or higher
- **RAM**: 2 GB
- **Storage**: 1 GB + space for downloads

---

## 📦 Building Executable

To create a standalone executable using PyInstaller:

```bash
# Navigate to src folder
cd src

# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name YTDownloader4k --icon=icon.ico descargador.py

# The executable will be in the 'src/dist' folder
# Copy it to the root
copy dist\YTDownloader4k.exe ..
```

### Build Options Explained

```bash
pyinstaller \
    --onefile \              # Create a single executable file
    --windowed \             # No console window (GUI only)
    --name YTDownloader4k \  # Name of the executable
    --icon=icon.ico \        # Add custom icon
    descargador.py           # Source Python file
```

---

## 📁 Project Structure

```
YTDownloader4k/
├── YTDownloader4k.exe      # ⭐ Ready-to-use executable (download this!)
├── version.txt             # Current version for update checks
├── README.md               # This file
└── src/                    # Source code folder
    ├── descargador.py      # Main application source code
    ├── requirements.txt    # Python dependencies
    ├── icon.ico            # Application icon
    ├── YTDownloader4k.spec # PyInstaller configuration
    ├── build/              # Build artifacts (git ignored)
    └── dist/               # Compiled outputs (git ignored)
    └── YTDownloader4k.exe
```

---

## 🔑 Key Technologies

### Core Dependencies

```mermaid
graph LR
    A[YTDownloader4K] --> B[yt-dlp]
    A --> C[Tkinter]
    A --> D[FFmpeg]
    
    B --> E[Video Download Engine]
    C --> F[GUI Framework]
    D --> G[Audio/Video Processing]
    
    style A fill:#d32f2f,color:#fff
    style B fill:#e57373,color:#fff
    style C fill:#81c784,color:#fff
    style D fill:#64b5f6,color:#fff
```

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: Modern YouTube downloader and fork of youtube-dl
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)**: Python's standard GUI library
- **[FFmpeg](https://ffmpeg.org/)**: Multimedia framework for audio/video processing

---

## 📄 License

This project is **open source** and available under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2026 Alejandro Zabaleta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

### 🆓 Free and Open Source

- ✅ **Both the source code and executable are free to use**
- ✅ **Open source** - inspect, modify, and distribute
- ✅ **No restrictions** - use for personal or commercial purposes
- ✅ **Community-driven** - contributions welcome

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute

1. 🐛 **Report Bugs**: Open an issue describing the problem
2. 💡 **Suggest Features**: Share your ideas for improvements
3. 🔧 **Submit Pull Requests**: Fix bugs or add features
4. 📖 **Improve Documentation**: Help make the docs clearer
5. 🌍 **Translations**: Add support for more languages

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/YTDownloader4k.git
cd YTDownloader4k

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make your changes and test
python descargador.py

# Submit a pull request
```

---

## 🐛 Troubleshooting

### Common Issues

#### "FFmpeg not found"
**Solution**: Install FFmpeg as described in the [Installation](#-installation) section.

#### "SSL Certificate Error"
**Solution**: The app automatically uses `nocheckcertificate: True` to handle this.

#### "Video unavailable"
**Solution**: The video might be private, deleted, or geo-restricted. Try using a VPN.

#### Download is slow
**Solution**: This depends on your internet connection and YouTube's servers. The app uses the fastest available method.

---

## � Author

**Alejandro Zabaleta**

Feel free to reach out for questions, suggestions, or collaborations!

---

## �📞 Support

- 📧 **Email**: support@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/YTDownloader4k/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/YTDownloader4k/discussions)

---

## 🌟 Acknowledgments

- Thanks to the [yt-dlp](https://github.com/yt-dlp/yt-dlp) team for the amazing download engine
- Thanks to the [FFmpeg](https://ffmpeg.org/) project for media processing capabilities
- Built with ❤️ by **Alejandro Zabaleta** using Python and Tkinter

---

## 📊 Project Status

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/YTDownloader4k)
![GitHub issues](https://img.shields.io/github/issues/yourusername/YTDownloader4k)
![GitHub stars](https://img.shields.io/github/stars/yourusername/YTDownloader4k?style=social)

---

<div align="center">
  
### ⭐ If you find this project useful, please consider giving it a star!

**Made with ❤️ for the community**

[Report Bug](https://github.com/yourusername/YTDownloader4k/issues) · [Request Feature](https://github.com/yourusername/YTDownloader4k/issues) · [Contribute](https://github.com/yourusername/YTDownloader4k/pulls)

</div>
