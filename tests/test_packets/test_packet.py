import caseus

def test_packet_suffix():
    for packet_cls in caseus.Packet.subclasses():
        assert packet_cls.__qualname__.endswith("Packet")
