from public import public

from ..packet import ClientboundLegacyPacket

@public
class SetSyncingPlayerPacket(ClientboundLegacyPacket):
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
