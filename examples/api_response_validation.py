"""
Example usage of type-enforcer for validating complex API responses,
such as one from the DexScreener API.
"""

from typing import Any, TypedDict

from type_enforcer import ValidationError, enforce

# ===== Type Definitions for DexScreener API Response Validation =====
# These TypedDicts define the expected structure and types of the API response.
# Using TypedDict allows for precise validation of dictionary structures.


class TokenDict(TypedDict):
    address: str
    name: str
    symbol: str


class TransactionsDict(TypedDict, total=False):
    buys: int
    sells: int


class TxnsPeriodsDict(TypedDict, total=False):
    m5: TransactionsDict
    h1: TransactionsDict
    h6: TransactionsDict
    h24: TransactionsDict


class VolumeDict(TypedDict, total=False):
    h24: float
    h6: float
    h1: float
    m5: float


class PriceChangeDict(TypedDict, total=False):
    m5: float
    h1: float
    h6: float
    h24: float


class LiquidityDict(TypedDict, total=False):
    usd: float | None  # Field can be present but None
    base: float
    quote: float


class WebsiteDict(TypedDict):
    label: str
    url: str


class SocialDict(TypedDict, total=False):
    type: str
    url: str
    label: str | None


class InfoDict(TypedDict, total=False):
    imageUrl: str | None
    websites: list[WebsiteDict] | None
    socials: list[SocialDict] | None
    header: str | None
    openGraph: str | None


class BoostsDict(TypedDict, total=False):
    active: int | None


class PairDict(TypedDict, total=False):
    chainId: str
    dexId: str
    url: str
    pairAddress: str
    baseToken: TokenDict
    quoteToken: TokenDict
    priceNative: str
    priceUsd: str | None
    txns: TxnsPeriodsDict
    volume: VolumeDict
    priceChange: PriceChangeDict | None
    liquidity: LiquidityDict | None
    fdv: float | None
    marketCap: float | None
    pairCreatedAt: int | None
    info: InfoDict | None
    boosts: BoostsDict | None
    labels: list[str] | None
    moonshot: dict[str, Any] | None


class DexScreenerResponseDict(TypedDict):
    schemaVersion: str
    pairs: list[PairDict] | None
    pair: PairDict | None


# ===== Example Usage =====

# Example raw JSON data (simulating an API response)
# This one is mostly valid according to DexScreenerResponseDict
valid_api_response_data = {
    "schemaVersion": "1.0.0",
    "pairs": [
        {
            "chainId": "ethereum",
            "dexId": "uniswap",
            "url": "https://dexscreener.com/ethereum/0x123...",
            "pairAddress": "0x123...",
            "baseToken": {
                "address": "0xabc...",
                "name": "Example Token",
                "symbol": "EXT",
            },
            "quoteToken": {
                "address": "0xc0ffee...",
                "name": "Wrapped Ether",
                "symbol": "WETH",
            },
            "priceNative": "1500.5",
            "priceUsd": "3000000",
            "txns": {
                "m5": {"buys": 10, "sells": 5},
                "h1": {"buys": 100, "sells": 50},
            },
            "volume": {"h24": 1000000.0, "h6": 250000.0},
            "priceChange": {"m5": 0.1, "h1": 1.5},
            "liquidity": {"usd": 5000000.0, "base": 1666.6, "quote": 2500000.0},
            "fdv": 300000000.0,
            "pairCreatedAt": 1609459200000,
            "info": {
                "imageUrl": "https://example.com/token.png",
                "websites": [{"label": "Homepage", "url": "https://example.com"}],
                "socials": [{"type": "twitter", "url": "https://twitter.com/example"}],
            },
            # Missing optional fields are okay (e.g., marketCap, boosts, labels)
        }
    ],
    # Missing 'pair' is okay as it's optional
}

# Example invalid data (e.g., wrong type for a required field)
invalid_api_response_data = {
    "schemaVersion": "1.0.0",
    "pairs": [
        {
            "chainId": "ethereum",
            "dexId": "uniswap",
            "url": "https://dexscreener.com/ethereum/0x123...",
            "pairAddress": "0x123...",
            "baseToken": {
                "address": "0xabc...",
                "name": "Example Token",
                "symbol": 123,  # <--- INVALID: symbol should be str
            },
            "quoteToken": {
                "address": "0xc0ffee...",
                "name": "Wrapped Ether",
                "symbol": "WETH",
            },
            "priceNative": "1500.5",
        }
    ],
}

print("Validating DexScreener API response structure...")

try:
    # Use enforce to validate the raw dictionary against the TypedDict
    validated_data = enforce(valid_api_response_data, DexScreenerResponseDict)
    print("Valid data structure conforms to DexScreenerResponseDict.")

    # You can now safely access elements knowing they match the expected types
    if validated_data["pairs"] and validated_data["pairs"][0]["baseToken"]:
        print(f"Validated Base Token Symbol: {validated_data['pairs'][0]['baseToken']['symbol']}")
    if validated_data["pairs"] and validated_data["pairs"][0]["liquidity"]:
        print(f"Validated Liquidity (USD): {validated_data['pairs'][0]['liquidity'].get('usd')}")

except ValidationError as e:
    print(f"ERROR validating valid data: {e}")

print("\n---")

print("Attempting to validate invalid data structure...")
try:
    validated_data = enforce(invalid_api_response_data, DexScreenerResponseDict)
    print("ERROR: Invalid data was incorrectly validated!")
except ValidationError as e:
    print("SUCCESS: Correctly caught validation error in invalid data:")
    print(f"  {e}")
    # Example Error: pairs[0].baseToken.symbol: Expected str, got int

print("\n---")

# Example: Validating a sub-structure (e.g., just the TokenDict)
valid_token_data = {"address": "0x111...", "name": "Sub Token", "symbol": "SUB"}
invalid_token_data = {"address": "0x222...", "name": 123, "symbol": "SUB"}  # name is int

print("Validating sub-structure (TokenDict)...")
try:
    validated_token = enforce(valid_token_data, TokenDict)
    print(f"Validated Token: {validated_token}")
except ValidationError as e:
    print(f"ERROR validating valid token: {e}")

try:
    enforce(invalid_token_data, TokenDict)
    print("ERROR: Invalid token was incorrectly validated!")
except ValidationError as e:
    print("SUCCESS: Correctly caught validation error in invalid token:")
    print(f"  {e}")
    # Example Error: name: Expected str, got int
