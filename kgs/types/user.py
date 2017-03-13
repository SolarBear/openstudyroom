class User:
    """
    A KGS user account.
    """

    FLAGS = (
        'g',
        'c',
        'd',
        's',
        'a',
        'r',
        'TT',
        't',
        'p',
        'P',
        '*',
        '!',
        '=',
        '~',
    )

    AUTH_LEVELS = (
        'normal', # default
        'robot_ranked',
        'teacher',
        'jr_admin',
        'sr_admin',
        'super_admin',
    )

    def __init__(self, name, flags, rank='', auth_level='normal'):
        """
        Constructor.

        :param name: The user name
        :param flags: List of flags (see info file)
        :param rank: Rank of the user, empty means no rank.
        :param auth_level:
        """
        self._name = name
        self._rank = rank
        self._auth_level = auth_level

        # Build flags from string
        self._flags = list()
        self.build_flags(flags)

    def build_flags(self, flags_str):
        for char in flags_str:
            self.add_flag(char)

    def add_flag(self, flag):
        if flag in self.FLAGS:
            self._flags.append(flag)
        else:
            raise ValueError('Invalid flag character ' + flag)

    @property
    def auth_level(self):
        return self._auth_level

    @auth_level.setter
    def auth_level(self, auth_level):
        if auth_level in self.AUTH_LEVELS:
            self._auth_level = auth_level
        else:
            raise ValueError('Invalid auth level ' + auth_level)
