def write_markdown(path: str, content: str):
    with open(path, "w") as file:
        file.write(content)
