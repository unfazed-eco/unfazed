import typing as t

type CanBeImported = t.Annotated[str, "can be imported by unfazed.utils.import_string"]
type Domain = t.Annotated[str, "domain name: 127.0.0.1:9527"]
