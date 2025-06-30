from pydantic import BaseModel

class Plan(BaseModel):
    plan_id: str
    name: str
    description: str
    image_key: str