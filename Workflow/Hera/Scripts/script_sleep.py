from hera.workflows import script


@script()
def sleep(delay: int):
    import time
    print(f"Sleeping for {delay} seconds.")
    time.sleep(delay)
    print(f"Waking up and exiting.")
