import typing
from dataclasses import dataclass

from ._enums import SqlDataType


class ColumnDescription(typing.NamedTuple):
    """A description of a result set column.

    https://www.python.org/dev/peps/pep-0249/#description
    """

    name: str
    type_code: type
    display_size: typing.Optional[int] = None
    internal_size: typing.Optional[int] = None
    precision: typing.Optional[int] = None
    scale: typing.Optional[int] = None
    null_ok: typing.Optional[bool] = None


@dataclass(frozen=True)
class SqlColumnDescription:
    """Internal object which describes a result set column."""

    name: str
    data_type: SqlDataType
    python_data_type: type
    size: int
    decimal_digits: int
    is_nullable: bool
    column_number: int

    def to_column_description(self) -> ColumnDescription:
        column_description = ColumnDescription(
            name=self.name,
            type_code=self.python_data_type,
            # TODO: display_size is hard-coded as in pyodbc - is this ok?
            display_size=None,
            # TODO: internal_size is set as in pyodbc - is this ok?
            internal_size=self.size,
            precision=self.size,
            scale=self.decimal_digits,
            null_ok=self.is_nullable,
        )
        return column_description
