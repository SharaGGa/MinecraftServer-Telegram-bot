import subprocess
import threading
import time
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def logs(update, context):
    with open('./logs/latest.log', 'r') as file:
        timer.sleep(5)
        contents = file.read()
        update.message.reply_text(contents)


class MinecraftServer:

    def __init__(self):
        self.process = None
        self.logs = []
        self.thread = None
        self.last_log_index = 0

    def start(self):

        if self.process is None:
            self.process = subprocess.Popen(["java", "-Xmx1024M", "-Xms1024M", "-jar", "server.jar", "nogui"],
                                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True)
            self.thread = threading.Thread(target=self.capture_output)
            self.thread.start()

    def stop(self):
        if self.process is not None:
            self.send_command("stop")
            self.thread.join()
            self.process = None

    def capture_output(self):
        while self.process.poll() is None:
            line = self.process.stdout.readline()
            if line.strip():
                self.logs.append(line.strip())

    def send_command(self, command):
        if self.process is not None:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            time.sleep(2)
            new_logs_count = len(self.logs) - self.last_log_index

            new_logs = self.logs[self.last_log_index:]
            self.last_log_index = len(self.logs)

            return new_logs


def start(update, context):
    global server
    import os
    import sys



    if not os.path.isfile("server.jar"):
        update.message.reply_text("Error: server.jar not found")
        return



    if server.process is None:

        server.start()
        update.message.reply_text("Starting server...")
        time.sleep(5)

        with open('./logs/latest.log', 'r') as file:
            contents = file.read()
        update.message.reply_text(contents)
        with open('eula.txt', 'r') as file:
            contents = file.read()
            if 'eula=true' not in contents:
                update.message.reply_text("First run: you should replace \"eula=false\" with \"eula=true\", inside the file 'eula.txt ' and run the bot script again.")
                exit()
            time.sleep(9)
            update.message.reply_text("loading, please wait..")


        for log in server.send_command(""):
            update.message.reply_text(log)
        time.sleep(1)
        update.message.reply_text(
            "Help: Sending commands to the server console is done by simply sending a message to the bot. "
            "Ever console commands such as: weather, time, difficulty work properly. "
            "In addition to this, the console uses *server* commands of the type: ban, kick, say, that not aviable in client. ")
        update.message.reply_text("to send a message to the server chat, use: say \"your message without quotes\".")
        update.message.reply_text("note: console commands should be sent to the bot without using slash(/), this is done to avoid conflicts with bot commands.")
        update.message.reply_text(" Console commands must start with a lowercase letter.")
    else:
        update.message.reply_text("Server is already running")




def stop(update, context):
    global server
    if server.process is not None:
        server.stop()
        update.message.reply_text("Stopping server...")
        time.sleep(2)
        with open('./logs/latest.log', 'r') as file:
            contents = file.read()
        update.message.reply_text(contents)

    else:
        update.message.reply_text("Server is not running")


def send_command(update, context):
    global server
    command = update.message.text
    new_logs = server.send_command(command)
    for log in new_logs:
        update.message.reply_text(log)


def main():
    global server
    server = MinecraftServer()

    telegram_token = input("Enter your telegram bot token: ")

    while not telegram_token:
        print("Token can't be empty!")
        telegram_token = input("Enter your telegram bot token: ")
    from telegram import error

    try:
        updater = Updater(telegram_token, use_context=True)
        print("The bot was successfully launched using the token: ", "\"", telegram_token, "\"", sep="")
    except error.InvalidToken:
        print("Invalid token, please try again.")
        telegram_token = input("Enter your telegram bot token: ")
        updater = Updater(telegram_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("logs", logs))
    dp.add_handler(MessageHandler(Filters.text, send_command))

    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    main()
