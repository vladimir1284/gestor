from openapi_client import CatalogApi
import xml.etree.ElementTree as et
from datetime import datetime, timezone
from killbill.tools.get_leases import get_leases

VALID_PERIODS = [
    "DAILY",
    "WEEKLY",
    "BIWEEKLY",
    "THIRTY_DAYS",
    "MONTHLY",
    "QUARTERLY",
    "BIANNUAL",
    "ANNUAL",
    "BIENNIAL",
    "NO_BILLING_PERIOD",
]


def get_period(p: str):
    pu = p.upper()
    if pu in VALID_PERIODS:
        return pu

    return "MONTHLY"


def get_effective_date():
    date = datetime.now(timezone.utc).replace(microsecond=0)
    return date.isoformat()


def push_phase(
    plan: et.Element,
    period: str = "MONTHLY",
    amount: str = "100.00",
    currency: str = "USD",
):
    et.SubElement(plan, "initialPhases").text = " "

    phase = et.SubElement(plan, "finalPhase")
    phase.attrib["type"] = "EVERGREEN"

    duration = et.SubElement(phase, "duration")
    et.SubElement(duration, "unit").text = "UNLIMITED"

    recurring = et.SubElement(phase, "recurring")

    et.SubElement(recurring, "billingPeriod").text = period

    rec_prices = et.SubElement(recurring, "recurringPrice")
    price = et.SubElement(rec_prices, "price")
    et.SubElement(price, "currency").text = currency
    et.SubElement(price, "value").text = amount


def push_plan(
    plans: et.Element,
    pricePlans: et.Element,
    period: str = "MONTHLY",
    amount: str = "100.00",
    currency: str = "USD",
    product: str = "Standard",
):
    # Plan name
    price_name = amount.replace(".", "-")
    plan_name = f"{product}-{period}-{price_name}".lower()

    # Add plan to price list
    et.SubElement(pricePlans, "plan").text = plan_name

    # plan root element with plan name
    plan = et.SubElement(plans, "plan")
    plan.attrib["name"] = plan_name

    # add plan product
    et.SubElement(plan, "product").text = product

    # push phases
    push_phase(plan, period, amount, currency)


def push_rule(rules: et.Element, type: str, policy: str = "IMMEDIATE"):
    policy_element = et.SubElement(rules, f"{type}Policy")
    policy_case = et.SubElement(policy_element, f"{type}PolicyCase")
    et.SubElement(policy_case, "policy").text = policy


def push_product(products: et.Element, name: str, category: str = "BASE"):
    product = et.SubElement(products, "product")
    product.attrib["name"] = name
    et.SubElement(product, "category").text = category


def generate_catalog(product_name: str = "TrailerRent", currency: str = "USD"):
    # Catalog element (root)
    catalog = et.Element("catalog")
    catalog.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    catalog.attrib["xsi:noNamespaceSchemaLocation"] = "CatalogSchema.xsd"

    # Global elements
    # - effective date
    # - catalog name
    # - recurring billing mode
    et.SubElement(catalog, "effectiveDate").text = get_effective_date()
    et.SubElement(catalog, "catalogName").text = f"{product_name}Catalog"
    et.SubElement(catalog, "recurringBillingMode").text = "IN_ADVANCE"

    # Currency
    currencies = et.SubElement(catalog, "currencies")
    et.SubElement(currencies, "currency").text = currency

    # Products
    products = et.SubElement(catalog, "products")
    push_product(products, product_name)

    # Rules
    rules = et.SubElement(catalog, "rules")
    push_rule(rules, "change")
    push_rule(rules, "cancel")

    # Plans
    plans = et.SubElement(catalog, "plans")

    # Price lists
    priceLists = et.SubElement(catalog, "priceLists")
    defaultPriceList = et.SubElement(priceLists, "defaultPriceList")
    defaultPriceList.attrib["name"] = "DEFAULT"
    pricePlans = et.SubElement(defaultPriceList, "plans")

    # leases = Lease.objects.all()
    leases = get_leases()
    processed = []

    # get period-price map
    for lease in leases:
        period = get_period(lease.payment_frequency)
        price = "{:.2f}".format(lease.payment_amount)
        pp = f"{period}-{price}"
        if pp not in processed:
            processed.append(pp)
            push_plan(
                plans,
                pricePlans,
                period=period,
                amount=price,
                product=product_name,
            )

    # Get xml and return it
    return '<?xml version="1.0" encoding="UTF-8"?>' + et.tostring(
        catalog, encoding="unicode"
    )


def sync_catalog(catalog_api: CatalogApi):
    catalog = generate_catalog()
    catalog_api.upload_catalog_xml(
        "admin",
        catalog,
    )
