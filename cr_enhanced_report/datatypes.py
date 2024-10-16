"""Module to declare datatypes used in the cosmic-ray report."""
import enum
import pathlib

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


class SummaryDetail(object):
    """Object to store summary details for a given file."""

    __slots__ = (
        '_file',
        '_killed',
        '_incompetent',
        '_survived',
    )

    def __init__(
        self,
        path: pathlib.Path,
        killed: int = 0,
        incompetent: int = 0,
        survived: int = 0,
    ) -> None:
        """
        Initialize a SummaryDetail object.

        Args:
            path (pathlib.Path): Path to the summary file.
            killed (int, optional): Killed status. Defaults to 0.
            incompetent (int, optional): Incompetent status. Defaults to 0.
            survived (int, optional): Survived status. Defaults to 0.
        """
        self._file = path
        self._incompetent = incompetent
        self._killed = killed
        self._survived = survived

    @property
    def file(self) -> pathlib.Path:
        """
        Property for file and path.

        Returns:
            pathlib.Path: Path for the file the summary is for.
        """
        return self._file

    @property
    def killed(self) -> int:
        """
        Property for killed status. Defaults to 0.

        Returns:
            int: Killed status.
        """
        return self._killed

    @killed.setter
    def killed(self, killed: int) -> None:
        """
        Setter for killed status. Defaults to 0.

        Args
            killed (int): Killed status.
        """
        self._killed = killed

    @property
    def incompetent(self) -> int:
        """
        Property for incompetent status. Defaults to 0.

        Returns:
            int: Incompetent status.
        """
        return self._incompetent

    @incompetent.setter
    def incompetent(self, incompetent: int) -> None:
        """
        Setter for incompetent status. Defaults to 0.

        Args
            incompetent (int): Incompetent status.
        """
        self._incompetent = incompetent

    @property
    def score(self) -> float:
        """
        Property for the score for the file.

        Returns:
            Float: Score for the file.
        """
        total_tests = self.killed + self.incompetent + self.survived
        if self.killed == 0:
            return 0.
        return round(self.killed / total_tests * 100, 2)

    @property
    def survived(self) -> int:
        """
        Property for survived status. Defaults to 0.

        Returns:
            int: Survived status.
        """
        return self._survived

    @survived.setter
    def survived(self, survived: int = 0) -> None:
        """
        Setter for survived status. Defaults to 0.

        Args
            survived (int): Survived status.
        """
        self._survived = survived

    def __eq__(self, other: object) -> bool:
        """
        Equals operator.

        Args:
            other (object): Other object.

        Returns:
            True if self equals other, False otherwise.
        """
        if isinstance(other, SummaryDetail):
            return self._file == other._file
        return False

    def __ge__(self, other: 'SummaryDetail') -> bool:
        """
        Greater than or equal operator.

        Args:
            other (SummaryDetail): Other object.

        Returns:
            True if self greater than or equals other, False otherwise.
        """
        if self.__eq__(other):
            return True
        return self.__gt__(other)

    def __gt__(self, other: 'SummaryDetail') -> bool:
        """
        Greater than operator.

        Args:
            other (SummaryDetail): Other object.

        Returns:
            True if self greater than other, False otherwise.
        """
        this_path = self.file.parent
        other_path = other.file.parent
        if this_path == other_path:
            return self.file > other.file
        if str(this_path).startswith(str(other_path)):
            return False
        if str(other_path).startswith(str(this_path)):
            return True
        return self.file > other.file

    def __le__(self, other: 'SummaryDetail') -> bool:
        """
        Less than or equals operator.

        Args:
            other (SummaryDetail): Other object.

        Returns:
            True if self less than or equals other, False otherwise.
        """
        if self.__eq__(other):
            return True
        return self.__lt__(other)

    def __lt__(self, other: 'SummaryDetail') -> bool:
        """
        Less than operator.

        Args:
            other (SummaryDetail): Other object.

        Returns:
            True if self less than other, False otherwise.
        """
        this_path = self.file.parent
        other_path = other.file.parent
        if this_path == other_path:
            return self.file < other.file
        if str(this_path).startswith(str(other_path)):
            return True
        if str(other_path).startswith(str(this_path)):
            return False
        return self.file < other.file

    def __ne__(self, other: object) -> bool:
        """
        Not equals operator.

        Args:
            other (object): Other object.

        Returns:
            True if self not equals other, False otherwise.
        """
        return not self.__eq__(other)
