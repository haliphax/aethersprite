"""Web application"""

# stdlib
from importlib import import_module

# 3rd party
from fastapi import APIRouter, FastAPI

# local
from .. import config, log

app = FastAPI()
"""Web application"""

router = APIRouter()
"""Router for web application"""


def _load_ext(ext, package=None):
    mod = import_module(ext, package)

    if hasattr(mod, "META_EXTENSION") and mod.META_EXTENSION:
        for child in mod._mods:
            _load_ext(f"..{child}", ext)

    if not hasattr(mod, "setup_webapp"):
        return

    log.info(f"Web app setup: {mod.__name__}")
    mod.setup_webapp(app, router)


# probe extensions for web app hooks
for ext in config["bot"]["extensions"]:
    _load_ext(ext)

app.include_router(router)
