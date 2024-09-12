from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseModelCamel(BaseModel):
    """Base model with camel case alias generator.

    Example:
    ```python
    class Event(BaseModelCamel):
        html_link: AnyUrl
        created: datetime
    ```

    `html_link` will be serialized as `htmlLink`.
    """

    model_config = ConfigDict(alias_generator=lambda field_name: to_camel(field_name))
