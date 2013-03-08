from app.choices import Choices

class MediaStatusChoices(Choices):
    VISIBLE = 1
    REPORTED = 2
    DELETED = 3

class MediaTypeChoices(Choices):
    IMAGE = 1
    VIDEO = 2
    PROFILE_PICTURE = 3
    YOUTUBE_VIDEO = 4