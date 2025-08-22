from dataclasses import dataclass
from typing import Optional, Literal

ClipboardType = Literal['text', 'link', 'image', 'file']

@dataclass
class ClipItem:
    id: int
    type: ClipboardType
    content: str
    path: Optional[str]
    ts: str
    favorite: bool
    hash: str
