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
