import requests

from messages import *


class KgsConnection:
    """
    Creates a connection to KGS.
    """

    def __init__(self, url):
        self._url = url
        self._formatter = MessageFormatter()

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

        if login_response.ok:
            print("Connection success!")
        else:
            print("Connection failed :(")
            print(login_response)

        hello_received = False

        while not hello_received:
            response = requests.get(self._url)

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

# Running as standalone to test stuff, remove this ASAP
if __name__ == '__main__':
    connection = KgsConnection('http://localhost:8080/jsonClient/access')
