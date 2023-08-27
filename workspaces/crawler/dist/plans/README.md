# PLANS

The plans structure is given by 2 sections:

- meta
- models

## META

It contains information about the market

```yaml
meta:
  domain: http://somemarketABC.i2p
  market: somemarket
```

## MODELS

It contains information about each model to crawl, instructions on "how to crawl", important pages to crawl, and validators.
It may also include a sub-model called `all`, which will be used for generic purposes.

For example:

```yaml
models:
  all:                      # General model
    validators:             # Validators
      invalid:              # Invalid elements
        - name: captcha     # (should not be found)
          instructions:
            - props:
              ...

  category:
    validators:
      required:             # Reqiored validator
        - &listing          # (must be found)
          name: listing
          many: true
          instructions:
            - props:
              ...

    elements:                # Guide to some elements
      - <<: *listing
      - name: next_page
        instructions:
          - props:
            ...

    pages:                    # Important pages
      - name: first
        url: "?category=1"

```
