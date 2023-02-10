from public import public

from ..packet import ClientboundLegacyPacket

@public
class PlayerDiedPacket(ClientboundLegacyPacket):
    id = (8, 5)

    def __init__(self, session_id, unk_attr_2, score, unk_attr_4):
        self.session_id = session_id
        self.unk_attr_2 = unk_attr_2
        self.score      = score
        self.unk_attr_4 = unk_attr_4

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(int(components[0]), int(components[1]), int(components[2]), int(components[3]))

    def _body_components(self, *, ctx):
        return [
            str(self.session_id),
            str(self.unk_attr_2),
            str(self.score),
            str(self.unk_attr_4),
        ]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "session_id",
        "unk_attr_2",
        "score",
        "unk_attr_4",
    )

@public
class SetSynchronizerPacket(ClientboundLegacyPacket):
    id = (8, 21)

    def __init__(self, session_id, spawn_initial_objects):
        self.session_id            = session_id
        self.spawn_initial_objects = spawn_initial_objects

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(int(components[0]), len(components) == 2)

    def _body_components(self, *, ctx):
        if self.spawn_initial_objects:
            return [str(self.session_id), ""]

        return [str(self.session_id)]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs("session_id", "spawn_initial_objects")
