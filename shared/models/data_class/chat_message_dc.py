from dataclasses import dataclass


@dataclass
class ChatMessageDC(object):
    sender: str = None
    message: str = None
