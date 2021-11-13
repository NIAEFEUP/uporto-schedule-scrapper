

def get_create_table(table_name: str, head: list[str], types: list[str]) -> str:
    num_columns = len(types)
    create_string = f"CREATE TABLE {table_name} ("

    for i in range(num_columns):
        create_string += f"{head[i]} {types[i]},"

    return create_string[:-1] + ");"