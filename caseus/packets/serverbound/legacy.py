from public import public

from ..packet import ServerboundLegacyPacket

from ... import enums
from ... import game

@public
class RemoveExplodedObjectPacket(ServerboundLegacyPacket):
    id = (4, 6)

    def __init__(self, object_id):
        self.object_id = object_id

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(int(components[0]))

    def _body_components(self, *, ctx):
        return [str(self.object_id)]

    __repr__ = ServerboundLegacyPacket.repr_for_attrs("object_id")

@public
class AddAnchorsPacket(ServerboundLegacyPacket):
    id = (5, 7)

    def __init__(self, anchors):
        self.anchors = list(anchors)

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(game.Anchor.from_description(description) for description in components)

    def _body_components(self, *, ctx):
        return [anchor.description for anchor in self.anchors]

    __repr__ = ServerboundLegacyPacket.repr_for_attrs("anchors")

@public
class SyncExplosionPacket(ServerboundLegacyPacket):
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

    __repr__ = ServerboundLegacyPacket.repr_for_attrs(
        "x",
        "y",
        "power",
        "radius",
        "affect_objects",
        "particles",
    )

@public
class MapEditorXMLPacket(ServerboundLegacyPacket):
    id = (14, 10)

    def __init__(self, xml):
        self.xml = xml

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls(components[0])

    def _body_components(self, *, ctx):
        return [self.xml]

    __repr__ = ServerboundLegacyPacket.repr_for_attrs("xml")

@public
class ReturnToMapEditorPacket(ServerboundLegacyPacket):
    id = (14, 14)

    def __init__(self):
        pass

    @classmethod
    def _from_body_components(cls, components, *, ctx):
        return cls()

    def _body_components(self, *, ctx):
        return []

    __repr__ = ServerboundLegacyPacket.repr_for_attrs()
