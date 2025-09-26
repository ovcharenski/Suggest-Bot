# 🤖 Suggest Bot v4.1

Telegram bot for collecting user suggestions and feedback with tag-based categorization. Automatically forwards suggestions to a specified chat, supports multiple content formats, and includes a comprehensive moderation system.

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

### 👥 User Management

* **Automatic registration** of new users
* **Role system** with access rights
* **Ban and warning checks**
* **User info** via /me command
* **SQLite database** - efficient user data storage

### ⚙️ Administrative Functions

* **Role-based access control** - granular permissions
* **Content moderation** - only allowed message types
* **Logging of all actions** - comprehensive audit trail
* **Flexible ban system** (temporary and permanent)

### 🛡️ Security

* **Username validation** - mandatory requirement
* **Content filtering** - only text, photo, and video
* **Anti-spam protection** via warnings
* **Access rights validation**
* **SQL injection protection** - parameterized queries

---

## ⚙️ Installation and Run

### Requirements

* Python 3.8+
* Telegram Bot Token
* Chat ID for receiving suggestions

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
SGS_TOKEN=your_telegram_bot_token
SGS_CHAT_ID=chat_id_for_suggestions
DATA_DIR=data                    # Directory for data
LOGS_DIR=logs                    # Directory for logs
MAX_WARN=3                       # Maximum number of warnings
```

4. Run the bot:

```bash
python sgs-bot.py
```

### Build as Executable (optional)

To create a standalone version:

```bash
pyinstaller --onefile --add-data ".env;." --additional-hooks-dir=. sgs-bot.py
```

---

## 🎮 Usage

### Main Commands

* **`/start`** - registration and welcome message
* **`/me`** - information about your account
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
Bot: ✅ Содержание получено! Теперь выберите тег для вашего предложения:
[💡 Идея] [🚀 Улучшение] [📤 Отправить без тега]

User: 💡 Идея
Bot: ✅ Ваше предложение отправлено с тегом Идея!
```

### Tag System

* **Predefined categories**: Bug, Idea, Improvement, Documentation, Design
* **Customizable**: Modify tags.json to add new categories
* **Visual interface**: Easy selection via reply keyboard

---

## 🗃️ Data Structure

### Database Schema

```
data/
├── system.db           # SQLite database (users, bans, permissions)
├── tags.json           # Tag definitions and hashtags
└── welcome_message.txt # Welcome message (reserved)
```

### Database Tables

**users table:**
- username (TEXT PRIMARY KEY)
- user_id (INTEGER)
- first_name (TEXT)
- rank (TEXT)
- warns (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**bans table:**
- username (TEXT PRIMARY KEY)
- ban_time (INTEGER)  # hours, 0 = permanent
- banned_at (INTEGER) # timestamp
- reason (TEXT)

**operators/global_admins tables:**
- username (TEXT PRIMARY KEY)

### Tags Configuration

**tags.json:**
```json
{
  "🐛 Баг": "#баг",
  "💡 Идея": "#идея", 
  "🚀 Улучшение": "#улучшение",
  "📝 Документация": "#документация",
  "🎨 Дизайн": "#дизайн"
}
```

---

## 👥 Role System

### 🎯 Access Levels

* **👤 User** - can send suggestions
* **🪛 Local Administrator** - basic moderation rights  
* **🔧 Global Administrator** - extended management rights
* **⚡ Operator** - full system control

### 🔐 Command Rights

| Command   | User | Local Admin | Global Admin | Operator |
| --------- | ---- | ----------- | ------------ | -------- |
| `/start`  | ✅    | ✅           | ✅            | ✅        |
| `/me`     | ✅    | ✅           | ✅            | ✅        |
| `/help`   | ✅    | ✅           | ✅            | ✅        |

---

## 📊 Logging

The bot keeps detailed logs of all actions:

* `logs/sgs-bot.log` - main bot logs
* Registration of all incoming suggestions with tags
* Tracking admin actions
* System errors and warnings
* Suggestion forwarding status

**Example log:**
```
2024-01-15 10:30:00 - sgs-bot - INFO - Suggestion from @username forwarded to chat 12345 with tag Идея
2024-01-15 10:31:00 - sgs-bot - INFO - New user registered: username
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
* ✅ Registration via /start
* ✅ No active bans

---

## 🚀 Performance

* **Asynchronous message processing**
* **SQLite database** - optimized data storage
* **Automatic directory creation**
* **Background cleanup** of expired suggestions
* **Minimal system load**

---

## 🆘 Support

If you encounter issues:

1. **Check .env settings** - token and chat ID
2. **Ensure access rights** to directories
3. **Check logs** in `logs/sgs-bot.log`
4. **Verify database integrity** in `data/system.db`
5. **Ensure** the bot is added to the target chat with admin rights

**Important:** The bot must have permission to send messages in the target chat!

### Common Issues

* **"User not registered"** - Use `/start` command first
* **"Username required"** - Set username in Telegram settings
* **Tag selection not appearing** - Check `tags.json` file exists and is valid JSON

---

**Version:** 4.1 