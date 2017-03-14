import json
import requests

from messages import *


class KgsConnection:
    """
    Creates a connection to KGS.
    """

    def __init__(self, url):
        self._url = url
        self._formatter = MessageFormatter()
        self._message_factory = MessageFactory()
        self._cookies = None

        self.init_sequence()

    def init_sequence(self):
        """
        Perform the initialization sequence with the servlet.

        Basically, we perform the following operations:

        * Send LOGIN message for logging in
        * Immediately receive response to confirm data is OK

        :return:
        """

        login_response = self.send_message(LoginMessage('username', 'password'))

        self._cookies = login_response.cookies  # NOM NOM NOM
        hello_received = False

        while not hello_received:
            response = requests.get(self._url, cookies=self._cookies)
            kgs_response = KgsResponse(self._message_factory, bytes.decode(response.content))

            # TODO : process the messages contained in the KgsResponse

            if response.ok:
                hello_received = True

        print("Handshake succeeded")

    def send_message(self, message):
        formatted_message = self._formatter.format_message(message)

        if message.action == 'POST':
            headers = {"content-type": "application/json;charset=UTF-8"}
            response = requests.post(self._url, json=formatted_message, headers=headers)
        elif message.action == 'GET':
            response = requests.get(self._url, formatted_message)
        else:
            raise ValueError("Invalid action for message")

        return response


class KgsResponse:
    """
    A response from the server (or rather, the servlet). It is simply a JSON object containing an array of messages that
    will need to be parsed and made into proper Message objects.
    """

    def __init__(self, message_factory, data):
        self._messages = list()
        self._message_factory = message_factory

        self.parse_messages(data)

    @property
    def messages(self):
        return self._messages

    def parse_messages(self, data):
        for message_dict in json.loads(data)['messages']:
            self._messages.append(self.create_message(message_dict))

    def create_message(self, message_dict):
        return self._message_factory.create_message(message_dict)


# Running as standalone to test stuff, remove this ASAP
if __name__ == '__main__':
    connection = KgsConnection('http://localhost:8080/jsonClient/access')
