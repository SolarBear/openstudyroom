from kgs.server.messages import RoomNamesMessage


class Room:
    """
    A KGS room.
    """
    def __init__(self, channel_id):
        self._channel_id = channel_id

        self._name = None
        self._category_id = None
        self._description = None
        self._owners = list()
        self._private = False
        self._tournament_only = False
        self._global_games_only = False

    @property
    def owners(self):
        return self._owners

    def set_info_from_message(self, message):
        """
        Extract room information from a message.
        :param message:  
        """
        if not isinstance(RoomNamesMessage):
            raise TypeError('Only RoomNamesMessage objects can be processed')

        # Try to get the room with the same channel ID
        for message_room in message.rooms:
            if message_room['channelId'] == self._channel_id:
                self._name = message_room['name']

                if 'private' in message_room:
                    self._private = message_room['private']

                if 'tournOnly' in message_room:
                    self._tournament_only = message_room['tournOnly']

                if 'globalGamesOnly' in message_room:
                    self._global_games_only = message_room['globalGamesOnly']

                return self

        # No such room found
        return None
