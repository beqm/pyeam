import pyeam
from pyeam.tools import log

@pyeam.command
def example(name: str):
    return f"Greetings from Pyeam {name}!"

if __name__ == "__main__":
    log.Env.level(log.INFO)
    log.info("Hello from pyeam!")

    pyeam.Builder.default().invokers([example]).run()