from kgs.server.messages import *

class KgsServer:
    """
    A class representing the KGS server's state.
    """

    # Maps message classes to the function that handles it
    MESSAGE_HANDLERS = {
        RoomNamesMessage: 'handle_room_desc_message',
    }

    def __init__(self, connection):
        self._connection = connection
        self._rooms = dict()
        self._rooms_per_category = dict()
        self._users = dict() # Users, indexed by name

    def process_message(self, message):
        """
        Dispatches messages to their related handler method.
        :param message: Message object to process
        :return: The handler method's return value
        """

        message_type = type(message)
        if message_type in self.MESSAGE_HANDLERS:
            handler_method = getattr(self, self.MESSAGE_HANDLERS[message_type])
            return handler_method(message)

    def handle_room_desc_message(self, message):
        """
        Handle ROOM_DESC message.
        :param message: 
        :return: 
        """
        if message.channel_id not in self._rooms.keys():
            raise IndexError('No room with ID ' + message.channel_id)

        room = self._rooms[message.channel_id]
        room._description = message.description

        if message.owners:
            for owner in message.owners:
                name = owner['name']
                if name in self._users.keys():
                    owner = self._users[name]
                else:
                    auth_level = owner['authLevel'] if 'authLevel' in owner.keys() else 'normal'
                    owner = KgsUser(name, owner['flags'], auth_level)

                    # An owner is user, add it to the users list
                    self._users[name] = owner

                room.owners.append(owner)
