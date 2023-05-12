import logging
import logging.config 

class Logger():

    def __init__(self, name):
        self.name = name
        self.log = logging.getLogger(self.name)

    async def LogInfo(self, message):
        self.log.info(message)

    async def LogError(self, message):
        self.log.error(message)

    async def LogWarning(self, message):
        self.log.warning(message)