from app.choices import Choices
    
class UserStatusChoices(Choices):
    NEW = 0
    ACTIVE = 1
    INACTIVE = 2
    REPORTED = 3
    DELETED = 4