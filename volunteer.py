from messages import *
from socket import *
import ssl


# TODO: address all the TODOs in this file (and delete each addressed TODO).

# TODO: test your volunteer.py implementation by running volunteer_test.py.
# You're welcome to add more tests there, but it's not required.

class Volunteer():
    """
    A class that repeatedly asks for work from the Coordinator, performs the
    work, and then reports the results to the Coordinator.
    """

    def __init__(self, coordinator_host: str, coordinator_port: int):
        """
        Constructs a Volunteer who will talk to the specified Coordinator
        server.
        """

        self.coordinator_host = coordinator_host
        self.coordinator_port = coordinator_port

    def connect(self) -> socket:
        """
        Connects to the Coordinator using TCP on IPv4 and returns the connection
        socket.
        """
        
        client_socket = socket(family=AF_INET, type=SOCK_STREAM)
        try:
            client_socket.connect((self.coordinator_host, self.coordinator_port))
        except:
            print("Connection for Volunteer to Coordinator was refused, Closing socket")
            client_socket.close()
            return None
        return client_socket



    def get_work(self) -> GetWorkResponse:
        """
        Connects to the Coordinator, asks for work, and returns the response.
        """
        socket = self.connect()
        try:
            if socket is not None:
                socket.send(GetWorkRequest().serialize().encode())
                bufsize = 5000
                with socket.makefile('r', buffering=bufsize, encoding='utf-8') as response_file:
                    response = Message.deserialize(response_file)
                    socket.close()
                    return response
        except:
            print("Volenteer: Cannot get work, closing socket")
            if socket is not None: socket.close()
            

    def do_work(self, get_work_response: GetWorkResponse) -> dict:
        """
        Performs the work denoted by get_work_response and returns the
        word-counts. This is a simple implementation that counts all words
        that have more than 5 characters. You don't need to modify this and can
        use it as is.
        """
    
        context = ssl.create_default_context()
        download_socket = socket(AF_INET, SOCK_STREAM)
        download_socket = context.wrap_socket(
            download_socket, server_hostname=get_work_response.host)
        
        port = 443
        download_socket.connect((gethostbyname(get_work_response.host), port))
        request = HTTPGetRequest(get_work_response.host, get_work_response.path)
        download_socket.send(request.serialize().encode())

        word_counts = dict()
        with download_socket.makefile('r', encoding='utf-8') as f:
            while True:
                # Read a line from the socket
                line = f.readline()
                if len(line) == 0:
                    break
                words = line.split()
                for word in words:
                    if len(word) > 5:
                        word = word.lower()
                        word_counts[word] = word_counts.get(word, 0) + 1
        download_socket.close()
        sorted_words = dict(sorted(word_counts.items(),
                                   key=lambda item: item[1],
                                   reverse=True)[:20])
        print(sorted_words)
        return sorted_words

    def report_work(self, path: str, result: dict) -> WorkCompleteResponse:
        """
        Connects to the Coordinator and reports the results of a previously
        completed analysis of a play.
        """

        # TODO: implement
        try:
            socket = self.connect()
            if socket is not None:
                socket.send(WorkCompleteRequest(path, result).serialize().encode())
                with socket.makefile('r', encoding='utf-8') as response_file:
                    response = Message.deserialize(response_file)
                print("\nSuccessfully sent over the report\n")
                socket.close()
                return response
            else:
                print("Volunteer report work: Socket was closed")
        except error as e:
            print("Volunteer: Cannot Report work")


    def keep_working_until_done(self):
        """
        Repeatedly asks for work from the Coordinator, performs the work, and
        reports the results. Continues unit the Coordinator responds with no
        work or there's an error talking to the Coordinator.
        """
        while True:
            try:
                get_work_response = self.get_work()
                if get_work_response is None or get_work_response.path is '':
                    print("\nCoordinator signaled no more work. Finishing.\n")
                    break
                else:
                    do_work_response = self.do_work(get_work_response)
                    report_work_response = self.report_work(get_work_response.path, do_work_response)

            except error as e:
                print("Volunteer: Coordinator connection refused, assuming no work to do.")
                break


if __name__ == '__main__':
    volunteer = Volunteer('localhost', 5791)
    volunteer.keep_working_until_done()