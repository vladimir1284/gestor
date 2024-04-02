def url_match(url: str, pattern: str) -> bool:
    # Remove query params
    url = url.split("?")[0]
    if url.endswith("/"):
        url = url[:-1]

    # Exctract components
    url_components = url.split("/")
    pat_components = pattern.split("/")

    # Components match
    if len(url_components) != len(pat_components):
        return False

    for i in range(len(pat_components)):
        pc = pat_components[i]
        # Ignore params
        if pc == "" or pc == "+":
            continue

        # Not match
        if pc != url_components[i]:
            return False

    return True


def url_match_internal(url: str, pattern: str, start: bool = False) -> bool:
    # Remove query params
    url = url.split("?")[0]
    if url.endswith("/"):
        url = url[:-1]
    if url.startswith("/"):
        url = url[1:]

    if pattern.endswith("/"):
        pattern = pattern[:-1]
    if pattern.startswith("/"):
        pattern = pattern[1:]

    # Exctract components
    url_components = url.split("/")
    pat_components = pattern.split("/")

    # Components match
    if start:
        if len(url_components) < len(pat_components):
            return False
    else:
        if len(url_components) != len(pat_components):
            return False

    for i in range(len(pat_components)):
        pc = pat_components[i]
        # Ignore params
        if pc.startswith("%"):
            continue

        # Not match
        if pc != url_components[i]:
            return False

    return True
