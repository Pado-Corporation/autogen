def read_file(path: str):
    with open(path, "r") as file:
        content = file.read()
    return content
