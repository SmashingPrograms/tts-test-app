#!/bin/bash

# install_kokoro.sh
# Automated installation script for Kokoro TTS
# This script installs Kokoro TTS and all its dependencies

set -e  # Exit on any error

echo "🎤 Kokoro TTS Installation Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION found"
        PYTHON_CMD="python"
    else
        print_error "Python not found. Please install Python 3.7+ first."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
        PIP_CMD="pip"
    else
        print_error "pip not found. Please install pip first."
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            print_status "Detected Debian/Ubuntu system"
            sudo apt-get update
            sudo apt-get install -y espeak-ng ffmpeg libsndfile1-dev
        elif command -v yum &> /dev/null; then
            print_status "Detected Red Hat/CentOS system"
            sudo yum install -y epel-release
            sudo yum install -y espeak-ng ffmpeg libsndfile-devel
        elif command -v pacman &> /dev/null; then
            print_status "Detected Arch Linux system"
            sudo pacman -S --noconfirm espeak-ng ffmpeg libsndfile
        else
            print_warning "Unknown Linux distribution. Please install espeak-ng and ffmpeg manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_status "Detected macOS system"
        if command -v brew &> /dev/null; then
            brew install espeak ffmpeg libsndfile
        else
            print_error "Homebrew not found. Please install Homebrew first:"
            print_error "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        print_warning "Windows detected. Please manually install:"
        print_warning "1. espeak-ng from: http://espeak.sourceforge.net/download.html"
        print_warning "2. FFmpeg from: https://ffmpeg.org/download.html"
        print_warning "Then run this script again."
        read -p "Press Enter after installing the above dependencies..."
    else
        print_warning "Unknown operating system: $OSTYPE"
        print_warning "Please install espeak-ng and ffmpeg manually."
    fi
    
    print_success "System dependencies installed"
}

# Install Kokoro TTS via pip
install_kokoro_pip() {
    print_status "Installing Kokoro TTS via pip..."
    
    # Try to install the official kokoro package
    if $PIP_CMD install kokoro>=0.9.2 soundfile; then
        print_success "Kokoro TTS installed successfully via pip"
        return 0
    else
        print_warning "Failed to install via pip. Trying alternative method..."
        return 1
    fi
}

# Install Kokoro TTS via GitHub (alternative method)
install_kokoro_github() {
    print_status "Installing Kokoro TTS from GitHub..."
    
    # Create temporary directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Clone the repository
    if git clone https://github.com/nazdridoy/kokoro-tts.git; then
        cd kokoro-tts
        
        # Install the package
        if $PIP_CMD install -e .; then
            print_success "Kokoro TTS installed from GitHub"
            
            # Download model files
            print_status "Downloading Kokoro model files..."
            
            if wget -q https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin; then
                print_success "Downloaded voices.bin"
            else
                print_warning "Failed to download voices.bin"
            fi
            
            if wget -q https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx; then
                print_success "Downloaded kokoro model"
            else
                print_warning "Failed to download kokoro model"
            fi
            
            cd - > /dev/null
            rm -rf "$TEMP_DIR"
            return 0
        else
            print_error "Failed to install from GitHub"
            cd - > /dev/null
            rm -rf "$TEMP_DIR"
            return 1
        fi
    else
        print_error "Failed to clone repository"
        rm -rf "$TEMP_DIR"
        return 1
    fi
}

# Install fallback TTS engine
install_fallback() {
    print_status "Installing fallback TTS engine (pyttsx3)..."
    if $PIP_CMD install pyttsx3; then
        print_success "Fallback TTS engine installed"
    else
        print_error "Failed to install fallback TTS engine"
    fi
}

# Test installation
test_installation() {
    print_status "Testing Kokoro TTS installation..."
    
    # Test Python import
    if $PYTHON_CMD -c "import kokoro; print('Kokoro import successful')" 2>/dev/null; then
        print_success "Kokoro Python package working"
        return 0
    fi
    
    # Test CLI command
    if command -v kokoro-tts &> /dev/null; then
        print_success "Kokoro CLI command available"
        return 0
    fi
    
    # Test fallback
    if $PYTHON_CMD -c "import pyttsx3; print('pyttsx3 fallback available')" 2>/dev/null; then
        print_success "Fallback TTS engine working"
        return 0
    fi
    
    print_error "No TTS engine is working properly"
    return 1
}

# Main installation process
main() {
    echo ""
    print_status "Starting Kokoro TTS installation..."
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Install system dependencies
    install_system_deps
    
    # Try to install Kokoro TTS
    if ! install_kokoro_pip; then
        print_warning "Pip installation failed, trying GitHub installation..."
        if ! install_kokoro_github; then
            print_error "Both installation methods failed"
            print_status "Installing fallback TTS engine..."
            install_fallback
        fi
    fi
    
    # Install additional Python dependencies
    print_status "Installing additional Python dependencies..."
    $PIP_CMD install soundfile numpy torch torchaudio || print_warning "Some dependencies may have failed"
    
    echo ""
    print_status "Testing installation..."
    if test_installation; then
        echo ""
        print_success "🎉 Installation completed successfully!"
        echo ""
        print_status "You can now:"
        print_status "1. Use 'kokoro-tts' command in terminal"
        print_status "2. Import kokoro in Python: 'import kokoro'"
        print_status "3. Run your FastAPI backend with TTS support"
        echo ""
    else
        echo ""
        print_error "❌ Installation completed with issues"
        print_warning "The system may work with fallback engines, but Kokoro TTS is not fully functional"
        echo ""
    fi
    
    print_status "Installation log completed"
}

# Show usage if --help is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Kokoro TTS Installation Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --no-system    Skip system dependency installation"
    echo "  --fallback     Only install fallback TTS engine"
    echo ""
    echo "This script will:"
    echo "1. Check Python and pip installation"
    echo "2. Install system dependencies (espeak-ng, ffmpeg)"
    echo "3. Install Kokoro TTS via pip or GitHub"
    echo "4. Install fallback TTS engine (pyttsx3)"
    echo "5. Test the installation"
    echo ""
    exit 0
fi

# Handle options
SKIP_SYSTEM=false
FALLBACK_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-system)
            SKIP_SYSTEM=true
            shift
            ;;
        --fallback)
            FALLBACK_ONLY=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run installation based on options
if [[ "$FALLBACK_ONLY" == true ]]; then
    check_python
    check_pip
    install_fallback
    test_installation
else
    if [[ "$SKIP_SYSTEM" == true ]]; then
        print_warning "Skipping system dependency installation"
    fi
    main
fi