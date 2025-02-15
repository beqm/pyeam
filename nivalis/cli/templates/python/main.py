import nivalis

# from nivalis.tools import log
# log.Env.init().stdout().file("log.txt", json=True)
# log.info("This is my log message!")

@nivalis.command
def example(name: str):
    return f"{name}, Hello from Python!"


if __name__ == "__main__":
    nivalis.Builder.default().invokers([example]).workers(2).run()