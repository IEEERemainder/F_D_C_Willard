class IdStorage:
    def __init__(self):
        self.storage={}
        self.guilds={}
        self.channels={}
        self.roles={}
        self.users={}

    def addUser(self, key, id):
        self.users[key] = id

    def addGuild(self, key, id):
        self.guilds[key] = id

    def addChannel(self, key, id):
        self.channels[key] = id

    def addRole(self, key, id):
        self.roles[key] = id

    def user(self, key):
        return self.users[key]

    def guild(self, key):
        return self.guilds[key]

    def channel(self, key):
        return self.channels[key]
        
    def role(self, key):
        return self.roles[key]

ids = IdStorage()
ids.addUser("ego",310752934465896449)
ids.addUser("Крекер",353454053742739456)
ids.addUser("Крабик",535062749256876032)
ids.addRole("КрекерОповещение",922181531873726484)
ids.addRole("ТестированиеРеагированияБотаНаСообщениеСПсевдоупоминанием",963797507580760174)
ids.addGuild("КтоЭтиВашиТипыИчности",790852003106258944)
ids.addChannel("СпамБоты",934894878880587817)
