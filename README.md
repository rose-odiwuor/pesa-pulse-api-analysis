# Pesa Pulse: Where Are Our Customers?

Pesa Pulse, a Nairobi fintech start-up, has a new partner who shares a customer directory through an API. Before marketing plans regional campaigns, they want to know how many customers there are, where they are, and what the data looks like. This project pulls the data, explores its nested structure, answers "where are our customers?" first with plain Python structures and then with pandas, and produces charts marketing can use in a slide.

## Project structure

```
day1-api-analysis/
├── analysis.py
├── output/
│   ├── customers.csv
│   ├── city_counts.csv
│   ├── customer_distribution.png
│   └── email_tld_distribution.png
├── pyproject.toml
├── uv.lock
├── requirements.txt
└── README.md
```

## How to run

## How to run

This project uses [uv] to manage the environment.

1. Install uv if you don't have it .
2. From the project folder, install the dependencies. uv creates the virtual environment automatically:
   ```
   uv sync
   ```
3. Run the analysis:
   ```
   uv run analysis.py
   ```
4. The console shows each step's results. The CSVs and charts are saved to the `output/` folder, which is created automatically.

If you don't use uv, `requirements.txt` is included. Create a virtual environment and run `pip install -r requirements.txt`, then `python analysis.py`.

An internet connection is needed because the data comes from `https://jsonplaceholder.typicode.com/users`.

## Approach

| Task | Function | What it does |
|------|----------|--------------|
| 1 | `get_customers(url)` | Calls the API with `requests` and a 10-second timeout, uses `raise_for_status()` to catch bad status codes, and returns the parsed list. Any network failure prints a clear message and returns an empty list instead of a traceback. |
| 2 | `explore(record, indent)` | Recursively walks one customer record and prints every key with its Python type, indented by depth. |
| 3 | `extract_attributes(customers)` | Returns one flat dict per customer: id, name, username, email, email domain, phone, city, zipcode, latitude, longitude, company and website. Latitude and longitude are converted from strings to floats. |
| 4 | `unique_cities(customers)` | Uses a set comprehension to find distinct cities. |
| 5 | `city_counts(customers)` and `email_domain_counts(customers)` | City counts use a plain loop with a dictionary (no `Counter`, no pandas). Email counts use a dict comprehension over a list of top-level domains. |
| 6 | `to_dataframe(rows)` | Converts the flat rows into a DataFrame. The script prints the shape and `dtypes`, and checks that `value_counts()` matches the hand-written counts. |
| 7 | (in `__main__`) | Writes `customers.csv` and `city_counts.csv` without the pandas index. |
| 8 | `plot_distribution(counts, path, title)` | Saves a horizontal bar chart with the most common category at the top and whole-number axis ticks. It is used for both the city chart and the email TLD chart. |

## Task 2: the nested structure

Each customer record has two kinds of attribute.

**Flat attributes** (reached directly): `id`, `name`, `username`, `email`, `phone`, `website`.

**Nested attributes:**

- `address` is a dictionary containing `street`, `suite`, `city`, `zipcode` and a further nested dictionary, `geo`.
- `geo` is a dictionary containing `lat` and `lng`.
- `company` is a dictionary containing `name`, `catchPhrase` and `bs`.

The deepest values are the coordinates, three levels down. To reach them from a customer record:

```python
customer["address"]["geo"]["lat"]   # latitude, returned as a string
customer["address"]["geo"]["lng"]   # longitude, returned as a string
```

The API returns the coordinates as strings, so `extract_attributes` converts them with `float()`.

## Findings

The numbers below are for the 10 customers the API returns. Check them against your own console output when you run the script.

1. **City is too granular to plan campaigns around.** There are 10 customers and 10 unique cities, so every customer is in a different city. Marketing cannot target a "biggest city", and campaigns would need a coarser grouping, such as region or country, which this data does not contain.
2. **Email top-level domains are the more useful grouping.** `.biz` appears three times, more than any other TLD. The others (`.tv`, `.net`, `.org`, `.ca`, `.info`, `.me`, `.io`) appear once each.
3. **The hand-written counts and pandas agree.** The loop and dict-comprehension counts match `value_counts()` exactly, which confirms the hand-written logic is correct.

## Which chart is more useful?

The **email TLD chart** is more useful. The city chart is flat, with every bar at 1, so it shows no pattern and gives marketing nothing to act on. The TLD chart has variation (`.biz` clearly leads), so it shows a real distribution that marketing could use to segment customers, for example by business versus personal email.

## Assumptions and notes

- **Email "domain" versus TLD:** the `email_domain` column in `customers.csv` holds the full domain (for example `april.biz`), as the task asks. The counts and the second chart use only the top-level part (`biz`), as the starter docstring specifies. Full domains are all unique here, so counting them would not show anything.
- **Case:** email domains are lower-cased before counting so that `Biz` and `biz` are treated as the same.
- **Data source:** JSONPlaceholder is a mock API with 10 fixed records, so the findings illustrate the method and are not real customer insight.
- **Failure handling:** if the API call fails, the script prints a message and stops cleanly. It does not write empty outputs.
- **City counts CSV:** it is sorted by count (descending) and then city name (ascending) so the order is stable.