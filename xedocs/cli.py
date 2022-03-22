"""Console script for xedocs."""
import sys

import click
from rich.console import Console
from rich.table import Table

table = Table(title="Star Wars Movies")
import xedocs

@click.group()
def main():
    """Console script for xedocs."""
    click.echo("Welcome to the xedocs CLI")
    
    return 0
    

@main.command(name='find', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument('name')
@click.pass_context
def cli_find(ctx, name: str):
    kwargs = dict([item.strip('--').split('=') for item in ctx.args])
    kwargs = {k: v.split(',') if ',' in v else v for k,v in kwargs.items()}
    schema = xedocs.find_schema(name)

    click.echo(f"Looking for {name} documents that match your query...")
    docs = schema.find(**kwargs)
    query_str = ", ".join([f'{k}={v}' for k,v in kwargs.items()])

    table = Table(title=f"{name.title()} query {query_str}")

    field_order = []
    for field in schema.get_index_fields():
        table.add_column(field.title(), justify="left")
        field_order.append(field)

    for field in schema.get_column_fields():
        table.add_column(field.title(), justify="center")
        field_order.append(field)

    for doc in docs:
        data = doc.jsonable()
        row = [str(data[field]) for field in field_order]
        table.add_row(*row)

    console = Console()
    console.print(table)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
