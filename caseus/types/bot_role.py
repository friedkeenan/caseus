import pak

from public import public

@public
class UnlessBotRole(pak.DeferringType):
    underlying = None

    @classmethod
    def _defer_to(cls, *, ctx):
        if ctx.is_bot_role():
            return pak.EmptyType

        return cls.underlying

    @classmethod
    @pak.Type.prepare_types
    def _call(cls, underlying: pak.Type):
        return cls.make_type(
            f"{cls.__qualname__}({underlying.__qualname__})",

            underlying = underlying,
        )
