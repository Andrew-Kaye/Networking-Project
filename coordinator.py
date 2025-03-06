from messages import *
import random
from socket import *

# TODO: copy over messages.py and messages_test.py from milestone 1 into the 
# same folder as your milestone 2 code. If you weren't satisfied with your
# solution, reach out to Vishesh for his solution to milestone 1, which you are
# welcome to use for misletone 2 onward.

# TODO: address all the TODOs in this file (and delete each addressed TODO).

# TODO: test your coordinator implementation by running coordinator_test.py.
# You're welcome to add more tests there, but it's not required.

# This class is fully implemented for you and you should not need to make any
# modifications to it.
# TODO: read the docstring of each method to understand how to use an instance
# of WorkTracker in your coordinator code.
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
        self.server_socket = socket(family=AF_INET, type=SOCK_STREAM)

    def start(self, port: int) -> int:
        """
        Starts the coordinator server on the specified port. If the specified
        port is 0 then picks an unused port. Returns the port that the server
        is listening on.
        """

        # TODO: implement this method following the docstring specification.
        # Use IPv4 network and TCP transport.
        # Hint: in the case of picking an unused port, you can use the
        # getsockname() method on a socket to get the port.

        #instantiate the socet, use the port that the collaer provided or pick an unsused port
        #then return the port that the server is listening on
        #BEFORE YOU CALL socket on accept
        #Predicted start of the code for starting a TCP transport on the server
        #This is a direct copy-paste so it will need considerable editing)
        self.server_socket.bind(('localhost', port))
        self.server_socket.listen(10)
        return self.server_socket.getsockname()[1]

    def accept_connections_until_all_work_done(self):
        """
        Allows Volunteers to repeatedly connect and execute the application
        layer protocol. When there's no work left to do then prints out the
        aggregated result and shuts down the server. This method blocks until
        there's no more work to do.
        """
        bufsize = 4096
        while True:
            response = ""
            if not self.work_tracker.is_all_work_done():
                connection_socket, addr_ = self.server_socket.accept()
                with connection_socket.makefile('rw', buffering=bufsize) as response_file:
                    msg_deserialized = Message.deserialize(response_file)
                    if isinstance(msg_deserialized, GetWorkRequest):
                        path = self.work_tracker.get_path_for_volunteer()
                        response_file.write(GetWorkResponse(self.work_tracker.play_download_host, path).serialize()) #send the response
                        response_file.flush()
                    elif isinstance(msg_deserialized, WorkCompleteRequest):
                        self.work_tracker.process_result(msg_deserialized.path, msg_deserialized.word_counts)
                        response = WorkCompleteResponse().serialize()
                        response_file.write(response) #send the response
                        response_file.flush()
                    else:
                        print("Value Error")
                        raise ValueError
                    print("Trying to write..")
                    #If no Error Thrown, write response, send to socket, close client socket.
                    response_file.write(response)
                    print("Written, Flushing")
                    response_file.flush()
                    print("Closing Socket")
                    print(self.work_tracker.is_all_work_done())
                    connection_socket.close()
            else:
                print("Printing result")
                print(self.work_tracker.get_word_counts_desc())
                connection_socket.close()
                break


if __name__ == '__main__':
    coordinator = Coordinator()
    port = coordinator.start(0)
    coordinator.accept_connections_until_all_work_done()
    