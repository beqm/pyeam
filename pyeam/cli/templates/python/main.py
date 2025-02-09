import pyeam
from pyeam.tools import log

@pyeam.command
def say_hi(name: str):
    return f"Hello from pyeam, {name}!"

if __name__ == "__main__":
    log.Env.level(log.INFO)
    log.info("Hello from pyeam!")

    pyeam.Builder.default().invokers([say_hi]).run()