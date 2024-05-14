from typing import Any

from shared.globals.enums import ChatbotTemperaments


class ChatbotTemperamentDC(object):
    def __init__(self,
                 temperament: ChatbotTemperaments | str = None,
                 temperature: float = None,
                 top_k: int = None,
                 top_p: float = None):
        if temperament is None:
            temperament = ChatbotTemperaments.FUN
        if temperature is None:
            temperature = 0.6
        if top_k is None:
            top_k = 40
        if top_p is None:
            top_p = 0.95

        self.temperament = temperament if isinstance(temperament, str) else temperament.name
        self.temperature = temperature if isinstance(temperament, str) else 0.2 + (float(temperament.value) * 0.2)
        self.top_k: int = top_k
        self.top_p: float = top_p

    def get_vertex_chat_fields(self) -> dict[str, Any]:
        return {
            'temperature': self.temperature,
            'top_k': self.top_k,
            'top_p': self.top_p
        }

    def get_temperament_fields(self) -> dict[str, Any]:
        return {
            'temperament': self.temperament,
            'temperature': self.temperature,
            'top_k': self.top_k,
            'top_p': self.top_p
        }
