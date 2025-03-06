"""
Application layer messages for the Shakespear word-frequency distributed app.
Defines all relevant message types for the application.
For each message type defines its serialization into a human-readable ASCII
format that can be sent over the network.
Also defines the deserialization when receiving each message type from the
network.
"""
from io import *
import ast
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
        if firstline.startswith("GET "):
            return HTTPGetRequest.deserialize(firstline, msg)
        elif firstline.startswith("REQWORK"):
            return GetWorkRequest.deserialize(firstline, msg)
        elif firstline.startswith("ACK_REQWORK"):
            return GetWorkResponse.deserialize(firstline, msg)
        elif firstline.startswith("REQ_WORK_COMP"):
            return WorkCompleteRequest.deserialize(firstline, msg)
        elif firstline.startswith("ACK_WORK_COMP"):
            return WorkCompleteResponse.deserialize(firstline, msg)
        raise ValueError

class HTTPGetRequest(Message):
    """
    Message used by a Volunteer to request the text of a particular play from
    a web-service hosting Shakespeare's plays.
    This is fully defined for you as an example.
    """

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

        if firstline.startswith("GET "):
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

    # TODO: override serialize().
    def serialize(self):
        return "REQWORK\r\n"
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline (or raises a ValueException if the msg is not a valid
        serialized GetWorkRequest).
        """
        # TODO: implement this.
        if firstline.startswith("REQWORK"):
            return GetWorkRequest()
        raise ValueError

class GetWorkResponse(Message):
    """
    Message sent by the Coordinator to a Volunteer in response to the
    Volunteer's GetWorkRequest.
    """

    def __init__(self, host: str, path: str):
        """
        Constructs a response identifying a Shakespeare play (via the path) to
        download from a specified web-service (via the host). If either the path
        or the host is unspecified, then the response indicates that there is
        no work left to do.
        """
        self.host = host
        self.path = path


    # TODO: override serialize().
    def serialize(self) -> str:
        if self.host and self.path:
            result = "ACK_REQWORK\r\n"
            result += f"Host: {self.host}\r\n"
            result += f"Path: {self.path}\r\n"
            result += "\r\n"
        else: # No work available (host or path is unspecified)
            result = f"ACK_REQWORK {"NoWork_noHost" if self.host is None else "NoWork_noPath"}\r\n"
        return result

    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the specified firstline and rest (of message) and returns a
        GetWorkResponse (or raises a ValueException if the msg given by Message class
        is not a valid serialized GetWorkResponse).
        """

        #TODO: redo for the new information that i found out :D
        if firstline.startswith("ACK_REQWORK"):
            if firstline[12:].startswith("NoWork"): # Check for "NoWork" case
                return GetWorkResponse(host="", path="")
            else: # Assume work is available, parse host and path from subsequent lines
                host_line = rest.readline()
                path_line = rest.readline()
                if host_line.startswith("Host: ") and path_line.startswith("Path: "):
                    host = host_line.split(": ", 1)[1].strip()
                    path = path_line.split(": ", 1)[1].strip()
                    return GetWorkResponse(host=host, path=path)
        raise ValueError
    
class WorkCompleteRequest(Message):
    """
    Message sent by a Volunteer to the Coordinator to inform the Coordinator
    about the word-frequency data for a Shakespeare play that was previously
    assigned to the Volunteer in response to a GetWorkRequest.
    """

    def __init__(self, path: str, word_counts: dict):
        """
        Constructs a WorkCompleteRequest reporting the word-frequency result
        (dictionary with word as key and count as value) for the specified
        Shakespeare play (indentified by the path).
        """
        
        self.path = path
        self.word_counts = word_counts

    # TODO: override serialize().
    def serialize(self) -> str:
        result = "REQ_WORK_COMP\r\n"
        result += f"Path: {self.path}\r\n"
        result += f"Word_count: .{self.word_counts}.\r\n"
        return result
    
    def deserialize(firstline: str, rest: TextIOBase) -> Message:
        """
        Parses the firstline and rest (of message) given by the Message class 
        and returns a a WorkCompleteRequest (or raises a ValueException if firstline or rest
        is not a valid serialized WorkCompleteRequest).
        - Will parse Firstline for validation
        - Will parse Path to give a path back into avalid path for self.path of WorkCompleteRequest
        - Will parse Word_Count into a dictonary class for valid self.word_counts of WorkCompleteRequest
        
        """
        
        if firstline.startswith("REQ_WORK_COMP"):
            #Parse Path
            line = rest.readline()    
            [_, path] = line.split()

            #Parse Dictonary
            line = rest.readline()
            [name, valueDict, _] = line.split(".")
            if name.startswith("Word_count"):
                return WorkCompleteRequest(path, ast.literal_eval(valueDict))
        raise ValueError

class WorkCompleteResponse(Message):
    """
    Message sent by the Coordinator to a Volunteer in response to a
    WorkCompleteRequest.
    """

    # TODO: override serialize().
    def serialize(self) -> str:
        return "ACK_WORK_COMP\r\n" 

    def deserialize(firstline:str, rest: TextIOBase) -> Message:
        """
        Parses the specified msg and returns a a WorkCompleteResponse (or
        raises a ValueException if the msg is not a valid serialized
        WorkCompleteResponse).
        """
        # TODO: implement this.
        if firstline.startswith("ACK_WORK_COMP"):
                return WorkCompleteResponse()
        raise ValueError