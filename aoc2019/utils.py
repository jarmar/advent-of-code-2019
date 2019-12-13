import itertools


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def ichunks(iterable, n):
    while True:
        chunk = tuple(itertools.islice(iterable, n))
        if not chunk:
            return
        yield chunk
