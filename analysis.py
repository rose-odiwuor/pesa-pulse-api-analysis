"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics
"""

from pathlib import Path
import os
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing."""
    try:
        response = requests.get(url,timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Error fetching customers: {error}")
        return []


def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    pad = "     " * indent
    if isinstance(record, dict):
        for key, value in record.items():
            print(f"{pad}{key}: {type(value).__name__}") 
            explore(value, indent + 1)
    elif isinstance(record, list):
        for i, item in enumerate(record):
            if isinstance(item, (dict, list)):
                print(f"{pad}{i}: {type(item).__name__}")
                explore(item, indent + 1)


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    extracted_customers = []

    for item in customers:
        row = {
            "id": item["id"], 
            "name": item["name"],
            "username": item["username"],
            "email": item["email"],
            "email_domain": item["email"].split("@")[1].lower(),
            "phone": item["phone"],
            "city": item["address"]["city"],
            "zipcode": item["address"]["zipcode"],
            "latitude": float(item["address"]["geo"]["lat"]),
            "longitude": float(item["address"]["geo"]["lng"]),
            "company": item["company"]["name"],
            "website": item["website"]
            }
        extracted_customers.append(row)
    return extracted_customers


def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {customer["address"]["city"] for customer in customers}


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts = {}

    for customer in customers:
        city = customer["address"]["city"]
        if city in counts:
            counts[city] += 1
        else:
            counts[city] = 1
    return counts


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain (e.g. 'biz', 'tv')."""
    tlds = [customer["email"].split("@")[1].lower().split(".")[-1] for customer in customers]

    return {tld: tlds.count(tld) for tld in set(tlds)}


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert a list of dictionaries into a pandas DataFrame."""
    return pd.DataFrame(rows)


def plot_distribution(counts: dict[str, int], path: str, title: str = "Customer distribution") -> None:
    """Save a horizontal bar chart of counts, most common at the top."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    items = sorted(counts.items(), key=lambda item: (item[1], item[0]))  # smallest first, so largest ends up on top
    labels = [name for name, _ in items]
    values = [n for _, n in items]

    fig, ax = plt.subplots(figsize=(8, max(3, 0.4 * len(labels))))
    ax.barh(labels, values)
    ax.set_title(title)
    ax.set_xlabel("Number of customers")
    ax.set_xticks(range(0, max(values) + 1))   # whole numbers only
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)             # free memory, avoids charts piling up


if __name__ == "__main__":

    # Fetch the API data
    customers = get_customers()

    if not customers:
        print("Analysis stopped: No customer data was retrieved")

    else:
        # Create the output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Explore the first customer's nested structure
        print("\n--- Exploring the first customer ---")
        explore(customers[0])

        # Extract selected attributes
        extracted_customers = extract_attributes(customers)

        print("\n--- First extracted customer ---")
        print(extracted_customers[0])

        # Find unique cities
        cities = unique_cities(customers)

        print("\n--- Unique cities ---")
        print(f"Unique cities: {cities}")
        print(f"Number of unique cities: {len(cities)}")
        print(f"Number of customers: {len(customers)}")

        # Count customers by city
        city_result = city_counts(customers)

        print("\n Customers by city (most to least common): ")
        for city, count in sorted(city_result.items(), key=lambda item: item[1], reverse=True):
            print(f"{city}: {count}")

        # Count customers by email domain
        domain_result = email_domain_counts(customers)

        print("\nCustomers by email domain (most to least common): ")
        for domain, count in sorted(domain_result.items(), key=lambda item: item[1], reverse=True):
            print(f"{domain}: {count}")

        # Convert extracted records into a DataFrame
        df = to_dataframe(extracted_customers)

        print(f"\nDataFrame: {df}")
        print(f"\nDataFrame shape: {df.shape}")
        print(f"\nData types: {df.dtypes}")

        # Validate manual counts against pandas
        pandas_city_counts = df["city"].value_counts().to_dict()
        print(f"\nCity counts from pandas: {pandas_city_counts}")
        print(f"\nDo manual & pandas city counts agree? {pandas_city_counts == city_result}")

        pandas_domain_counts = df["email_domain"].str.split(".").str[-1].value_counts().to_dict()
        print(f"\nTLD counts from pandas: {pandas_domain_counts}")
        print(f"\nDo manual & pandas TLD counts agree? {pandas_domain_counts == domain_result}")

        # Export customer records to CSV
        df.to_csv(output_dir / "customers.csv", index=False)

        # Export city counts to CSV
        city_df = (
            df.groupby("city")
            .size()
            .reset_index(name="count")
            .sort_values(["count", "city"], ascending=[False, True])
        )
        city_df.to_csv(output_dir / "city_counts.csv", index=False)

        # Chart 1: customers by city
        plot_distribution(city_result, output_dir / "customer_distribution.png", "Customers by city")
        
        # Chart 2: customers by email tld
        plot_distribution(domain_result, output_dir / "email_tld_distribution.png", "Customers by email TLD")