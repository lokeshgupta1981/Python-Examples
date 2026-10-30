"""The fixed category list for a small business account."""

CATEGORIES = {
    "Office supplies": "stationery, printing, postage and small office equipment",
    "Software": "software subscriptions, apps, cloud services and domains",
    "Travel": "trains, taxis, fuel, parking and hotels for business trips",
    "Meals": "coffee, meals and catering for staff or clients",
    "Utilities": "electricity, water, gas, broadband and phone bills",
    "Rent": "rent for the office or a workspace",
    "Payroll": "salary and wage payments to employees",
    "Bank fees": "account fees, payment fees and interest charged by the bank",
    "Taxes": "payments to HMRC such as VAT, PAYE and corporation tax",
    "Sales income": "money from customers for our invoices or card sales",
    "Refunds": "money we return to a customer, or a supplier returns to us",
    "Other": "anything else, or rows without enough information "
             "(cash, cheques, transfers between our own accounts)",
}

# Categories that only make sense for one direction of money
MONEY_IN_ONLY = {"Sales income"}
MONEY_OUT_ONLY = {
    "Office supplies", "Software", "Travel", "Meals", "Utilities",
    "Rent", "Payroll", "Bank fees", "Taxes",
}
