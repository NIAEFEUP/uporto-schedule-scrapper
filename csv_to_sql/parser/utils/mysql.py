

def get_create_table(table_name: str, head: list[str], types: list[str]) -> str:
    create_string = f"CREATE TABLE {table_name} ("

    for head, type in zip(head, types):
        create_string += f"\"{head}\" {type},"

    return create_string[:-1] + ");"


def get_insert_values(table_name: str, columns: list[str], values: list[str]) -> str: 
    insert_string = f"INSERT INTO {table_name} (" 

    # add columns names
    for col in columns:
        insert_string += f"\"{col}\"," 
    insert_string = insert_string[:-1] + ")"

    insert_string += " VALUES ("
    for val in values: 
        insert_string += f"\"{val}\"" + ","
    return insert_string[:-1] + ");"
        