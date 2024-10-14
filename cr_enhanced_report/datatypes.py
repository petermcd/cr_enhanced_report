"""Module to declare datatypes used in the cosmic-ray report."""
import enum

from attr import dataclass


class HtmlColor(enum.Enum):
    """Enum to store HTML colors for different states."""

    amber = 'orange'
    green = 'green'
    lightgrey = 'lightgrey'
    red = 'red'


@dataclass
class TaskData:
    """Data class to store report summary data."""

    module_path: str
    status_count: dict[str, int]
