from public import public

from ..packet import ServerboundLegacyPacket

from ... import game

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
