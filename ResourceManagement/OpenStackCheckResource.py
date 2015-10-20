#!/usr/bin/python
def print_list(objs, fields, formatters={}, sortby_index=None):
    new_dict = dict()
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    mixed_case_fields = ['serverId']

    for o in objs:
        row = []
        data = None
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                olddata = data
                data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                row.append(data)
        new_dict[olddata] = data
    return new_dict
