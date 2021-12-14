def _dict_to_arrays(data: dict):
    fields = []
    values = []
    param = []
    for d in data:
        fields.append(str(d))
        param.append('%s')
        values.append(data[d])

    return fields, values, param


def _dict_to_set(data: dict):
    fields = []

    param = []
    for d in data:
        # fields.append(f"{str(d)}='{str(data[d])}'")
        fields.append(f"{str(d)}=%s")
        param.append(data[d])
        # values.append(f"'{str(data[d])}'")

    return ', '.join(fields), param


def insert_query(table: str, data: dict, dup_update=False):
    fields, values, param = _dict_to_arrays(data)
    fields = ', '.join(fields)
    # values = ', '.join(values)
    param = ', '.join(param)
    if dup_update:
        set_dat, set_values = _dict_to_set(data)
        for v in set_values:
            values.append(v)
        return f'INSERT INTO {table} ({fields}) VALUES ({param}) ON DUPLICATE KEY UPDATE {set_dat};', values
    return f'INSERT INTO {table} ({fields}) VALUES ({param});', values


def select_query(table: str, data: dict):
    fields, params = _dict_to_set(data)
    return f'SELECT * FROM {table} WHERE {fields}', params


def update_query(table: str, data: dict, where: dict):
    fields, params = _dict_to_set(data)
    where, p2 = _dict_to_set(where)
    for p in p2:
        params.append(p)
    return f'UPDATE {table} SET {fields} WHERE {where}', params
