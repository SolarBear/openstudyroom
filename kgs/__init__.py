from kgs.server.connection import KgsConnection
from kgs.types.server import KgsServer
import kgs.types.kgsuser

# TODO : Running as standalone to test stuff, remove this ASAP
if __name__ == '__main__':
    # TODO : create setting for actual URL
    # bot = kgs.types.kgsuser.KgsUser()

    connection = KgsConnection('http://www.gokgs.com/json/', 'SolarBear', 'gros0Sale1!kg')
    server = KgsServer(connection)

    # Add some message callbacks
    connection.add_message_callback()

    # Add some commands
    # connection.queue_message(RoomJoinMessage())

    while connection.loop():
        pass

    connection.close()  # kthxbye
