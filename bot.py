import gspread
import asyncio
import nest_asyncio
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import Update
from fuzzywuzzy import process

nest_asyncio.apply()

# ========== CONFIG ==========
BOT_TOKEN = "7570710604:AAF5rnPjLz1F69g67KtBnoBgdXOPK_7ZwxE"  # ← replace with your bot token
SPREADSHEET_ID = "1T84RPPic4jANe3LtSRvsjPr7HInOrp_PTTBjfatAbDE"  # ← your sheet ID
# ============================

# STEP 1: Connect to Google Sheet
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1
data = sheet.get_all_records()

# STEP 2: Search logic
def find_best_match(query):
    topics = [row['Topic Keyword'] for row in data]
    match, score = process.extractOne(query, topics)
    if score > 60:
        for row in data:
            if row['Topic Keyword'].lower() == match.lower():
                return f"📘 *{match.title()}*: {row['Google Drive Link']}"
    return "❌ Sorry, no matching notes found."

# STEP 3: Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! Just type the topic like 'S2', 'ADSA', or 'AOS' and I'll give you the note link!")

async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    result = find_best_match(query)
    await update.message.reply_text(result)


# STEP 4: Start the bot
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))
    print("✅ Bot is running... Open Telegram and talk to it!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

