from bwell.forms.validators import password_is_valid


def test_password_is_valid():
    prefix = "aA12345"
    specials = "_~!@#$%^&*()+-=[]{}\\|;:'\";:/?.>,<"
    for special in specials:
        assert password_is_valid(prefix + special)
