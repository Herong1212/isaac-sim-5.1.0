import os

import carb

import uvicorn

class _Server(uvicorn.Server):
    def install_signal_handlers(self):
        # To avoid uvicorn catching sigint as well as installing signals from a thread which does not work
        pass

    async def serve(self, sockets=None):
        process_id = os.getpid()

        config = self.config
        if not config.loaded:
            config.load()

        self.lifespan = config.lifespan_class(config)

        self.install_signal_handlers()

        carb.log_info(f"Started server process [{process_id}]")

        await self.startup(sockets=sockets)
        if self.should_exit:
            return
        await self.main_loop()
        await self.shutdown(sockets=sockets)

        carb.log_info(f"Finished server process [{process_id}]")