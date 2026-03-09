from pydantic import BaseModel, ConfigDict, Field

# This schema code is the requirements for a post to be validated

class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)


# This class requires the code at the top because it'll access it's parameters when creating
class PostCreate(PostBase):
    pass



# This will generate fields by the system and not by the client 
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    date_posted: str




