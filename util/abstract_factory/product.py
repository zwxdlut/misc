from abc import ABC, abstractmethod


class Attribute:
    """
    Attribute.
    """

    def __init__(self, width: int = 0, height: int = 0) -> None:
        self.width = width
        self.height = height

    def __del__(self) -> None:
        pass


class IProduct(ABC):
    """
    Interface of product.

    Parameters
    ----------
    id : int
        The id.

    date : str
        The date.

    attribute : Attribute
        The attribute.

    Returns
    -------

    Attributes
    ----------

    See Also
    --------

    Examples
    --------
    Create a product A.

    >> attr = Attribute(100, 100)
    >> factory = ProductAFactory()
    >> product = factory.create(1, "2024-10-01", attr)
    >> dataset.get_attribute()
    
    """

    def __init__(self, id: int, date: str, attribute: Attribute = None) -> None:
        self.id = id
        self.date = date
        self.attribute = attribute

    def __del__(self) -> None:
        pass

    @abstractmethod
    def get_attribute(self) -> Attribute:
        return self.attribute


class ProductA(IProduct):
    """
    Product A.
    """

    def __init__(self, id: int, date: str, attribute: Attribute = None) -> None:
        super(ProductA, self).__init__(id, date, attribute)

    def get_attribute(self) -> Attribute:
        print("[ProductA.get_attribute] {}".format(self.attribute))
        return self.attribute
