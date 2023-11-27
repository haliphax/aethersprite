# 3rd party
from uvicorn import run

# local
from .. import config


def start_server():
    """Run ASGI web application in a uvicorn server."""

    wconfig = config.get("webapp", {})

    run(
        "aethersprite.webapp:app",
        host=wconfig.get("host", "0.0.0.0"),
        port=int(wconfig.get("port", 5000)),
        lifespan="off",
    )


if __name__ == "__main__":
    start_server()
