from pydantic import BaseModel
from typing import Union, Dict

class MetadataContent(BaseModel):
    num_pages : int
    num_tables : int
    num_pictures : int

class ConvertedContent(BaseModel):
    text : Union[str, Dict]
    metadata : MetadataContent
