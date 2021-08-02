from .MyMQTTllistener import MyMQTTlistener


class DatabbaseSaveListener(MyMQTTlistener):
    def __init__(self,dbproxy,msg_recipes: list, name: str, broker, topic: str, username: str = None, pwd: str = None, dataholders: dict = None):
        MyMQTTlistener.__init__(self, msg_recipes, name, broker, topic, username, pwd, dataholders)

        self.db = dbproxy

    def on_msg_hook(self, client, userdata, msg_type, data):
        dbproxy.save()

