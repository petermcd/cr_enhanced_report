"""Console script for cr_enhanced_report."""
import re
import sys

import click

from cr_enhanced_report.db import DB, use_db
from cr_enhanced_report.reporter import Reporter


@click.command()
@click.option("--only-completed/--not-only-completed", default=False)
@click.option("--skip-success/--include-success", default=False)
@click.argument("session-file", type=click.Path(dir_okay=False, readable=True, exists=True))
def cr_enhanced_report(only_completed, skip_success, session_file) -> None:
    """
    Create an enhanced Cosmic-Ray report.

    Args:
        only_completed: If `True`, only the completed work items.
        skip_success: If `True`, skip all successful work items.
        session_file: The path to the session file.
    """
    with use_db(session_file, DB.Mode.open) as db:
        db.skip_success = skip_success
        report = Reporter(db=db, only_completed=only_completed)
        report.create_report()


def main() -> None:
    """Entry point."""
    # sys.argv.append('cosmic.sqlite')
    sys.exit(cr_enhanced_report())


if __name__ == '__main__':
    """Handle calls directly to the module."""
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.argv.append('/Users/peter/PycharmProjects/cr_enhanced_report/cosmic.sqlite')
    main()
