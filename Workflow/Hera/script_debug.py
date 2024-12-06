from hera.workflows import script


@script()
def debug(message: str):
    print(f"Hello {message}")
