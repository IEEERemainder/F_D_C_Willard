from CommandContext import CommandContext

class Command:
    def __init__(self, method, nameOrNames, *constraints):
        self.method = method
        self.names = nameOrNames if isinstance(nameOrNames, list) else [nameOrNames]
        self.constraints = constraints or []

    async def __call__(self, ctx):
        for c in self.constraints:
            c.check(msg)
        await self.method(ctx)