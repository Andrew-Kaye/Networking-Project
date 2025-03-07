"""
Application layer messages for the Shakespear word-frequency distributed app.
Defines all relevant message types for the application.
For each message type defines its serialization into a human-readable ASCII
format that can be sent over the network.
Also defines the deserialization when receiving each message type from the
network.
"""

from io import *

class Message():
    """
    Base class for every app message type.
    """

    def serialize(self) -> str:
        """
        Returns a string corresponding to the human-readable ASCII message that
        can be sent over the network.
        The default base implementation intentionally raises an exception to
        ensure that each concrete message type implements this method.
        """

        raise NotImplementedError

    def deserialize(msg: TextIOBase):
        """
        Parses the specified msg and returns its deserialized Message object (or
        raises a ValueException if the msg is not a valid serialization).
        """

        firstline = msg.readline()
        if firstline.startswith(HTTPGetRequest.firstline_prefix):
            return HTTPGetRequest.deserialize(firstline, msg)
        elif firstline.startswith(GetWorkRequest.firstline_prefix):
            return GetWorkRequest.deserialize(firstline, msg)
        elif firstline.startswith(GetWorkResponse.firstline_prefix):
            return GetWorkResponse.deserialize(firstline, msg)
        elif firstline.startswith(WorkCompleteRequest.firstline_prefix):
            return WorkCompleteRequest.deserialize(firstline, msg)
        elif firstline.startswith(WorkCompleteResponse.firstline_prefix):
            return WorkCompleteResponse.deserialize(firstline, msg)
        raise ValueError

class HTTPGetRequest(Message):
    """
    Message used by a Volunteer to request the text of a particular play from
    a web-service hosting Shakespeare's plays.
    This is fully defined for you as an example.
    """

    firstline_prefix = "GET "

    def __init__(self, host: str, path: str):
        """
        Creates an HTTPGetRequest for the specified host and path.
        """

        super().__init__()
        self.host = host
        self.path = path

    # Overrides super().serialize()
    def serialize(self) -> str:
        result = "GET %s HTTP/1.1\r\n" % (self.path)
        result += "Host: %s\r\n" % (self.host)
        result += "\r\n"
        return result 
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns an
        HTTPGetRequest (or raises a ValueException if the msg is not a valid
        serialized HTTPGetRequest).
        This is a class method i.e. associated with the class rather than
        instances of the class. 
        """

        if firstline.startswith(HTTPGetRequest.firstline_prefix):
            [_, path, _] = firstline.split()
            line = rest.readline()
            [name, value] = line.split()
            if name == "Host:":
                return HTTPGetRequest(value, path)
        raise ValueError

class GetWorkRequest(Message):
    """
    Message sent by a Volunteer to the Coordinator to ask for work.
    """
    
    firstline_prefix = "REQWORK"

    # Overrides super().serialize()
    def serialize(self) -> str:
        return GetWorkRequest.firstline_prefix + "\n"
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns a
        GetWorkRequest (or raises a ValueException if the msg is not a valid
        serialized GetWorkRequest).
        """

        if firstline.startswith(GetWorkRequest.firstline_prefix):
            return GetWorkRequest()
        raise ValueError

class GetWorkResponse(Message):
    """
    Message sent by the Coordinator to a Volunteer in response to the
    Volunteer's GetWorkRequest.
    """

    firstline_prefix = "ACK_REQWORK "

    def __init__(self, host: str, path: str):
        """
        Constructs a response identifying a Shakespeare play (via the path) to
        download from a specified web-service (via the host). If either the path
        or the host is unspecified, then the response indicates that there is
        no work left to do.
        """
        self.host = host
        self.path = path


    def serialize(self):
        result = GetWorkResponse.firstline_prefix
        if len(self.host) > 0 and len(self.path) > 0:
            result += "Download and analyze the following.\n"
            result += "Host: %s\n" % (self.host)
            result += "Path: %s\n" % (self.path)
        else:
            result += "There's no work left.\n"
        return result
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns a
        GetWorkResponse (or raises a ValueException if the msg is not a valid
        serialized GetWorkResponse).
        """

        if firstline.startswith(GetWorkResponse.firstline_prefix):
            host = ""
            path = ""
            if firstline.find("There's no work left") > 0:
                return GetWorkResponse(host, path)
            line = rest.readline()
            while len(line) > 0:
                [key, value] = line.split()
                if key == "Host:":
                    host = value
                elif key == "Path:":
                    path = value
                if len(host) > 0 and len(path) > 0:
                    return GetWorkResponse(host, path)
                line = rest.readline()
        raise ValueError
    
class WorkCompleteRequest(Message):
    """
    Message sent by a Volunteer to the Coordinator to inform the Coordinator
    about the word-frequency data for a Shakespeare play that was previously
    assigned to the Volunteer in response to a GetWorkRequest.
    """

    firstline_prefix = "REQ_WORK_COMP "

    def __init__(self, path: str, word_counts: dict):
        """
        Constructs a WorkCompleteRequest reporting the word-frequency result
        (dictionary with word as key and count as value) for the specified
        Shakespeare play (indentified by the path).
        """
        
        self.path = path
        self.word_counts = word_counts

    # override super().serialize()
    def serialize(self):
        result = WorkCompleteRequest.firstline_prefix + self.path + "\n"
        for [word, count] in self.word_counts.items():
            result += "%s %d\n" % (word, count)
        result += "\n"
        return result
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns a
        WorkCompleteRequest (or raises a ValueException if the msg is not a
        valid serialized WorkCompleteRequest).
        """

        if firstline.startswith(WorkCompleteRequest.firstline_prefix):
            [_, path] = firstline.split()
            word_counts = dict()
            line = rest.readline()
            while line != "\n":
                [word, count] = line.split()
                word_counts[word] = int(count)
                line = rest.readline()
            return WorkCompleteRequest(path, word_counts)
        raise ValueError
    
class WorkCompleteResponse(Message):
    """
    Message sent by the Coordinator to a Volunteer in response to a
    WorkCompleteRequest.
    """

    firstline_prefix = "ACK_WORK_COMP"

    # Overrides super().serialize().
    def serialize(self):
        return WorkCompleteResponse.firstline_prefix + "\n"
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns a
        WorkCompleteResponse (or raises a ValueException if the msg is not a
        valid serialized WorkCompleteResponse).
        """
        
        if firstline.startswith(WorkCompleteResponse.firstline_prefix):
            return WorkCompleteResponse()
        raise ValueError