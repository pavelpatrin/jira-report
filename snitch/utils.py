def split_key(key):
    """Splits task key into project code and task num."""
    project, number = key.split('-', 1)
    return project, int(number)
