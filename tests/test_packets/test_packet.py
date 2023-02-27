import caseus

def test_packet_suffix():
    for parent_cls in (caseus.Packet, caseus.TribullePacket, caseus.LegacyPacket, caseus.ExtensionPacket):
        for packet_cls in parent_cls.subclasses():
            assert packet_cls.__qualname__.endswith("Packet")
