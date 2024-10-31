import requests

BASE_URL = "http://localhost:8080/v1/claims"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer test",
    "Content-Type": "application/json",
}

# Sample claim data for POST request
claim_data = [
    [
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D0180",
            "quadrant": None,
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1497775530",
            "provider fees": "$100.00",
            "Allowed fees": "$100.00",
            "member coinsurance": "$0.00",
            "member copay": "$0.00",
        },
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D0210",
            "quadrant": None,
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1497775530",
            "provider fees": "$108.00",
            "Allowed fees": "$108.00",
            "member coinsurance": "$0.00",
            "member copay": "$0.00",
        },
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4346",
            "quadrant": None,
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1497775530",
            "provider fees": "$130.00",
            "Allowed fees": "$65.00",
            "member coinsurance": "$16.25",
            "member copay": "$0.00",
        },
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1497775530",
            "provider fees": "$178.00",
            "Allowed fees": "$178.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
    [
        # net fees : 85
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1497775530",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
    [
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730184502",
            "Provider NPI": "1497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new sub
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3732189402",
            "Provider NPI": "1497775530",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
    [
        # invalid provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3730189502",
            "Provider NPI": "1234514",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
    [
        # invalid submitted procedure
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "E4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3732189502",
            "Provider NPI": "1234514",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
    # Additional providers for NPI
    [
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "1730184502",
            "Provider NPI": "2497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "2730184502",
            "Provider NPI": "3497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "4730184502",
            "Provider NPI": "4497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "5730184502",
            "Provider NPI": "5497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "6730184502",
            "Provider NPI": "6497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "7730184502",
            "Provider NPI": "7497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "8730184502",
            "Provider NPI": "8497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "9730184502",
            "Provider NPI": "9497775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
        # new provider
        {
            "service date": "3/28/18 0:00",
            "submitted procedure": "D4211",
            "quadrant": "UR",
            "Plan/Group #": "GRP-1000",
            "Subscriber#": "3830184502",
            "Provider NPI": "1597775531",
            "provider fees": "$550.00",
            "Allowed fees": "$500.00",
            "member coinsurance": "$35.60",
            "member copay": "$0.00",
        },
    ],
]


# Function to POST claims
def post_claims():

    for i, claim in enumerate(claim_data):
        print(f"Processing claim at index: {i}, claim: {claim}")
        response = requests.post(f"{BASE_URL}/", headers=HEADERS, json=claim)
        print("POST /claims/")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        print()


# Function to GET claims list with optional limit
def get_claims_list(limit=100):
    params = {"limit": limit}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    print("GET /claims/")
    print("Status Code:", response.status_code)
    print("Response:", response.json())


# Function to GET specific claim by ID
def get_claim_by_id(claim_id):
    response = requests.get(f"{BASE_URL}/{claim_id}", headers=HEADERS)
    print(f"GET /claims/{claim_id}")
    print("Status Code:", response.status_code)
    print("Response:", response.json())


# Function to GET top providers by net fees
def get_top_providers():
    response = requests.get(f"{BASE_URL}/top-providers/", headers=HEADERS)
    print("GET /claims/top-providers/")
    print("Status Code:", response.status_code)
    print("Response:", response.json())


# Run all tests
if __name__ == "__main__":
    print("Testing API Endpoints...\n")

    # Post sample claims
    post_claims()
    print("\n")

    # Get list of claims
    get_claims_list()
    print("\n")

    # Get specific claim by ID
    get_claim_by_id(1)
    print("\n")

    # Get top providers by net fees
    get_top_providers()
    print("\n")
