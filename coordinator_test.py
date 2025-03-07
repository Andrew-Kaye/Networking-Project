from coordinator import *
from messages import *
from socket import *
import threading
import unittest

class TestCoordinator(unittest.TestCase):
    """
    This test case starts a Coordinator server in another thread and runs tests
    against it.
    """

    def setUp(self):
        """
        Starts the Coordinator server on another thread.
        """
        
        coordinator = Coordinator()
        self.port = coordinator.start(0)
        print("port: %d" % self.port)
        self.coordinator_thread = threading.Thread(
            target=coordinator.accept_connections_until_all_work_done)
        self.coordinator_thread.start()
        print("Coordinator server thread started")
        
    def tearDown(self):
        self.coordinator_thread.join()

    def send_request(self, request) -> Message:
        """
        Connects to the Coordinator server and sends the specified request to
        it. Returns the response from the server.
        """
        
        connection_socket = socket(AF_INET, SOCK_STREAM)
        connection_socket.connect(('localhost', self.port))
        connection_socket.send(request.serialize().encode())
        with connection_socket.makefile('r') as response_file:
            response = Message.deserialize(response_file)
        connection_socket.close()
        return response

    def test_all_work_completes(self):
        """
        Repeatedly sends a GetWorkRequest and then a WorkCompleteRequest to the
        Coordinator server. Continues until there is no work left.
        """

        all_work_complete = False
        started_paths = set()
        finished_paths = set()
        while True:
            get_work_request = GetWorkRequest()
            get_work_response = self.send_request(get_work_request)
            self.assertIsInstance(get_work_response, GetWorkResponse)
            if get_work_response.path == "":
                all_work_complete = True
                break
            self.assertEqual(get_work_response.host, "www.gutenberg.org")
            self.assertFalse(get_work_response.path in finished_paths)
            started_paths.add(get_work_response.path)
            if len(started_paths) > 0:
                path = next(iter(started_paths))
                word_counts = {'hello': 10, 'world': 20}
                work_complete_request = WorkCompleteRequest(path, word_counts)
                work_complete_response = self.send_request(
                    work_complete_request)
                self.assertIsInstance(work_complete_response, 
                                      WorkCompleteResponse)
                started_paths.remove(path)
                finished_paths.add(path)
        self.assertTrue(all_work_complete)

if __name__ == '__main__':
    unittest.main(verbosity=2)    
