from typing import List, Optional

from pydantic import BaseModel


class Warehouse(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    quantity: Optional[str] = '0'


class Product(BaseModel):
    id: Optional[int] = 0
    header: Optional[str] = None
    articul: Optional[str] = None
    code: Optional[str] = None
    body: Optional[str] = None
    price: Optional[float] = 0
    old_price: Optional[float] = 0
    storqnt: Optional[int] = 0
    code1c: Optional[str] = None
    warehouses: Optional[List[Warehouse]] = None
    brend: Optional[str] = None
