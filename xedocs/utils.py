


def docs_to_wiki(schema, docs, title=None):
    """Convert a list of documents to a dokuwiki table 

    :param title: title of the table.
    """
    if title is None:
        title = schema._ALIAS.replace('_', ' ').capitalize() + ' Table'

    columns = list(schema.get_index_fields()) + list(schema.get_column_fields())

    table = '^ %s ' % title + '^' * (len(columns) - 1) + '^\n'
    table += '^ ' + ' ^ '.join(columns) + ' ^\n'

    for doc in docs:
        data = doc.dict()
        table += "| " + ' | '.join([
            str(data[col]) for col in columns]) + ' |\n'
    return table
