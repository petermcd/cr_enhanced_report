"""Module to create the Cosmic Ray report."""
import re

from cosmic_ray.tools.html import pycharm_url
from cosmic_ray.work_item import TestOutcome
from yattag import Doc

from cr_enhanced_report.datatypes import HtmlColor, TaskData
from cr_enhanced_report.db import DB


class Reporter(object):
    """Create an enhanced cosmic-ray work report from scratch."""

    __slots__ = (
        '_db',
        '_only_completed',
    )

    def __init__(self, db, only_completed) -> None:
        """
        Initialize Reporter.

        Args:
            db: Instance of MyDB
            only_completed: If `True`, only completed work items are reported.
        """
        self._db: DB = db
        self._only_completed: bool = only_completed

    def create_report(self) -> None:
        """Create a report from scratch."""
        doc, tag, text, line = Doc().ttl()
        doc.asis("<!DOCTYPE html>")
        with (tag("html", lang="en")):
            with tag("head"):
                doc.stag("meta", charset="utf-8")
                doc.stag("meta", name="viewport", content="width=device-width, initial-scale=1, shrink-to-fit=no")
                doc.stag(
                    "link",
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
                    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH",
                    crossorigin="anonymous",
                )
                self._css(tag=tag, text=text)
                with tag("title"):
                    text("Cosmic Ray Enhanced Report")
            with tag("body"):
                with tag("div", klass="container"):
                    self._create_summary(tag=tag, text=text)
                    self._create_analysis(tag=tag, text=text)
                with tag("script"):
                    doc.attr(src="https://code.jquery.com/jquery-3.7.1.js")
                    doc.attr(
                        ("integrity", "sha256-eKhayi8LEQwp4NKxN+CfCh+3qOVUtJn3QNZ0TciWLP4=")
                    )
                    doc.attr(("crossorigin", "anonymous"))
                with tag("script"):
                    doc.attr(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js")
                    doc.attr(
                        ("integrity", "sha384-0pUGZvbkm6XF6gxjEnlmuGrJXVbNuzT9qBBavbLwCsOGabYfZo0T0to5eqruptLy")
                    )
                    doc.attr(("crossorigin", "anonymous"))

        print(doc.getvalue())

    def _create_analysis(self, tag, text) -> None:
        """
        Create analysis section from scratch.

        Args:
            tag: Tag object.
            text: Text object.
        """
        with tag("section", id="file-analysis"):
            work_item_data = self._fetch_work_items_data()
            with tag("div", klass="accordion accordion-flush", id="accordian-files"):
                file_id = 1
                for file_name in sorted(work_item_data.keys()):
                    with tag("div", klass="accordion-item"):
                        with tag("h2", klass="accordion-header", id=f"flush-heading{file_id}"):
                            with tag(
                                "button",
                                ("data-bs-toggle", "collapse"),
                                ("data-bs-target", f"#flush-collapse{file_id}"),
                                ("aria-expanded", "false"),
                                ("aria-controls", f"flush-collapse{file_id}"),
                                klass="accordion-button collapsed",
                                type="button",
                                id=self._normalize_path(str(file_name)),
                            ):
                                text(str(file_name))
                        with tag(
                            "div",
                            ("data-bs-parent", "#accordian-files"),
                            ("aria-labelledby", "flush-heading{file_id}"),
                            klass="accordion-collapse collapse",
                            id=f"flush-collapse{file_id}"
                        ):
                            with tag("div", klass="accordion-body"):
                                self._create_file_analysis(
                                    file_id=file_id, file_tasks=work_item_data[file_name], tag=tag, text=text
                                )
                    file_id += 1

    def _fetch_work_items_data(self):
        """Fetch and organize work items based on the file."""
        if self._only_completed:
            # TODO ensure this only fetches completed work items.
            work_items = self._db.completed_work_items
        else:
            # TODO fix so that this fetches all work items.
            work_items = self._db.completed_work_items
        work_item_groups = {}
        for work_item in work_items:
            if work_item[2].module_path not in work_item_groups:
                work_item_groups[work_item[2].module_path] = []
            work_item_groups[work_item[2].module_path].append(work_item)
        return work_item_groups

    @staticmethod
    def _create_file_analysis(file_id: int, file_tasks, tag, text) -> None:
        with tag("div", klass="accordion-item", id=f"accordiantasks-{file_id}"):
            task_id = 1
            for file_task in file_tasks:
                with tag("div", klass="accordion-item"):
                    with tag("h2", klass="accordion-header", id=f"flush-heading-{file_id}-{task_id}"):
                        with tag(
                            "button",
                            ("data-bs-toggle", "collapse"),
                            ("data-bs-target", f"#flush-collapse-{file_id}-{task_id}"),
                            ("aria-expanded", "false"),
                            ("aria-controls", f"flush-collapse-{file_id}-{task_id}"),
                            klass=f"accordion-button collapsed {file_task[1].test_outcome.value}",
                            type="button",
                        ):
                            with tag("span", klass="job_id"):
                                text(file_task[0].job_id)
                    with tag(
                        "div",
                        ("aria-labelledby", f"flush-heading-{file_id}"),
                        ("data-bs-parent", f"#accordiantasks-{file_id}"),
                        klass="accordion-collapse collapse",
                        id=f"flush-collapse-{file_id}-{task_id}",
                    ):
                        with tag("div", klass="accordion-body"):
                            with tag("section", klass=f"task-summary {file_task[1].test_outcome.value}"):
                                with tag("p"):
                                    with tag("b"):
                                        text(file_task[1].test_outcome.value.upper())
                                with tag("p"):
                                    text(f'Worker outcome: {file_task[1].worker_outcome.value}')
                                with tag("p"):
                                    text(f'Test outcome: {file_task[1].test_outcome.value}')

                            with tag("pre", klass="location"):
                                with tag(
                                    "a",
                                    href=pycharm_url(str(file_task[2].module_path), file_task[2].start_pos[0]),
                                    klass="text-secondary",
                                ):
                                    with tag("button", klass="btn btn-outline-dark"):
                                        text(
                                            f"{file_task[2].module_path}, "
                                            + f"start pos: {file_task[2].start_pos}, end pos: {file_task[2].end_pos}"
                                        )
                            with tag("p"):
                                text(f"Operator: {file_task[2].operator_name}, Occurrence: {file_task[2].occurrence}")
                            with tag("pre", klass="task-diff"):
                                text(file_task[1].diff)
                            with tag("pre", klass="task-output"):
                                text(file_task[1].output)
                task_id += + 1

    def _create_summary(self, tag, text) -> None:
        """
        Create report summary section from scratch.

        Args:
            tag: Tag object.
            text: Text object.
        """
        with tag("section", id="report-summary"):
            with tag("h2"):
                text('Summary')
            with tag("p"):
                with tag("a", ("data-toggle", "collapse"), ("aria-expanded", "false"), ("aria-controls", "summary"),
                         klass="btn btn-primary", href="#summary", role='button'):
                    text('summary')
            with tag("div", klass="collapse.show", id="summary"):
                with tag("div", klass="card card-body"):
                    with tag("table"):
                        with tag("thead"):
                            with tag("tr"):
                                with tag("th"):
                                    text('Path')
                                with tag("th"):
                                    text('Score')
                                with tag("th"):
                                    text(TestOutcome.KILLED.capitalize())
                                with tag("th"):
                                    text(TestOutcome.INCOMPETENT.capitalize())
                                with tag("th"):
                                    text(TestOutcome.SURVIVED.capitalize())
                        with tag("tbody"):
                            summary_data = self._fetch_summary_data()
                            for summary_item_key in summary_data.keys():
                                with tag("tr"):
                                    with tag("td"):
                                        if summary_item_key == 'all':
                                            text(summary_item_key)
                                        else:
                                            with tag("a", href=f'#{self._normalize_path(summary_item_key)}'):
                                                text(summary_item_key)
                                    score = self._calculate_score(
                                        killed=summary_data[summary_item_key].status_count.get(TestOutcome.KILLED,
                                                                                               0),
                                        incompetent=summary_data[summary_item_key].status_count.get(
                                            TestOutcome.INCOMPETENT, 0),
                                        survived=summary_data[summary_item_key].status_count.get(
                                            TestOutcome.SURVIVED, 0),
                                    )
                                    with tag("td", klass=self._score_color(score=score)):
                                        text(f'{score}%')
                                    with tag("td", klass="killed"):
                                        text(summary_data[summary_item_key].status_count.get(TestOutcome.KILLED, 0))
                                    with tag("td", klass="incompetent"):
                                        text(
                                            summary_data[summary_item_key].status_count.get(TestOutcome.INCOMPETENT, 0))
                                    with tag("td", klass="survived"):
                                        text(summary_data[summary_item_key].status_count.get(TestOutcome.SURVIVED, 0))

    def _fetch_summary_data(self):
        """Fetch data used for the report summary."""
        task_data = {}
        status_counts = self._db.fetch_status_counts()
        task_data['all'] = TaskData(module_path='all', status_count={})
        for status_count in status_counts:
            if status_count[1] not in task_data:
                task_data[status_count[1]] = TaskData(module_path=status_count[1], status_count={})
            task_data[status_count[1]].status_count[status_count[0]] = status_count[2]
            task_data['all'].status_count[status_count[0]] = task_data['all'].status_count.get(
                status_count[0], 0
            ) + status_count[2]
        return task_data

    @staticmethod
    def _calculate_score(killed: int, incompetent: int, survived: int) -> float:
        """
        Calculate the mutation score based on values provided.

        Args:
            killed: Number of killed mutations.
            incompetent: Number of incompetent mutations.
            survived: Number of survived mutations.

        Returns:
            Score as a percentage to 2 decimal places.
        """
        total_tests = killed + incompetent + survived
        if killed == 0:
            return 0.
        return round(killed / total_tests * 100, 2)

    @staticmethod
    def _normalize_path(path: str) -> str:
        """
        Normalize a path to use as a document link.

        Args:
            path: Path to normalize.

        Returns:
            Normalized path.
        """
        return re.sub(pattern=r'[\/.]', repl='_', string=path)

    @staticmethod
    def _score_color(score: float) -> str:
        """
        Calculate the score color.

        Args:
            score: Score as a percentage to 2 decimal places.

        Returns:
            HtmlColor based on the score.
        """
        if score >= 80.01:
            return 'killed'
        if score >= 50.01:
            return 'incompetent'
        return 'survived'

    @staticmethod
    def _css(tag, text) -> None:
        with tag("style"):
            text(f"""
                .survived {{
                    background-color: {HtmlColor.red.value};
                    color: white;
                }}
                .incompetent {{
                    background-color: {HtmlColor.amber.value};
                }}
                .killed {{
                    background-color: {HtmlColor.green.value};
                    color: white;
                }}
                .task-output, .task-diff {{
                    background-color: {HtmlColor.lightgrey.value};
                    padding: 30px;
                }}
                .task-summary {{
                    padding: 10px 30px;
                    margin-bottom: 20px;
                }}
            """)
