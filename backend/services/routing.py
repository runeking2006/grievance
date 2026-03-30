def route(category: str) -> str:
    mapping = {
        "Hostel": "Hostel Office",
        "Fees": "Accounts",
        "IT": "IT Support",
        "General": "Admin",
    }
    return mapping.get(category, "Admin")
