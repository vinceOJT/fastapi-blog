from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, EmailStr 


# Creating a user with required information
class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


# Create user
class UserCreate(UserBase):
    pass

# Response when create user
class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id:int
    image_file: str | None
    image_pat: str 







# This schema code is the requirements for a post to be validated
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


# This class requires the code at the top because it'll access it's parameters when creating
class PostCreate(PostBase):
    user_id: id # TEMP TESTING



# This will generate fields by the system and not by the client 
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id:int
    user_id: int
    date_posted: datetime
    author: UserResponse




