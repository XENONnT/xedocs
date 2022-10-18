import pandas as pd

from collections import UserDict


def docs_to_wiki(schema, docs, title=None, columns=None):
    """Convert a list of documents to a dokuwiki table

    :param title: title of the table.
    """
    if title is None:
        title = schema._ALIAS.replace("_", " ").capitalize() + " Table"

    if columns is None:
        columns = list(schema.get_index_fields()) + list(schema.get_column_fields())

    table = "^ %s " % title + "^" * (len(columns) - 1) + "^\n"
    table += "^ " + " ^ ".join(columns) + " ^\n"

    for doc in docs:
        table += "| " + " | ".join([str(getattr(doc, col)) for col in columns]) + " |\n"
    return table


def docs_to_dataframe(schema, docs, columns=None):
    if columns is None:
        columns = list(schema.__fields__)
    else:
        columns = list(columns)

    docs = [doc.pandas_dict() for doc in docs]
    df = pd.json_normalize(docs)

    if len(df):
        df = df[columns]
    else:
        df = df.reindex(columns=list(columns))

    index_fields = [name for name in schema.get_index_fields() if name in columns]

    if len(index_fields) == 1:
        index_fields = index_fields[0]

    return df.set_index(index_fields)


class DatasetCollection(UserDict):
    def __getattr__(self, attr):
        if attr in self.keys():
            return self[attr]
        raise AttributeError(attr)

    def __dir__(self):
        return list(self.keys())
