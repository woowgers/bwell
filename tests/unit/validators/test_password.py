import pytest

from bwell.forms.validators import password_is_valid


class TestPasswordValidity:
    @pytest.mark.parametrize(
        'password',
        [
            'abCD1@',
        ],
    )
    def test(self, password):
        assert password_is_valid(password)


    @pytest.mark.parametrize(
        'password',
        [
            '',
            'abCD!@',
            'abCD01',
            'ab01!@',
            'AB01!@',
        ],
    )
    def test_invalid(self, password):
        assert not password_is_valid(password)
