# single-line comment using the hash character
total = 2 + 3    # inline comment after the code
print('total', '=', repr(total))

"""
Triple-quoted text is a string, not a comment.
Python evaluates it and throws it away.
"""
print(total)

# Retry three times because the payment API drops the first call
retries = 3   # set to 0 in tests
print('retries', '=', repr(retries))
url = "https://example.com/#top"   # this # inside the string is not a comment
print('url', '=', repr(url))

# The cache keeps prices for 10 minutes.
# Longer times showed stale prices after a sale started,
# shorter times overloaded the pricing service.
CACHE_SECONDS = 600

def price_with_tax(price):
    """Return the price including 18% tax."""
    return round(price * 1.18, 2)

doc = price_with_tax.__doc__     # 'Return the price including 18% tax.'
print('doc', '=', repr(doc))

page = 0

# Bad: repeats the code
page = page + 1   # add 1 to page
print('page', '=', repr(page))

# Good: explains a decision
page = 1          # the orders API numbers pages from 1, not 0
print('page', '=', repr(page))
