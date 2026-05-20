from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    COMPANY_OVERVIEW = "company_overview"
    PRODUCTS = "products"
    BRANDS = "brands"
    SERVICES = "services"
    DELIVERY = "delivery"
    PRICE = "price"
    STOCK = "stock"
    PROMOTIONS = "promotions"
    VACANCIES = "vacancies"
    INTERNAL_PROMPT = "internal_prompt"
    UNKNOWN_PRODUCT = "unknown_product"
    GENERAL_RAG = "general_rag"
