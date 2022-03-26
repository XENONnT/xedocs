"""Console script for xedocs."""
import sys
import time
import xedocs
import click
import logging

from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from rich.live import Live


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("xedocs")


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
    console = Console()
    kwargs = dict([item.strip('--').split('=') for item in ctx.args])
    kwargs = {k: v.split(',') if ',' in v else v for k,v in kwargs.items()}
    try:
        schema = xedocs.find_schema(name)
    except KeyError:
        logger.error(f'Cant find a schema for `{name}`\n'
                    f'Available schemas: {xedocs.list_schemas()}'
        )
        exit(0)
    
    query_str = ", ".join([f'{k}={v}' for k,v in kwargs.items()])

    table = Table(title=f"{name.title()} query {query_str}")

    field_order = []
    for field in schema.get_index_fields():
        table.add_column(field.title(), justify="left")
        field_order.append(field)

    for field in schema.get_column_fields():
        table.add_column(field.title(), justify="center")
        field_order.append(field)

    with console.status(f"[bold green]Looking for {name} documents that match your query...") as status:
        docs = schema.find_iter(**kwargs)

    with Live(table, refresh_per_second=4):

        for doc in docs:
            data = doc.jsonable()
            row = [str(data[field]) for field in field_order]
            table.add_row(*row)
            time.sleep(0.1)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
