from kgs.data.kgsuser import Friend, KgsUser
from kgs.data.room import Room


def _list_object_properties(obj):
    """
    Utility function that returns a list of properties contained in an object.
    :param obj:
    :return:
    """
    return filter(
        lambda a:
        not a.startswith('_')
        and a not in ['_decl_class_registry', '_sa_instance_state', '_sa_class_manager', 'metadata']
        and not callable(getattr(obj, a)),
        dir(obj))

# List of supported message types
SUPPORTED_TYPES = (
    'LOGIN',
    'HELLO',
    'JOIN_REQUEST',
    'ROOM_DESC',
    'ROOM_JOIN',
)


class Message:
    """
    Abstract data class for the message to be send to KGS, please subclass.
    """

    def __init__(self, type, action):
        """
        Constructor.
        :param type: Message name (eg. LOGIN, CHAT, SET_PASSWORD, etc.)
        :param action: HTTP action (GET or POST)
        """
        self.type = type
        self.action = action

    def post_load(self):
        """
        To be called when the data from the server was received. Should be used to transform JSON dictionary into useful
        objects.
        :return:
        """
        raise NotImplementedError("Please implement the post_load method")


class PostMessage(Message):
    """
    Message sent as a POST request.
    """

    def __init__(self, type):
        super().__init__(type, 'POST')

    def post_load(self):
        """
        No post-load action to perform since we're posting our own data.
        """
        pass


class ChannelMessage:
    """
    Channel message (ie. one that requires a channelId field) POST request.
    """

    def __init__(self, channel_id):
        self._channel_id = channel_id


class GetMessage(Message):
    """
    Message sent as a GET request.
    """

    def __init__(self, type):
        super().__init__(type, 'GET')

    def post_load(self):
        """
        To be called when the data from the server was received. Should be used to transform JSON dictionary into useful
        objects.
        :return:
        """
        super().post_load()


class JoinRequestMessage(ChannelMessage, PostMessage):
    """
    Message sent to request to join a channel. Answered by the ROOM_JOIN message (see JoinMessage).
    """

    def __init__(self, channel_id):
        super(ChannelMessage).__init__(channel_id=channel_id)
        super(PostMessage).__init__('JOIN_REQUEST')


class JoinMessage(GetMessage):
    """
    Message received when you join a room - including right after login.
    """
    def __init__(self):
        super(GetMessage).__init__('ROOM_JOIN')


class LoginMessage(PostMessage):
    """
    Request for login.
    """
    def __init__(self, name, password, locale='en_US'):
        super().__init__('LOGIN')
        self.name = name
        self.password = password
        self.locale = locale


class HelloMessage(GetMessage):
    """
    Very first message the server sends when try connecting.
    """
    def __init__(self):
        super().__init__('HELLO')
        self.versionMajor = ''
        self.versionMinor = ''
        self.versionBugfix = ''
        self.jsonClientBuild = ''


class LoginSuccessMessage(GetMessage):
    """
    Login confirmation. We may now receive further messages. This message's payload contains much of the server's state:
    rooms, users, room categories, etc.
    """
    def __init__(self):
        super().__init__('LOGIN_SUCCESS')
        self.you = None
        self.friends = list()
        # self.subscriptions = list() TODO
        self.room_category_channel_id = list()
        self.rooms = list()

    def post_load(self):
        """
        Called when the object has been built with raw data. 
        """
        self._load_you()
        self._load_friends()
        self._load_room_categories()
        self._load_rooms()

    # TODO : consider whether these methods would be best left out of the message object itself or if they're relevant
    def _load_you(self):
        """
        Convert "you" raw data into a User object
        """

        # Optional. Regular users don't seem to have the authLevel field
        if 'auth_level' in self.you:
            auth_level = self.you['authLevel']
        else:
            auth_level = KgsUser.DEFAULT_AUTH_LEVEL

        self.you = KgsUser(self.you['name'], self.you['flags'], self.you['rank'], auth_level)

    def _load_friends(self):
        """
        Load the user's friend list. Friends are useful for a bot since it makes it easy to track league members, for
        instance.
        """
        friends = self.friends
        self.friends = list()

        # Friends field is optional
        if friends is None:
            return

        for friend in friends:
            self.friends.append(Friend(friend['friend_type'], friend['name'], friend['rank'],
                                       friend['flags'], friend['authLevel']))

    def _load_room_categories(self):
        """
        From the docs : An object that maps room categories to the channel that has the master room list for that
        category.
        """
        room_cats = self.room_category_channel_id
        self.room_category_channel_id = dict()

        for room_cat in room_cats:
            self.room_category_channel_id[room_cat['category']] = room_cat['channelId']

    def _load_rooms(self):
        """
        A list of all rooms on the server, from a pair of channel ID and category.
        """
        rooms = self.rooms
        self.rooms = dict()

        for room in rooms:
            channel_id = room['channelId']
            self.rooms[channel_id] = Room(channel_id)


class LoginFailedBadPasswordMessage(GetMessage):
    def __init__(self):
        super().__init__('LOGIN_FAILED_BAD_PASSWORD')


class LogoutPostMessage(PostMessage):
    """
    LOGOUT message. Could be a POST or GET one
    """
    def __init__(self):
        super().__init__('LOGOUT')

    def post_load(self):
        pass


class RoomDescriptionMessage(GetMessage, ChannelMessage):
    """
    Get a room's description and its owners, optionally.
    """
    def __int__(self, channel_id):
        super(GetMessage).__init__('ROOM_DESC')
        super(ChannelMessage).__init__(channel_id)

    def post_load(self):
        pass


class RoomNamesMessage(GetMessage):
    """
    Message that contains the description of a set of rooms.
    """
    def __init__(self, type):
        super(GetMessage).__init__(type)

    def post_load(self):
        pass


class WakeUpMessage(PostMessage):
    """
    Message that simply resets your idle clock, just to keep the connection alive.
    """
    def __init__(self):
        super(PostMessage).__init__('WAKE_UP')


class MessageFormatter:
    """
    Formats a message to send to the web service which acts as a gateway to KGS.
    """

    @staticmethod
    def format_message(message):
        # TODO : ensure ChannelMessage objects get sent with their channel ID
        props = _list_object_properties(message)
        obj = {k: message.__getattribute__(k) for k in props}
        del obj['action']

        return obj


class MessageFactory:
    """
    Takes a KGS JSON message (as a Python dict) and converts it into the proper Message object. Used for GET responses.
    """

    # Mapping of 'type' value in KGS message to their related Message subclass
    TYPE_TO_CLASS = {
        'HELLO': HelloMessage,
        'JOIN_REQUEST': JoinRequestMessage,
        'LOGIN_SUCCESS': LoginSuccessMessage,
        'ROOM_DESC': RoomDescriptionMessage,
        'ROOM_NAMES': RoomNamesMessage,
        'WAKE_UP': WakeUpMessage,
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
        for prop in _list_object_properties(message):
            if prop in data:  # If the property does not exist in the object, it's because we don't care
                if prop == 'action':
                    setattr(message, prop, 'GET')
                else:
                    setattr(message, prop, data[prop])

        # Handle some special cases (eg. the 'you' field from the LOGIN_SUCCESS message is a User object)
        message.post_load()

        return message
