import logging
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

import asyncio

bot_token = 'Bot_token'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="HEY "+update.effective_user.first_name + "\n Pachathavala_here!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    user_info = f"user={update.effective_user.first_name} {
        update.effective_user.last_name}"

    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file_id)
        message_text = "Photo received"
    full_message = f"{message_text} \n {user_info} "
    await context.bot.send_message(chat_id=update.effective_chat.id, text=full_message)


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    response = await context.bot.send_message(chat_id=update.effective_chat.id, text="Pinging...")
    end_time = time.time()
    await response.edit_text(f"Pong! {end_time - start_time:.2f} seconds")

DATE, TIME, MESSAGE = 0, 1, 2

remainders = []


async def remainder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter date in format (YYYY-MM-DD)")
    return DATE


async def date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['date'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter time in format (HH:MM AM/PM)")
    return TIME


async def time_input(update, context):
    context.user_data['time'] = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter message")
    return MESSAGE


async def message_input(update, context):
    remainder = {
        'date': context.user_data['date'],
        'time': context.user_data['time'],
        'message': update.message.text,
        'chat_id': update.effective_chat.id
    }
    remainders.append(remainder)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Remainder set for "+context.user_data['date']+" "+context.user_data['time'])
    return ConversationHandler.END


async def remainderlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "             -------Remainders-------\n"
    for remainder in remainders:
        message += f"  Message: {remainder['message']}\n,Date: {
            remainder['date']}\n,Time: {remainder['time']}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Cancelled")
    return ConversationHandler.END

async def send(application, chat_id, text):
    await application.bot.send_message(chat_id=chat_id, text="Remainder Alert\n\n"+text+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
   # await application.bot.answer_callback_query(callback_query_id=chat_id, text="Notification already enabled", show_alert=True);

if __name__ == '__main__':
 
 application = ApplicationBuilder().token(
    bot_token).build()


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
 application.add_handler(CommandHandler('ping', ping))
 application.add_handler(CommandHandler('remainderlist', remainderlist))

 application.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND, echo))
 application.add_handler(MessageHandler(filters.PHOTO, echo))

def send_message_raw(chat_id, message):
    from requests import get

    req = get("https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+str(chat_id)+"&text="+message)
    print(req.text)
 


def alert():
    while True:
        print("Checking for remainders")
        # current_time = arrow.now().format('YYYY-MM-DD HH:mm A')
        current_time = time.strftime("%Y-%m-%d %I:%M %p", time.localtime())
        print("current time:  " + current_time)
       
        for remainder in remainders:
            wrp = f"{remainder['date']} {remainder['time']}"
            print("remainder time " +wrp)
            if current_time == f"{remainder['date']} {remainder['time']}":
                print("Sending remainder")
                send_message_raw(remainder['chat_id'], remainder['message'])
                
                del remainders[remainders.index(remainder)]

        time.sleep(10)
                
        
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_in_executor(None, alert)

# application.
try:
    application.run_polling()
except KeyboardInterrupt:
    print("Exiting")
    exit(0)
