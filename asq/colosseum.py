from autogen import GroupChat


class Colosseum(GroupChat):
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
