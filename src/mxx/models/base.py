
from dataclasses import dataclass, field
import typing


@dataclass(init=False)
class BaseModel:
    extra : dict = field(default_factory=dict)

    def update(self, data : dict):
        extra = {}
        for key in list(data.keys()):
            if key not in self.__class__.__dataclass_fields__:
                extra[key] = data[key]
            elif getattr(self, key) is not None and isinstance(getattr(self, key), BaseModel):
                getattr(self, key).update(data[key])
            else:
                setattr(self, key, data[key])

        self.extra = extra

    @classmethod
    def create(cls, data : dict):
        # Create a copy to avoid modifying original data
        data = data.copy()
        
        for k, v in list(data.items()):
            if k in cls.__dataclass_fields__:
                field_type = cls.__dataclass_fields__[k].type
                
                # Handle Optional types
                origin = typing.get_origin(field_type)
                if origin is typing.Union:
                    # Get the non-None type from Optional
                    args = typing.get_args(field_type)
                    field_type = next((arg for arg in args if arg is not type(None)), None)
                
                # Check if it's a BaseModel subclass and v is a dict
                if field_type and isinstance(v, dict):
                    try:
                        if issubclass(field_type, BaseModel):
                            data[k] = field_type.create(v)
                    except TypeError:
                        # Not a class, skip
                        pass
        
        # Filter out extra fields that aren't in dataclass
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        instance = cls(**valid_fields)
        
        # Store extra fields
        extra_fields = {k: v for k, v in data.items() if k not in cls.__dataclass_fields__}
        if extra_fields:
            instance.extra = extra_fields
        
        return instance