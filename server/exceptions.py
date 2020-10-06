class UserExists(Exception):
    """"Exception to be raised if user already exists"""
    pass


class NotPermitted(Exception):
    """Exception to be raised if user is not permitted"""
    pass


class UserDoesnotExist(Exception):
    """Exception to be raised if user does not exist"""
    pass
