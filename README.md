# 🤖 Suggest Bot v5.1

Telegram bot for collecting user suggestions and feedback with tag-based categorization. Automatically forwards suggestions to a specified chat, supports multiple content formats, and includes a comprehensive moderation system with API integration.

---

## ✨ Features

### 💡 Collecting Suggestions
* **Text suggestions** - any text messages
* **Photos** - with or without captions
* **Videos** - with or without captions
* **Tag-based categorization** - organize suggestions by type
* **Automatic forwarding** to target chat for moderation

### 🏷️ Tag System
* **Customizable tags** - predefined categories for suggestions
* **Visual tag selection** - user-friendly keyboard interface
* **Hashtag integration** - automatic hashtag assignment
* **Flexible configuration** - easy tag management

### 👥 User Management (API Integrated)
* **Centralized user database** - via REST API
* **Role system** with access rights (user, ladmin, gadmin, operator)
* **Real-time ban checks** - temporary and permanent bans
* **User info** via `/me` command with HTML formatting
* **API-based operations** - all user management through API

### ⚙️ Administrative Functions
* **Role-based access control** - granular permissions
* **Content moderation** - only allowed message types
* **Logging of all actions** - comprehensive audit trail
* **Flexible ban system** - temporary and permanent with automatic expiration

### 🛡️ Security
* **Username validation** - mandatory requirement
* **Content filtering** - only text, photo, and video
* **API authentication** - secure API key protection
* **HTML sanitization** - safe message formatting
* **Background cleanup** - automatic removal of expired data

---

## ⚙️ Installation and Run

### Requirements
* Python 3.8+
* Telegram Bot Token
* Chat ID for receiving suggestions
* Running Suggest Bot API (routes.py)

### Installation

1. Clone the project:
```bash
git clone <repo_url>
cd sgs-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file and configure parameters:
```env
# Bot Configuration
SGS_TOKEN=your_telegram_bot_token
SGS_CHAT_ID=chat_id_for_suggestions

# API Configuration
API_URL=http://localhost:5000
API_KEY=your_api_key_here

# System Configuration
DATA_DIR=data
LOGS_DIR=logs
MAX_WARN=3
DEFAULT_BAN_TIME=24
```

4. Ensure the API server is running (routes.py)

5. Run the bot:
```bash
python bot_core.py
```

### Project Structure
```
sgs-bot/
├── bot_core.py           # Main bot module
├── database_manager.py   # API integration and database operations
├── utils.py              # Utilities (tags, validators, formatters)
├── config.py             # Configuration management
├── logger.py             # Advanced logging with daily rotation
├── requirements.txt
├── .env
├── data/
│   └── tags.json         # Tag definitions
└── logs/                 # Daily log files
```

---

## 🎮 Usage

### Main Commands
* **`/start`** - registration and welcome message
* **`/me`** - information about your account (HTML formatted)
* **`/help`** - help with using the bot

### Sending Suggestions

1. Send your suggestion as:
   * 📝 **Text message** - any suggestion or idea
   * 📸 **Photo** - with or without caption
   * 🎥 **Video** - with or without caption

2. **Select a tag** from the interactive keyboard
3. **Confirm sending** with or without tag

**Example Flow:**
```
User: Hi! I suggest adding dark mode...
Bot: ✅ Content received! Now select a tag for your suggestion:
[💡 Idea] [🚀 Improvement] [📤 Send without tag]

User: 💡 Idea
Bot: ✅ Your suggestion has been sent with tag Idea!
```

### Tag System
* **Predefined categories**: Bug, Idea, Improvement, Documentation, Design
* **Customizable**: Modify `data/tags.json` to add new categories
* **Visual interface**: Easy selection via reply keyboard

---

## Tags Configuration
**tags.json:**
```json
{
  "🐛 Bug": "#bug",
  "💡 Idea": "#idea",
  "🚀 Improvement": "#improvement",
  "📝 Documentation": "#documentation",
  "🎨 Design": "#design"
}
```

---

## 👥 Role System

### 🎯 Access Levels
* **👤 User** - can send suggestions
* **🪛 Local Administrator** - basic moderation rights for specific bots
* **🔧 Global Administrator** - extended management rights across system
* **⚡ Operator** - full system control

### 🔐 Command Rights
| Command   | User | Local Admin | Global Admin | Operator |
| --------- | ---- | ----------- | ------------ | -------- |
| `/start`  | ✅    | ✅           | ✅            | ✅        |
| `/me`     | ✅    | ✅           | ✅            | ✅        |
| `/help`   | ✅    | ✅           | ✅            | ✅        |

---

## 📊 Logging

The bot keeps detailed logs with daily rotation:
* `logs/log_YYYY.MM.DD.log` - daily log files
* Registration of all incoming suggestions with tags
* Real-time API interactions
* System errors and warnings
* Suggestion forwarding status

**Example log:**
```
2024-01-15 10:30:00 - SuggestBot - INFO - Suggestion from @username forwarded to chat 12345 with tag Idea
2024-01-15 10:31:00 - SuggestBot - INFO - API: User @username created successfully
```

---

## ⚠️ Limitations

### 📵 Unsupported Content Types
* ❌ Documents (files)
* ❌ Audio messages
* ❌ Voice messages
* ❌ Stickers
* ❌ Locations
* ❌ Contacts

### 🔒 User Requirements
* ✅ Username required
* ✅ Registration via `/start`
* ✅ No active bans
* ✅ Valid API connection

---

## 🚀 Performance
* **Modular architecture** - clean separation of concerns
* **API integration** - centralized user management
* **HTML formatting** - improved message presentation
* **Background cleanup** - automatic removal of expired suggestions
* **Daily log rotation** - efficient log management

---

## 🆘 Support

If you encounter issues:

1. **Check .env settings** - token, chat ID, and API configuration
2. **Ensure API server is running** (routes.py)
3. **Check logs** in `logs/log_YYYY.MM.DD.log`
4. **Verify API connectivity** - ensure API_URL and API_KEY are correct
5. **Ensure** the bot is added to the target chat with admin rights

**Important:** The bot must have permission to send messages in the target chat!

### Common Issues
* **"User not registered"** - Use `/start` command first
* **"Username required"** - Set username in Telegram settings
* **"API connection failed"** - Check API_URL and API_KEY in .env
* **Tag selection not appearing** - Check `data/tags.json` file exists and is valid JSON

---

## 🔄 Migration from v4.1
- **New**: API integration for centralized user management
- **New**: HTML formatted messages with better presentation
- **New**: Modular architecture (3 main modules + config)
- **New**: Daily log rotation system
- **Updated**: Database schema with enhanced relationships
- **Updated**: Role system with local/global admins and operators
- **Improved**: Security with API key authentication

---

**Version:** 5.1 