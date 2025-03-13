from messages import *
import random
from socket import *

class WorkTracker():
    """
    A class that tracks the status of plays to download and analyze. This is
    used by the Coordinator server to assign work to Volunteers and to
    assimilate results from Volunteers.
    """
    
    def __init__(self):
        """
        Constructs a WorkTracker to analyze specific Shakespeare's plays.
        """

        self.play_download_host = "www.gutenberg.org"
        self.play_ids = []
        self.play_ids.append(1513)  # Romeo and Juliet
        self.play_ids.append(27761) # Hamlet
        self.play_ids.append(23042) # Tempest
        self.play_ids.append(1533)  # Macbeth
        self.play_ids.append(1531)  # Othello
        self.play_ids.append(1522)  # Julius Caesar
        self.play_ids.append(1526)  # Twelfth Night
        self.play_ids.append(1515)  # Merchant of Venice

        # A dictionary that maintains the aggregate word frequecies across the
        # plays analyzed by Volunteers.
        # key: word, value: count.
        self.word_counts = dict()

        # Paths of plays that have not been assigned to any Volunteers yet.
        self.unstarted_paths = set()
        for i in self.play_ids:
            self.unstarted_paths.add("/cache/epub/%s/pg%s.txt" % (i, i))
        
        # Paths of plays that have been assigned to Volunteers but they haven't
        # yet reported results for them yet.
        self.started_paths = set()

        # Paths of plays that have been analyzed by Volunteers and the reported
        # results have been assimilated by the Coordinator.
        self.finished_paths = set()
    
    def get_path_for_volunteer(self) -> str:
        """
        Returns the path to a play that a Volunteer looking for work should
        download from the webservice, analyze, and report results. If there is
        no work left, returns an empty path.
        """
        
        if len(self.unstarted_paths) > 0:
            # There are unstarted plays, so hand one of them out.
            path = random.choice(list(self.unstarted_paths))
            self.unstarted_paths.remove(path)
            self.started_paths.add(path)
        elif len(self.started_paths) > 0:
            print("There are no unstarted paths.")
            print("So handing out an already started (but not finished) path.")
            print ("Just in case the other volunteer flakes.")
            path = random.choice(list(self.started_paths))
        else:
            # There's no work left.
            path = ""
        return path
    
    def process_result(self, path, word_counts: dict):
        """
        Processes the word-counts report from a Volunteer for the specified
        path's play by aggregating them into the overall word-counts across all
        analyzed plays.
        """

        if path in self.finished_paths:
            # This path has already been processed, so ignore it. Otherwise it
            # would be processed multiple times and skew the results.
            return
        for [word, count] in word_counts.items():
            self.word_counts[word] = self.word_counts.get(word, 0) + int(count)
        self.started_paths.remove(path)
        self.finished_paths.add(path)

    def is_all_work_done(self) -> bool:
        """
        Return whether all the work is done.
        """

        return len(self.finished_paths) == len(self.play_ids)

    def get_word_counts_desc(self):
        """
        Returns the aggregate word-counts in descending order by count.
        """
        
        return dict(sorted(self.word_counts.items(), 
                           key=lambda item: item[1], reverse=True))

class Coordinator():
    """
    A class that starts a Coordinator server, handles requests from Volunteers,
    and aggregates results reported by Volunteers.
    """

    def __init__(self):
        """
        Constructs a Coordinator that will manage the word-counts analysis of
        a set of Shakespeare's plays, relying on Volunteers to ask for and do
        work on each play.
        """
        
        self.work_tracker = WorkTracker()

    def start(self, port: int) -> int:
        """
        Starts the coordinator server on the specified port. If the specified
        port is 0 then picks an unused port. Returns the port that the server
        is listening on.
        """

        # Use IPv4 network and TCP transport.
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('localhost', port))
        backlog = 10
        self.server_socket.listen(backlog)
        port = self.server_socket.getsockname()[1]
        print("Listening on localhost:%d" % port)
        return port

    def accept_connections_until_all_work_done(self):
        """
        Allows Volunteers to repeatedly connect and execute the application
        layer protocol. When there's no work left to do then shuts down the
        server.
        """

        while True:
            # Accept a new connection from a Volunteer.
            connection_socket, client_address = self.server_socket.accept()
            print("Connection from: ", client_address)

            shutdown = False
            with connection_socket.makefile('rw') as connection_file:
                shutdown = self.handle_request(connection_file)
            connection_socket.close()

            if shutdown:
                print("All work is done. Here are the results.")
                results = self.work_tracker.get_word_counts_desc()
                for [word, count] in results.items():
                    print("%s: %d" % (word, count))
                break
        self.server_socket.close()
    
    def handle_request(self, connection_file: TextIOBase) -> bool:
        """
        Handles a request from a Volunteer. Returns whether to shut down the
        Coordinator.
        """

        shutdown = False
        try:
            request = Message.deserialize(connection_file)
        except ValueError:
            print("Received an invalid request.")
            return shutdown
        if isinstance(request, GetWorkRequest):
            print("Received a GetWorkRequest.")
            path = self.work_tracker.get_path_for_volunteer()
            shutdown = (path == "")
            print(shutdown)
            response = GetWorkResponse(
                self.work_tracker.play_download_host, path).serialize()
            connection_file.write(response)
        elif isinstance(request, WorkCompleteRequest):
            print("Received a WorkCompleteRequest.")
            self.work_tracker.process_result(request.path, request.word_counts)
            response = WorkCompleteResponse().serialize()
            print("Updated word counts.")
            connection_file.write(response)
        else:
            print("Received an unexpected request. Ignoring it.")
            response = ""
        print(request.serialize())
        print(response)
        return shutdown

if __name__ == '__main__':
    coordinator = Coordinator()
    port = coordinator.start(0)
    coordinator.accept_connections_until_all_work_done()
    