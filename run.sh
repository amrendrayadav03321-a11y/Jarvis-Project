# Ensure Homebrew ARM64 binaries (flac, ffmpeg, python) are in PATH
export PATH="/opt/homebrew/bin:$PATH"

# Resolve project directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "$DIR/venv" ]; then
    echo "Virtual environment not found. Setting up..."
    /opt/homebrew/bin/python3.12 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

# Run Jarvis Voice Assistant
./venv/bin/python3 "$DIR/jarvis.py" "$@"
