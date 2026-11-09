# Remove the retired v1 pricing API

We no longer support the v1 pricing API, and nothing calls it anymore. Remove it:

- Delete `/app/shop/legacy_pricing.py`.
- Delete its tests, `/app/tests/test_legacy_pricing.py`.
- Remove `legacy_total` from `/app/shop/__init__.py`, so no code refers to the v1 API.

Keep everything else as it is. `/app/tests/test_pricing.py` must stay unchanged and
keep passing when you run `python3 -m pytest /app/tests` from `/app`.
