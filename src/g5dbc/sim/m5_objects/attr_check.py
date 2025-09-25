def attr_type_check(cls, cls_attr, v):
    cls_attr_str = type(getattr(cls, cls_attr)).__name__
    match cls_attr_str:
        case "MemorySize":
            return str(v)
        case _:
            return v
