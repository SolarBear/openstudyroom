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
        self._type = command
        self._action = action

    @property
    def action(self):
        return self._action

    @property
    def type(self):
        return self._type


class LoginMessage(Message):
    def __init__(self, name, password, locale='en_US'):
        super().__init__('LOGIN', 'POST')
        self._name = name
        self._password = password
        self._locale = locale


class HelloMessage(Message):
    def __init__(self):
        super().__init__('HELLO', 'GET')


class MessageFormatter:
    """
    Formats a message to send to the web service which acts as a gateway to KGS.
    """

    def __init__(self):
        pass

    def format_message(self, message):
        props = filter(
                lambda a:
                a.startswith('_') and not a.startswith('__')
                and a not in ['_decl_class_registry', '_sa_instance_state', '_sa_class_manager', 'metadata']
                and not callable(getattr(message, a)),
                dir(message))

        # Strip the beginning underscore and set the actual attribute value
        dic = {k[1:]: message.__getattribute__(k) for k in props}

        # Remove the action, it's not actually sent as part of the data payload
        return dic
