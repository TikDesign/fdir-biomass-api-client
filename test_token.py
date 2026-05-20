"""
test_token.py
Tester kun at Maskinporten-token hentes korrekt.
Kjør: python test_token.py
"""
from modules.maskinporten import get_access_token

print("Henter token fra Maskinporten testmiljø...")
try:
    token = get_access_token()
    print(f"\nSUKSESS! Token hentet.")
    print(f"Token (første 80 tegn): {token[:80]}...")
except Exception as e:
    print(f"\nFEIL: {e}")