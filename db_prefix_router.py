# db_prefix_router.py

def get_prefixed_db_table(model):
    if not model._meta.managed:
        return model._meta.db_table
    return f"j_{model._meta.db_table}"

class TableNamePrefixMixin:
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)
        if hasattr(new_class, "_meta") and hasattr(new_class._meta, "db_table") and new_class._meta.managed:
            if not new_class._meta.abstract:
                new_class._meta.db_table = get_prefixed_db_table(new_class)
        return new_class
