"""Console script for xedocs."""
import os
import sys
import time
import xedocs
import click
import logging

from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress


logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("xedocs")


def to_str(obj):
    if isinstance(obj, (list, tuple)):
        content = ",".join([to_str(x) for x in obj])
        return f"({content})"
    if isinstance(obj, dict):
        return ",".join([f"{k}={to_str(v)}" for k, v in obj.items()])
    return f"{obj}"


@click.group()
def main():
    """Console script for xedocs."""
    click.echo("Welcome to the xedocs CLI")

    return 0


@main.command(
    name="find",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("name")
@click.pass_context
def cli_find(ctx, name: str):
    console = Console()
    kwargs = dict([item.strip("--").split("=") for item in ctx.args])
    kwargs = {k: v.split(",") if "," in v else v for k, v in kwargs.items()}
    try:
        schema = xedocs.find_schema(name)
    except KeyError:
        logger.error(
            f"Cant find a schema for `{name}`\n"
            f"Available schemas: {xedocs.list_schemas()}"
        )
        exit(0)

    query_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])

    table = Table(title=f"{name.title()} query {query_str}")

    field_order = []
    for field in schema.get_index_fields():
        table.add_column(field.title(), justify="left")
        field_order.append(field)

    for field in schema.get_column_fields():
        table.add_column(field.title(), justify="center")
        field_order.append(field)

    with console.status(
        f"[bold green]Looking for {name} documents that match your query..."
    ) as status:
        docs = schema.find_iter(**kwargs)

    with Live(table, refresh_per_second=4):

        for doc in docs:
            data = doc.jsonable()
            row = [str(data[field]) for field in field_order]
            table.add_row(*row)
            time.sleep(0.1)


@main.command(
    name="download",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.argument("name")
@click.option("path", "--path", "-p", default=".", help="Path to download to")
@click.pass_context
def cli_download(ctx, name: str, path: str = None):
    console = Console()
    kwargs = dict([item.strip("--").split("=") for item in ctx.args])
    kwargs = {k: v.split(",") if "," in v else v for k, v in kwargs.items()}
    try:
        schema = xedocs.find_schema(name)
    except KeyError:
        logger.error(
            f"Cant find a schema for `{name}`\n"
            f"Available schemas: {xedocs.list_schemas()}"
        )
        exit(0)

    fname = f"{name}-{to_str(kwargs)}.csv"
    path = os.path.join(path, fname)
    fpath = os.path.abspath(path)

    with console.status(
        f"[bold green]Looking for {name} documents that match your query..."
    ) as status:
        df = schema.find_df(**kwargs)

    with console.status(f"[bold green]Saving {name} documents to {path}") as status:
        df.to_csv(fpath)
        time.sleep(1)

    console.print(f"Data saved to {fpath}")


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
