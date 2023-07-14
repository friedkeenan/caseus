from public import public

from ..packet import ClientboundLegacyPacket

from ... import enums
from ... import game

@public
class AddAnchorsPacket(ClientboundLegacyPacket):
    id = (5, 7)

    def __init__(self, anchors):
        self.anchors = list(anchors)

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(game.Anchor.from_description(description) for description in components)

    def _body_components(self, *, ctx):
        return [anchor.description for anchor in self.anchors]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "anchors",
    )

@public
class PlayerDiedPacket(ClientboundLegacyPacket):
    id = (8, 5)

    def __init__(self, session_id, unk_attr_2, score, type):
        self.session_id = session_id
        self.unk_attr_2 = unk_attr_2 # Per-round death counter?
        self.score      = score
        self.type       = type

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(
            int(components[0]),
            int(components[1]),
            int(components[2]),
            enums.DeathType(int(components[3])),
        )

    def _body_components(self, *, ctx):
        return [
            str(self.session_id),
            str(self.unk_attr_2),
            str(self.score),
            str(self.type.value),
        ]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "session_id",
        "unk_attr_2",
        "score",
        "type",
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

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "session_id",
        "spawn_initial_objects",
    )
