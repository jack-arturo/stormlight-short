# 🔐 Security Configuration

## API Key Management

### ✅ Current Setup
- **Environment Variable**: `GEMINI_API_KEY` set in `~/.zshrc`
- **Local .env File**: Contains all project environment variables
- **Git Protection**: `.env` files are in `.gitignore`
- **Template**: `.env.template` provided for other developers

### 🛡️ Security Measures
1. **Never commit API keys** - `.env` files are git-ignored
2. **Environment isolation** - Keys loaded from `.env` file automatically
3. **Shell persistence** - Key added to `~/.zshrc` for permanent access
4. **Template system** - `.env.template` shows required variables without secrets

### 🔄 For Other Developers
```bash
# 1. Copy the template
cp .env.template .env

# 2. Edit .env with your actual API key
nano .env

# 3. Add to your shell profile
echo 'export GEMINI_API_KEY=your_key_here' >> ~/.zshrc
source ~/.zshrc
```

### 🚨 If Key is Compromised
1. **Revoke** the key at https://aistudio.google.com/app/apikey
2. **Generate** a new key
3. **Update** both `.env` file and `~/.zshrc`
4. **Restart** your terminal

### 📋 Environment Variables
- `GEMINI_API_KEY` - Gemini API authentication
- `GCP_PROJECT_ID` - Google Cloud project ID
- `GCS_BUCKET` - Cloud Storage bucket name
- `DEBUG` - Development mode flag
- `LOG_LEVEL` - Logging verbosity

---
**✅ All tools automatically load from `.env` - no manual configuration needed!**
