class Request:
    def __init__(self, bot, message, textPos):
        self.bot = bot
        self.msg = message
        self.author = message.author
        self.text = message.content[textPos:]
