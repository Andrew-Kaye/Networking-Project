from coordinator import *
from messages import *
import random
from socket import *
import threading
import unittest
from volunteer import *

import tracemalloc

tracemalloc.start()

class TestVolunteer(unittest.TestCase):
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

    def test_all_work_completes(self):
        """
        Creates two Volunteers and runs each one in parallel in its own thread
        until all the work is done.
        """
        volunteer1 = Volunteer('localhost', self.port)
        self.volunteer1_thread = threading.Thread(
            target=volunteer1.keep_working_until_done)
        self.volunteer1_thread.start()
        volunteer2 = Volunteer('localhost', self.port)
        self.volunteer2_thread = threading.Thread(
            target=volunteer2.keep_working_until_done)
        self.volunteer2_thread.start()
        self.volunteer1_thread.join()
        self.volunteer2_thread.join()

if __name__ == '__main__':
    unittest.main()    
    print("Complete!")
