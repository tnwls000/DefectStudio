import enum

class Role(enum.Enum):
    super_admin = "super_admin"
    department_admin = "department_admin"
    department_member = "department_member"

class LogType(enum.Enum):
    use = "use"
    distribute = "distribute"
    issue = "issue"

class UseType(enum.Enum):
    text_to_image = "text_to_image"
    image_to_image = "image_to_image"
    inpaint = "inpaint"
    remove_background = "remove_background"
    clip = "clip"