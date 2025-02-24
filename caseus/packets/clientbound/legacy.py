from public import public

from ..packet import ClientboundLegacyPacket

from ... import enums
from ... import game

@public
class RemoveExplodedObjectPacket(ClientboundLegacyPacket):
    id = (4, 6)

    def __init__(self, object_id):
        self.object_id = object_id

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(int(components[0]))

    def _body_components(self, *, ctx):
        return [str(self.object_id)]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs("object_id")

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
class SyncExplosionPacket(ClientboundLegacyPacket):
    id = (5, 17)

    def __init__(self, *, x, y, power, radius, affect_objects, particles):
        self.x = x
        self.y = y

        self.power  = power
        self.radius = radius

        self.affect_objects = affect_objects

        self.particles = particles

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(
            x = int(components[0]),
            y = int(components[1]),

            power  = int(components[2]),
            radius = int(components[3]),

            affect_objects = (components[4] == "1"),

            particles = enums.ExplosionParticles(int(components[5])),
        )

    def _body_components(self, *, ctx):
        return [
            str(self.x),
            str(self.y),
            str(self.power),
            str(self.radius),
            "1" if self.affect_objects else "0",
            str(self.particles.value),
        ]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "x",
        "y",
        "power",
        "radius",
        "affect_objects",
        "particles",
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

@public
class BanMessagePacket(ClientboundLegacyPacket):
    id = (26, 18)

    # NOTE: 'duration' is in milliseconds.
    #
    # TODO: Should we use datetime stuff
    # to represent time things instead
    # of just numbers?

    def __init__(self, reason_template, duration):
        self.reason_template = reason_template
        self.duration        = duration

    @property
    def is_permanent(self):
        return self.duration is None

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        if len(components) < 2:
            return cls(components[0], None)

        return cls(components[1], int(components[0]))

    def _body_components(self, *, ctx):
        if self.is_permanent:
            return [self.reason_template]

        return [str(self.duration), self.reason_template]

    __repr__ = ClientboundLegacyPacket.repr_for_attrs(
        "reason_template",
        "duration",
    )
