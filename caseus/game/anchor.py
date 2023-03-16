import dataclasses

from public import public

@public
@dataclasses.dataclass
class Anchor:
    anchor_id: int

    object_id: int
    offset_x:  float
    offset_y:  float
    rotation:  float

    other_object_id: int
    other_offset_x:  float
    other_offset_y:  float
    other_rotation:  float

    speed: float
    power: float

    BACKGROUND_OBJECT_ID = -2

    @classmethod
    def from_description(cls, description):
        (
            anchor_id,

            object_id,
            offset_x,
            offset_y,
            rotation,

            other_object_id,
            other_offset_x,
            other_offset_y,
            other_rotation,

            speed,
            power,
        ) = description.split(",")

        return cls(
            int(anchor_id),

            int(object_id),
            float(offset_x),
            float(offset_y),
            float(rotation),

            int(other_object_id),
            float(other_offset_x),
            float(other_offset_y),
            float(other_rotation),

            float(speed),
            float(power),
        )

    @property
    def description(self):
        return ",".join(
            str(x)

            for x in [
                self.anchor_id,

                self.object_id,
                self.offset_x,
                self.offset_y,
                self.rotation,

                self.other_object_id,
                self.other_offset_x,
                self.other_offset_y,
                self.other_rotation,

                self.speed,
                self.power,
            ]
        )
