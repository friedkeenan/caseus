from .util import flag_url

__all__ = [
    "Room",
]

class Room:
    """A room within the game.

    Parameters
    ----------
    official : :class:`bool`
        Whether the room is official.

        If so, its name is displayed in yellow.
        Otherwise, its name is displayed in teal.
    raw_name : :class:`str`
        The raw name of the room.

        The raw name can take the form of ``"en-roomname"``,
        having the player-supplied room name after the community
        for the room. It may also be of the form ``"*roomname"``,
        resulting in an international room.
    flag_code : :class:`str`
        The flag code for the room, such as ``"gb"`` (Great Britain)
        for the United Kingdom, or ``"int"`` (international) for
        the United Nations.
    """

    FLAG_SIZE = 16

    def __init__(self, *, official, raw_name, flag_code):
        self.official  = official
        self.raw_name  = raw_name
        self.flag_code = flag_code

    @property
    def international(self):
        """Whether the room is international.

        If a room is international, then players from
        any server are able to join it.

        Returns
        -------
        :class:`bool`
            Whether the room is international.
        """

        return self.raw_name[0] == "*"

    @property
    def display_color(self):
        """The color used to display the room name.

        Returns
        -------
        :class:`int`
            The RGB value of the display color.
        """

        if self.official:
            return 0xBABD2F

        return 0x53C9A6

    @property
    def display_name(self):
        r"""The name of the room that will be displayed.

        .. note::

            For tribe house rooms, the display name will look
            something like ``"*\x03Tribe Name"``, the ``*\x03``
            indicating that it is a tribe house. The game will
            still attempt to display the ``\x03`` character,
            despite it showing up as whitespace. Therefore this
            too will provide a :class:`str` containing the ``\x03``
            character.

        Returns
        -------
        :class:`str`
            The room name.
        """

        if self.international:
            return self.raw_name

        names = self.raw_name.split("-", 1)

        if len(names) < 2:
            return names[0]

        return names[1]

    @property
    def community(self):
        """The community code of the room.

        Returns
        -------
        :class:`str` or ``None``
            The community for the room.
        """

        # Logic taken from how the game figures out
        # what flag to display for a user, e.g. in
        # the tribe house screen.

        if len(self.raw_name) == 0 or self.international:
            return "int"

        names = self.raw_name.split("-", 1)
        if len(names) < 2:
            return "int"

        return names[0]

    @property
    def flag_url(self):
        """The URL for the image of the flag that the game will load.

        Returns
        -------
        :class:`str`
            The URL for the image of the flag.
        """

        return flag_url(self.flag_code, self.FLAG_SIZE)
