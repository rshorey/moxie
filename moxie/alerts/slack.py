#  Copyright (c) Paul R. Tagliamonte <tag@pault.ag>, 2015
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import asyncio
from aiocore import Service


class SlackAlert:
    strings = {
        "starting": "{job.name} failed.",
        "running": "{job.name} is running.",
        "success": "{job.name} has completed successfully.",
        "error": "{job.name} had an error.",
        "failure": "{job.name} failed.",
    }

    def __init__(self, bot):
        self.bot = bot
        self.db = Service.resolve("moxie.cores.database.DatabaseService")

    @asyncio.coroutine
    def __call__(self, payload):
        job = yield from self.db.job.get(payload.get("job"))
        maintainer = yield from self.db.maintainer.get(job.maintainer_id)

        fmt = self.strings[payload["type"]]
        yield from self.bot.post(
            "#cron",
            fmt.format(job=job, maintainer=maintainer))
