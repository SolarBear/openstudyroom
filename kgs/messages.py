def list_object_properties(obj):
    """
    Utility function that returns a list of properties contained in an object.
    :param obj:
    :return:
    """
    return filter(
        lambda a:
        not a.startswith('__')
        and a not in ['_decl_class_registry', '_sa_instance_state', '_sa_class_manager', 'metadata']
        and not callable(getattr(obj, a)),
        dir(obj))

class Message:
    """
    Data for the message to be send to KGS.
    """

    def __init__(self, command, action):
        """
        Constructor.
        :param command: Message name (eg. LOGIN, CHAT, SET_PASSWORD, etc.)
        :param action: HTTP action (GET or POST)
        """
        self.type = command
        self.action = action


class LoginMessage(Message):
    def __init__(self, name, password, locale='en_US'):
        super().__init__('LOGIN', 'POST')
        self.name = name
        self.password = password
        self.locale = locale


class HelloMessage(Message):
    def __init__(self):
        super().__init__('HELLO', 'GET')
        self.versionMajor = ''
        self.versionMinor = ''
        self.versionBugfix = ''
        self.jsonClientBuild = ''


class LoginSuccessMessage(Message):
    def __init__(self):
        super().__init__('LOGIN_SUCCESS', 'POST')
        self.you = None
        self.friends = list()
        self.subscriptions = list()
        self.roomCategoryChannelIds = list()
        self.rooms = list()


class MessageFormatter:
    """
    Formats a message to send to the web service which acts as a gateway to KGS.
    """

    def __init__(self):
        pass

    def format_message(self, message):
        props = list_object_properties(message)

        # Strip the beginning underscore and set the actual attribute value
        dic = {k: message.__getattribute__(k) for k in props}

        # Remove the action, it's not actually sent as part of the data payload
        # del dic['action']
        return dic


class MessageFactory:
    """
    Takes a KGS JSON message (as a Python dict) and converts it into the proper Message object. Used for GET responses.
    """

    # Mapping of 'type' value in KGS message to their related Message subclass
    TYPE_TO_CLASS = {
        'HELLO': HelloMessage,
        'LOGIN_SUCCESS': LoginSuccessMessage,
    }

    def create_message(self, data):
        """
        Transform a JSON message into the proper Message object.
        :param data:
        :return:
        """
        # Create message object from mapping above
        message = self.TYPE_TO_CLASS[data['type']]()

        # Fill object properties from the data (fields should have the exact same name)
        for prop in list_object_properties(message):
            if prop in data:
                if prop == 'action':
                    setattr(message, prop, 'GET')
                else:
                    setattr(message, prop, data[prop])

        # TODO : handle some special cases (eg. the 'you' field from the LOGIN_SUCCESS message is a User object)

        return message
