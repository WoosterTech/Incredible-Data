import abc
import datetime as dt
from typing import Any, Literal, Self

from caseconverter.camel import (  # pyright: ignore[reportMissingTypeStubs]
    camelcase,  # pyright: ignore[reportUnknownVariableType]
)
from pydantic import BaseModel, ConfigDict, computed_field
from pydantic_extra_types.color import Color


class ChartJSBase(BaseModel, abc.ABC):  # pyright: ignore[reportUnsafeMultipleInheritance]
    model_config: ConfigDict = ConfigDict(alias_generator=lambda s: camelcase(s))  # pyright: ignore[reportIncompatibleVariableOverride]


class MetricChartDataPoint(BaseModel):
    date: dt.date
    value: int


class Dataset(ChartJSBase):
    label: str
    data: list[MetricChartDataPoint] = []
    border_color: Color | None = None
    background_color: Color | None = None


class ChartData(BaseModel):
    datasets: dict[str, list[MetricChartDataPoint]] = {}

    _dates: set[dt.date] = set()

    def populate_dates(self) -> None:
        for values in self.datasets.values():
            for point in values:
                self._dates.add(point.date)

    def get_dates(self, *, force: bool = False) -> set[dt.date]:
        if not self._dates or force:
            self.populate_dates()
        return self._dates

    @computed_field
    @property
    def labels(self) -> list[str]:
        sorted_dates = sorted(self.get_dates(force=True))
        return list(map(str, sorted_dates))


class Chart(ChartJSBase):
    type: Literal["line"]
    data: ChartData
    options: dict[str, Any] = {}  # pyright: ignore[reportExplicitAny]
