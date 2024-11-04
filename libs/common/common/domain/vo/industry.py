from enum import Enum
from typing import Any

from pydantic import RootModel


class TSESector(Enum):
    FISHERY_AGRICULTURE_FORESTRY = "水産・農林業"
    FOODS = "食料品"
    MINING = "鉱業"
    OIL_COAL_PRODUCTS = "石油・石炭製品"
    CONSTRUCTION = "建設業"
    METAL_PRODUCTS = "金属製品"
    GLASS_CERAMICS_PRODUCTS = "ガラス・土石製品"
    TEXTILES_APPARELS = "繊維製品"
    PULP_PAPER = "パルプ・紙"
    CHEMICALS = "化学"
    PHARMACEUTICAL = "医薬品"
    RUBBER_PRODUCTS = "ゴム製品"
    TRANSPORTATION_EQUIPMENT = "輸送用機器"
    IRON_STEEL = "鉄鋼"
    NONFERROUS_METALS = "非鉄金属"
    MACHINERY = "機械"
    ELECTRIC_APPLIANCES = "電気機器"
    PRECISION_INSTRUMENTS = "精密機器"
    OTHER_PRODUCTS = "その他製品"
    INFORMATION_COMMUNICATION = "情報・通信業"
    SERVICES = "サービス業"
    ELECTRIC_POWER_GAS = "電気・ガス業"
    LAND_TRANSPORTATION = "陸運業"
    MARINE_TRANSPORTATION = "海運業"
    AIR_TRANSPORTATION = "空運業"
    WAREHOUSING_HARBOR_TRANSPORTATION = "倉庫・運輸関連"
    WHOLESALE_TRADE = "卸売業"
    RETAIL_TRADE = "小売業"
    BANKS = "銀行業"
    SECURITIES_COMMODITIES_FUTURES = "証券、商品先物取引業"
    INSURANCE = "保険業"
    OTHER_FINANCING_BUSINESS = "その他金融業"
    REAL_ESTATE = "不動産業"


class Industry(RootModel[TSESector]):
    @classmethod
    def from_str(cls, string: Any) -> "Industry | None":
        if not isinstance(string, str):
            raise TypeError("Type of argument should be str")
        for member in TSESector:
            if string == member.value:
                return Industry(member)
        return None
