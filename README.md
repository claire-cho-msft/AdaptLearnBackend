# AdaptLearn Backend - Intelligent Documentation System

A Flask-based documentation/tutorial system that converts markdown files into interactive tutorials with **AI-powered content adaptation** for different skill levels.

## Features

### Core Features
- ✅ **Markdown to JSON conversion** with proper HTML rendering
- ✅ **YAML front matter handling** - cleanly stripped before processing
- ✅ **Microsoft Docs features support**:
  - [!NOTE] blocks and other callouts rendered properly
  - Zone pivots handled (simplified to show first zone)
  - Tabbed content support
- ✅ **Clean rendering** - no duplicate notes, no raw syntax, no unnecessary URL params
- ✅ **Sidebar navigation** from `index.yml` structure
- ✅ **"In this article" TOC** based on H2 headers
- ✅ **Interactive elements** with proper CSS/JS for code blocks and sliders

### 🆕 NEW: Local AI-Powered Content Adaptation
- ✅ **Smart difficulty levels** - Each section has a 3-level slider (Easy → Intermediate → Advanced)
- ✅ **Local AI content adaptation** - Uses Hugging Face transformers to rewrite content for different skill levels
- ✅ **No API keys required** - Runs completely locally with no quotas or costs
- ✅ **Real-time adaptation** - Content changes instantly when you move the slider
- ✅ **Caching system** - Adapted content is cached to improve performance
- ✅ **Offline capability** - Works without internet connection after initial model download

## How Content Adaptation Works

### The Sliders
Each tutorial section has a 3-position slider at the top:
- **Left (Easy)**: Content adapted for complete beginners
- **Middle (Intermediate)**: Content adapted for users with some experience  
- **Right (Advanced)**: Original technical content (default)

### Content Adaptation Levels

**🟢 Easy Level (Position 0)**
- Uses simple, non-technical language
- Explains technical terms in plain English
- Breaks down complex concepts into smaller steps
- Adds helpful context and explanations
- Perfect for complete beginners

**🟡 Intermediate Level (Position 1))**  
- Uses clear, professional language with some technical terms
- Focuses on practical implementation
- Assumes basic familiarity with development tools
- Provides useful tips for common scenarios

**🔴 Advanced Level (Position 2)**
- Original technical documentation (no adaptation)
- Assumes expert-level knowledge
- Uses standard technical terminology

## Quick Start

### 1. Setup
```bash
# Clone and navigate to the project
cd AdaptLearnBackend

# Run the setup script
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Install all required Python packages
- Help you configure your OpenAI API key (optional)
- Set up environment variables

### 2. Setup Local AI Model (Automatic)
The system now uses a local Hugging Face model instead of OpenAI:
- **No API keys needed** - everything runs locally
- **No quotas or costs** - unlimited usage
- **First run setup** - model downloads automatically (may take a few minutes)
- **Offline capability** - works without internet after initial setup

The system uses Microsoft DialoGPT-medium for content adaptation.

### 3. Run the Application
```bash
cd src
python3 app.py
```

Visit: http://localhost:5000/tutorial

## How to Use

1. **Browse tutorials** - Start with the overview page
2. **Try the sliders** - Each section has a difficulty slider at the top
3. **Move sliders left** for easier explanations, right for advanced content
4. **Watch content adapt** - The AI will rewrite the content in real-time

## Technical Details

### File Structure
```
AdaptLearnBackend/
├── src/
│   ├── app.py              # Main Flask app with LLM integration
│   └── templates/
│       └── index.html      # Template with slider interactions
├── markdown/               # Your markdown documentation files
├── parser/                 # Sidebar structure parser
├── requirements.txt        # Python dependencies
├── setup.sh               # Setup script
└── .env                   # Environment variables (created by setup)
```

### API Endpoints
- `GET /tutorial/<filename>` - Load and render tutorial
- `POST /slider-update` - Update slider state
- `POST /adapt-content` - Adapt content using LLM

### Content Adaptation Flow
1. User moves slider to easy/intermediate position
2. Frontend sends request to `/adapt-content` endpoint
3. Backend extracts section text content
4. Local Hugging Face model adapts content based on difficulty level
5. Adapted content is cached and returned
6. Frontend updates the section with new content

## Performance Notes

### First Run
- **Model Download**: First run downloads ~500MB model (one-time)
- **Initial Load**: First adaptation takes 30-60 seconds as model loads into memory
- **Subsequent Runs**: Much faster due to model caching

### Hardware Requirements
- **RAM**: 4GB+ recommended (model uses ~1-2GB when loaded)
- **Storage**: 1GB for model files
- **GPU**: Optional - will use CUDA if available for faster processing
- **CPU**: Works on any modern CPU (slower but functional)

## Customization

### Adding New Tutorials
1. Add `.md` files to the `markdown/azure-developer-cli/` directory
2. Use standard Microsoft Docs format with YAML front matter
3. The system will automatically process them

### Customizing Adaptation Prompts
Edit the `level_prompts` dictionary in `adapt_content_for_level()` function in `app.py`.

### Using Different AI Models
You can change the model by modifying the `model_name` variable in `app.py`:
- `"microsoft/DialoGPT-medium"` - Current default (good balance)
- `"distilgpt2"` - Faster, smaller model
- `"gpt2"` - Standard GPT-2 model
- Any other compatible Hugging Face model

### Styling
Modify the CSS in `templates/index.html` to customize the appearance.

## Without Internet Connection

The system works fully offline after initial setup:
- All basic features work normally
- Content adaptation works using local AI model
- Only initial model download requires internet
- Perfect for air-gapped or restricted environments

## Troubleshooting

### Common Issues
1. **"Model not available"** - First run is downloading the model, wait a few minutes
2. **Slow adaptation** - First requests are slower as model loads, subsequent ones use cache
3. **Out of memory** - Try using a smaller model like "distilgpt2" 
4. **Adaptation fails** - Content will remain at advanced level, check console for errors

### Performance Tips
- **GPU acceleration** - Install CUDA-compatible PyTorch for faster processing
- **Model selection** - Use smaller models for faster response times
- **Memory management** - Close other applications if running out of RAM
- **Caching** - Adapted content is cached, so repeated requests are instant

### Logs
Check the terminal output for detailed logs about:
- AI model loading status
- Content adaptation processing
- Performance metrics
- Error messages

## Advantages of Local AI

### 🚀 **Performance Benefits**
- **No API rate limits** - unlimited usage
- **No network latency** - instant responses after model loads
- **Consistent availability** - works offline

### 💰 **Cost Benefits**  
- **Zero API costs** - no per-request charges
- **No quotas** - unlimited content adaptation
- **One-time setup** - no ongoing expenses

### 🔒 **Privacy Benefits**
- **Data stays local** - content never leaves your machine
- **No external APIs** - complete privacy
- **Offline capability** - works in air-gapped environments

## Contributing

This system is designed to be easily extensible:
- Add new content types to the markdown processor
- Integrate different LLM providers
- Add more difficulty levels
- Customize adaptation strategies per content type

---

**Built with ❤️ for making technical documentation accessible to everyone**