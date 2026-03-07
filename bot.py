import os
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
from fuzzywuzzy import process
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ========= CONFIG =========
BOT_TOKEN = "7570710604:AAF5rnPjLz1F69g67KtBnoBgdXOPK_7ZwxE"
SPREADSHEET_ID = "1T84RPPic4jANe3LtSRvsjPr7HInOrp_PTTBjfatAbDE"
# ==========================

# Connect to Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ===== SEARCH FUNCTION =====
def find_best_match(query):
    data = sheet.get_all_records()
    topics = [row['Topic Keyword'] for row in data]

    match, score = process.extractOne(query, topics)

    if score > 60:
        for row in data:
            if row['Topic Keyword'].lower() == match.lower():
                return f"📘 *{match.title()}*\n{row['Google Drive Link']}"

    return "❌ Sorry, no matching notes found."

# ===== BOT COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi!\n\n"
        "Type subject name, teacher name, seminar, or topic.\n"
        "I will send the Google Drive notes.\n\n"
        "Made with ❤️ by Tutorain"
    )

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    result = find_best_match(query)
    await update.message.reply_text(result)

# ===== TELEGRAM APPLICATION =====
application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

# ===== FLASK SERVER =====
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Telegram Bot Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)

    import asyncio
    asyncio.run(application.process_update(update))

    return "ok"

# ===== START SERVER =====
if __name__ == "__main__":
    import asyncio

    async def main():
        await application.initialize()
        await application.start()

    asyncio.get_event_loop().run_until_complete(main())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)



