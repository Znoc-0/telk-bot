import logging
import time
import arrow
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler ,MessageHandler, filters ,ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
#/start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="HEY "+update.effective_user.first_name +"\n Pachathavala_here!")

# echoing back the message
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_info = f"user={update.effective_user.first_name} {update.effective_user.last_name}"
   
    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id)
        message_text = "Photo received"
    full_message = f"{message_text} \n {user_info} "
    await context.bot.send_message(chat_id=update.effective_chat.id, text=full_message)
#response to ping command
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    response= await context.bot.send_message(chat_id=update.effective_chat.id, text="Pinging...")
    end_time = time.time()
    await response.edit_text(f"Pong! {end_time - start_time:.2f} seconds")
# remainder settings
DATE, TIME, MESSAGE = range(3)

remainders = []


async def remainder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter date in format (YYYY-MM-DD)")
    return DATE

async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter time in format (HH:MM AM/PM)")
    return TIME

async def time_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    context.user_data['time'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter message")
    return MESSAGE

async def message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    remainder = {
     'date': context.user_data['date'],
     'time': context.user_data['time'],
     'message': update.message.text
    }
    remainders.append(remainder)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Remainder set for "+context.user_data['date']+" "+context.user_data['time'])
    return ConversationHandler.END

async def remainderlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "             -------Remainders-------\n"
    for remainder in remainders:
        message += f"  Message: {remainder['message']}\n,Date: {remainder['date']}\n,Time: {remainder['time']}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled")
    return ConversationHandler.END
    
from time import sleep

#async def alert(context: ContextTypes.DEFAULT_TYPE):
 #   while True:
  #      current_time = arrow.now().format('YYYY-MM-DD HH:mm A')
   #     print(current_time)
    #    for remainder in remainders:
     #       if current_time == f"{remainder['date']} {remainder['time']}":
      #          await context.bot.send_message(chat_id=context.user_data['chat_id'], text=remainder['message'])
       # sleep(60)

if __name__ == '__main__':
    application = ApplicationBuilder().token('7289346039:AAHdJxkSModalZ3JsUJEJMmEnyAP5t-Cpuo').build()
    

    application.add_handler(ConversationHandler(
        entry_points=[CommandHandler('remainder', remainder)],
        states={
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_input)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, time_input)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, message_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
        ))
    start_handler = CommandHandler('start', start)
   
    application.add_handler(start_handler)
    application.add_handler( CommandHandler('ping', ping))
    application.add_handler(CommandHandler('remainderlist', remainderlist))

    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.PHOTO, echo))
    
 
# Start the alert loop in a separate task
    
    application.run_polling()