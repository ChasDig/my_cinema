class SingletonMeta(type):
    instances: dict = {}

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)

        if cls not in cls.instances.keys():
            cls.instances[cls] = instance

        return cls.instances[cls]
