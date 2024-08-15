class Singleton:
    """
    A class that implements the Singleton design pattern.

    The Singleton class ensures that only one instance of the class is created throughout the program.

    Attributes:
        _instance (Singleton): The single instance of the class.

    Methods:
        __new__(cls): Creates a new instance of the class if it doesn't exist, otherwise returns the existing instance.

    Usage:
        singleton_instance = Singleton()
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
