"""Tests for messages.py."""

from io import *
from messages import *
import unittest

class TestMessage(unittest.TestCase):

    def test_invalid_deserialize(self):
        try:
           deserialized = Message.deserialize(StringIO("bogus msg"))
           self.fail("Expected ValueError") 
        except(ValueError):
            pass

class TestHTTPGetRequest(unittest.TestCase):

    def test_serialize_deserialize(self):
        """
        Tests that a message object is serialized and deserialized as expected,
        and that serialize followed by deserialize (round-tripping) returns an
        equal object.
        """

        request = HTTPGetRequest("some-host", "some-path")

        serialized = request.serialize()
        expected_serialized = "GET some-path HTTP/1.1\r\n"
        expected_serialized += "Host: some-host\r\n"
        expected_serialized += "\r\n"
        self.assertEqual(serialized, expected_serialized)

        deserialized = Message.deserialize(StringIO(serialized))
        self.assertIsInstance(deserialized, HTTPGetRequest)
        self.assertEqual(deserialized.host, "some-host")
        self.assertEqual(deserialized.path, "some-path")

class TestGetWorkRequest(unittest.TestCase):

    def test_serialize_deserialize(self):
        request = GetWorkRequest()

        serialized = request.serialize()
        expected_serialized = "REQWORK\r\n"
        self.assertEqual(serialized, expected_serialized)

        deserialized = Message.deserialize(StringIO(serialized))
        self.assertIsInstance(deserialized, GetWorkRequest)

class TestGetWorkResponse(unittest.TestCase):

    def test_serialize_deserialize(self):
        expected_serialized_sucsess = "ACK_REQWORK\r\nHost: some-host\r\nPath: some-path\r\n\r\n"
        expected_serialized_NoWork1 = "ACK_REQWORK NoWork_noHost\r\n"
        expected_serialized_NoWork2 = "ACK_REQWORK NoWork_noPath\r\n"

        #Sucsess
        serialized = GetWorkResponse("some-host", "some-path").serialize()
        self.assertEqual(serialized, expected_serialized_sucsess)
        self.assertIsInstance(Message.deserialize(StringIO(serialized)), GetWorkResponse)

        #NoWork, (noPath)
        serialized = GetWorkResponse("some-host", None).serialize()
        self.assertEqual(serialized, expected_serialized_NoWork2)
        self.assertIsInstance(Message.deserialize(StringIO(serialized)), GetWorkResponse)

        #NoWork, (NoHost)
        serialized = GetWorkResponse(None, "some-path").serialize()
        self.assertEqual(serialized, expected_serialized_NoWork1)
        self.assertIsInstance(Message.deserialize(StringIO(serialized)), GetWorkResponse)
        deserialized = Message.deserialize(StringIO(serialized))
        self.assertIsInstance(deserialized, GetWorkResponse)

        #NoWork, nothing given at all
        serialized = GetWorkResponse(None, None).serialize()
        self.assertEqual(serialized, expected_serialized_NoWork1)
        self.assertIsInstance(Message.deserialize(StringIO(serialized)), GetWorkResponse)
        deserialized = Message.deserialize(StringIO(serialized))
        self.assertIsInstance(deserialized, GetWorkResponse)

class TestWorkCompleteRequest(unittest.TestCase):

    def test_serialize_deserialize(self):
        request = WorkCompleteRequest("path-to-play",
                                      {"romeo": 16, "juliet": 18, "rose": 7})

        serialized = request.serialize()
        
        # TODO: validate
        expected_serialized = "REQ_WORK_COMP\r\nPath: path-to-play\r\nWord_count: .{'romeo': 16, 'juliet': 18, 'rose': 7}.\r\n"
        self.assertEqual(serialized, expected_serialized)

        deserialized = Message.deserialize(StringIO(serialized))
        # TODO: validate
        self.assertEqual(deserialized.path, "path-to-play")
        self.assertEqual(deserialized.word_counts, {'romeo': 16, 'juliet': 18, 'rose': 7})


class TestWorkCompleteResponse(unittest.TestCase):

    def test_serialize_deserialize(self):
        request = WorkCompleteResponse()

        serialized = request.serialize()
        # TODO: validate
        expected_serialized = "ACK_WORK_COMP\r\n"
        self.assertEqual(serialized, expected_serialized)

        deserialized = Message.deserialize(StringIO(serialized))
        # TODO: validate
        self.assertIsInstance(deserialized, WorkCompleteResponse)

    def test_invalid_deserialize(self):
        try:
           deserialized = Message.deserialize(StringIO("bogus msg"))
           self.fail("Expected ValueError") 
        except(ValueError):
            pass

if __name__ == '__main__':
    unittest.main()