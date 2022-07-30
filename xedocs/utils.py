
import pandas as pd


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
        table += "| " + ' | '.join([
            str(getattr(doc, col)) for col in columns]) + ' |\n'
    return table


def docs_to_dataframe(schema, docs):
    docs = [doc.pandas_dict() for doc in docs]
    df = pd.json_normalize(docs)
    if not len(df):
        df = df.reindex(columns=list(schema.__fields__))
    index_fields = list(schema.get_index_fields())
    if len(index_fields) == 1:
        index_fields = index_fields[0]
    return df.set_index(index_fields)
