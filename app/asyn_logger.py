import logging

class asyn_logger():

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(self.name)
        self.log.error('call get LOGGER' )
        self.log.error(name)
        self.logError("this is a msg")

    async def logInfo(self, message):
        self.log.info(message)

    async def logError(self, message):
        self.log.error(message)

    async def logWarning(self, message):
        self.log.warning(message)


