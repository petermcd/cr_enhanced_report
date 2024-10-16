"""Module to overload the cosmic-ray database."""
import contextlib
from typing import Any

from cosmic_ray.work_db import (MutationSpecStorage, WorkDB, WorkItemStorage,
                                WorkResultStorage, _mutation_spec_from_storage,
                                _work_item_from_storage,
                                _work_result_from_storage)
from cosmic_ray.work_item import TestOutcome
from sqlalchemy import func


class DB(WorkDB):
    """Database handler adding new functionality to WorkDB."""

    skip_success: bool = False

    @property
    def completed_work_items(self) -> tuple[Any, ...]:
        """Iterable of all completed work items."""
        with self._session_maker.begin() as session:
            results = session.query(
                WorkItemStorage, WorkResultStorage, MutationSpecStorage
            ).where(
                WorkItemStorage.job_id == WorkResultStorage.job_id
            ).where(
                WorkItemStorage.job_id == MutationSpecStorage.job_id
            )
            if self.skip_success:
                results = results.where(
                    WorkResultStorage.test_outcome != TestOutcome.KILLED
                )
            results = results.order_by(MutationSpecStorage.module_path)
            return tuple(
                (
                    _work_item_from_storage(work_item),
                    _work_result_from_storage(result),
                    _mutation_spec_from_storage(mutation_spec)
                ) for work_item, result, mutation_spec in results
            )

    def fetch_status_counts(self):
        """Fetch status counts from the database."""
        with self._session_maker.begin() as session:
            results = session.query(
                WorkResultStorage.test_outcome,
                MutationSpecStorage.module_path,
                func.count(WorkResultStorage.test_outcome)
            ).where(
                WorkResultStorage.job_id == WorkItemStorage.job_id
            ).where(
                WorkResultStorage.job_id == MutationSpecStorage.job_id
            )
            if self.skip_success:
                results = results.where(
                    WorkResultStorage.test_outcome != TestOutcome.KILLED
                )
            results = results.group_by(
                MutationSpecStorage.module_path, WorkResultStorage.test_outcome
            ).all()

        return results


@contextlib.contextmanager
def use_db(path, mode=DB.Mode.create):
    """
    Open a DB in file `path` in mode `mode` as a context manager.

    On exiting the context the DB will be automatically closed.

    Function is a copy of cosmic-ray.work_db.use_db modified to use our
    extension of WorkDB.

    Args:
      path: The path to the DB file.
      mode: The mode to open the DB with.

    Raises:
      FileNotFoundError: If `mode` is `Mode.open` and `path` does not
        exist.
    """
    database = DB(path, mode)
    try:
        yield database

    finally:
        database.close()
