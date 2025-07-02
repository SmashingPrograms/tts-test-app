# Real-time TTS App Setup

This is a complete React + FastAPI application for real-time text-to-speech using Kokoro TTS.

## Project Structure
```
tts-app/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── requirements.txt     # Python dependencies
│   └── install_kokoro.sh    # Kokoro installation script
├── frontend/
│   ├── src/
│   │   └── App.js          # React component (provided above)
│   ├── package.json        # Node dependencies
│   └── public/
└── README.md
```

## Backend Setup (FastAPI + Kokoro TTS)

### 1. Install Python Dependencies

Create `backend/requirements.txt`:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
pyttsx3==2.90  # Fallback TTS engine
```

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Kokoro TTS (Primary Engine)

**Option A: Official Kokoro Package (Recommended)**
```bash
# Install Kokoro TTS
pip install kokoro>=0.9.2 soundfile

# Install espeak-ng (required dependency)
# On Ubuntu/Debian:
sudo apt-get install espeak-ng

# On macOS:
brew install espeak

# On Windows:
# Download and install espeak from: http://espeak.sourceforge.net/download.html
```

**Option B: CLI Installation**
```bash
# Clone and install Kokoro CLI
git clone https://github.com/nazdridoy/kokoro-tts.git
cd kokoro-tts
pip install -e .

# Download required model files
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin
wget https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx
```

### 3. Run Backend
```bash
cd backend
python main.py
# Server will start at http://localhost:8000
```

## Frontend Setup (React)

### 1. Create React App
```bash
npx create-react-app frontend
cd frontend
```

### 2. Install Dependencies
```bash
npm install lucide-react
```

### 3. Update package.json
Add to `frontend/package.json`:
```json
{
  "name": "tts-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "lucide-react": "^0.263.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "proxy": "http://localhost:8000",
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### 4. Replace src/App.js
Replace the contents of `src/App.js` with the React component provided above.

### 5. Update src/index.css (Optional Styling)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
```

### 6. Install Tailwind CSS
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 7. Run Frontend
```bash
npm start
# App will open at http://localhost:3000
```

## Usage

1. **Start Backend**: `cd backend && python main.py`
2. **Start Frontend**: `cd frontend && npm start` 
3. **Open Browser**: Navigate to `http://localhost:3000`
4. **Type Text**: Enter text in the textarea
5. **Generate Speech**: Press Enter or click "Generate & Play"

## Features

- ✅ Real-time text-to-speech generation
- ✅ Multiple voice options (Kokoro TTS voices)
- ✅ Adjustable speech speed
- ✅ Play/Stop controls
- ✅ Enter key shortcut
- ✅ Character counter
- ✅ Error handling
- ✅ Responsive design

## Troubleshooting

### Backend Issues
1. **Kokoro not found**: Install using pip or follow CLI installation
2. **espeak-ng missing**: Install system dependency
3. **CORS errors**: Check frontend is running on port 3000

### Frontend Issues
1. **API connection failed**: Ensure backend is running on port 8000
2. **Audio won't play**: Check browser audio permissions
3. **Styling issues**: Ensure Tailwind CSS is installed

### Alternative TTS Engines

If Kokoro doesn't work, the backend falls back to:
1. **pyttsx3**: Basic TTS (install: `pip install pyttsx3`)
2. **System TTS**: Uses OS built-in text-to-speech

## Production Deployment

### Backend (FastAPI)
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend (React)
```bash
# Build for production
npm run build

# Serve with nginx or any static file server
npx serve -s build
```

## API Endpoints

- `GET /` - Health check
- `POST /generate-speech` - Generate TTS audio
- `GET /voices` - List available voices
- `GET /health` - Service status

Enjoy your real-time TTS app! 🎤