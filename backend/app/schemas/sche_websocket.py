from pydantic import BaseModel

class WebsocketRequestModel(BaseModel):
    type: str

# class WebsocketLikeRequestModel(WebsocketRequestModel):
#     post_id: int