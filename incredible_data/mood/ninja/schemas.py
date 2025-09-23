import datetime as dt
import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Annotated

from ninja import ModelSchema, Schema
from pydantic import Field

from incredible_data.mood.models import Entry, Metric, MetricType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.db import models

logger = logging.getLogger(__name__)


class MetricTypeOut(ModelSchema):
    class Meta:
        model: "type[models.Model]" = MetricType
        fields: "Iterable[str]" = [
            "id",
            "name",
            "help_text",
            "is_score",
            "higher_is_better",
            "min_value",
            "max_value",
            "scale_definition",
            "graph_color",
        ]


class MetricOut(ModelSchema):
    class Meta:
        model: "type[models.Model]" = Metric
        fields: "Iterable[str]" = ["id", "metric_type", "entry", "score_value"]


class MetricDatasetOut(ModelSchema):
    date: Annotated[dt.date, Field(..., validation_alias="entry.effective_date")]
    score_value: Annotated[int, Field(..., serialization_alias="value")]
    time_of_day: Annotated[
        Entry.TimeOfDay | None, Field(None, validation_alias="entry.time_of_day")
    ]

    class Meta:
        model: "type[models.Model]" = Metric
        fields: "Iterable[str]" = ["score_value"]


class TrendOut(ModelSchema):
    name: Annotated[str, Field(..., serialization_alias="label")]
    graph_color: Annotated[str, Field(..., serialization_alias="borderColor")]
    fill: bool = False
    tension: Decimal = Decimal("0.1")
    metric_set: Annotated[
        list[MetricDatasetOut], Field(..., serialization_alias="data")
    ]

    class Meta:
        model: "type[models.Model]" = MetricType
        fields: "Iterable[str]" = ["name", "graph_color"]


class EntryOut(ModelSchema):
    class Meta:
        model: "type[models.Model]" = Entry
        fields: "Iterable[str]" = [
            "id",
            "created_by",
            "created_on",
            "notes",
            "effective_date",
            "time_of_day",
        ]


class FieldOption(Schema):
    label: str
    value: str
