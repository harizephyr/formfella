from pydantic import BaseModel
class SignUpRequest(BaseModel):
    username: str
    password: str
    name: str = None

class AuthenticateUserRequest(BaseModel):
    username: str
    password: str


class ConfirmSignUpRequest(BaseModel):
    username: str
    confirmation_code: str