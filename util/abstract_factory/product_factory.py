from abc import ABC, abstractmethod

from .product import Attribute, IProduct, ProductA


class IProductFactory(ABC):
    """
    Interface of product factory.
    """

    @abstractmethod
    def create(self, id: int, date: str, attribute: Attribute) -> IProduct:
        pass


class ProductAFactory(IProductFactory):
    """
    Product A factory.

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

    def create(self, id: int, date: str, attribute: Attribute) -> IProduct:
        return ProductA(id, date, attribute)
