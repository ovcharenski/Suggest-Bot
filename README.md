# 🤖 Suggest Bot v3.1

Telegram bot for collecting user suggestions and feedback. Automatically forwards suggestions to a specified chat, supports multiple content formats, and includes a moderation system.

---

## ✨ Features

### 💡 Collecting Suggestions

* **Text suggestions** - any text messages
* **Photos** - with or without captions
* **Videos** - with or without captions
* **Automatic forwarding** to target chat for moderation

### 👥 User Management

* **Automatic registration** of new users
* **Role system** with access rights
* **Ban and warning checks**
* **User info** via /me command

### ⚙️ Administrative Functions

* **Set welcome message** (/setmg)
* **Content moderation** - only allowed message types
* **Logging of all actions**
* **Flexible ban system** (temporary and permanent)

### 🛡️ Security

* **Username validation** - mandatory requirement
* **Content filtering** - only text, photo, and video
* **Anti-spam protection** via warnings
* **Access rights validation**

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
SUPER_OPERATOR=username          # Super-operator of the system
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
* **`/setmg [text]`** - set welcome message (admins only)
* **`/chatid`** - get chat id

### Sending Suggestions

Simply send the bot:

* 📝 **Text message** - any suggestion or idea
* 📸 **Photo** - with or without caption
* 🎥 **Video** - with or without caption

**Example:**

```
User: Hi! I suggest adding a new feature...
Bot: ✅ Your suggestion has been sent!
```

### For Administrators

```
Admin: /setmg Welcome! Send your suggestions and ideas.
Bot: ✅ Welcome message updated!
```

---

## 🗃️ Data Structure

### Configuration Files

```
data/
├── users.json        # User data
├── banned.json       # Banned users
├── admins.json       # Admins and operators
├── bots_data.json    # Bot data (reserved)
├── auth_codes.json   # Authorization codes (reserved)
└── welcome_message.txt # Welcome message
```

### File Formats

**users.json**:

```json
{
  "username": {
    "id": 123456789,
    "first_name": "User Name",
    "rank": "user",
    "banned": false,
    "warns": 0
  }
}
```

**banned.json**:

```json
{
  "username": {
    "ban_time": 24,
    "banned_at": 1672531200,
    "reason": "spam"
  }
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
| `/setmg`  | ❌    | ❌           | ✅            | ✅        |
| `/chatid` | ❌    | ❌           | ✅            | ✅        |

---

## 📊 Logging

The bot keeps detailed logs of all actions:

* `logs/sgs-bot.log` - main bot logs
* Registration of all incoming suggestions
* Tracking admin actions
* System errors and warnings

**Example log:**

```
2024-01-15 10:30:00 - sgs-bot - INFO - Suggestion from @username forwarded to chat 12345
2024-01-15 10:31:00 - sgs-bot - INFO - Welcome message updated by admin_user
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
* ✅ No bans

---

## 🚀 Performance

* **Asynchronous message processing**
* **Optimized data storage**
* **Automatic directory creation**
* **Minimal system load**

---

## 🆘 Support

If you encounter issues:

1. **Check .env settings** - token and chat ID
2. **Ensure access rights** to directories
3. **Check logs** in `logs/sgs-bot.log`
4. **Ensure** the bot is added to the target chat with admin rights

**Important:** The bot must have permission to send messages in the target chat!

---

**Version:** 3.1
