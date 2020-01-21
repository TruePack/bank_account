from gino.ext.aiohttp import Gino as Gino_


class Gino(Gino_):
    __instance = None

    @staticmethod
    def init():
        if Gino.__instance is None:
            Gino.__instance = Gino_()
        return Gino.__instance
