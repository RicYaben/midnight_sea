# BLUEPRINTS

## CONFIGURATIONS

Here you can find the types of data formats the application accepts.
Each of these configurations works similarly, with different levels of
complexity.

### SIMPLE

The structure contains a list of `data point` objects with a name and a set of cascading instructions. The instructions indicate how to find the element containing the value for the data point. Each instruction is defined by the properties key (`props`) and the attributes key (`attrs`). The properties points to elements with similar characteristics, and if set, a `limit` of elements that we want to find (any amount by default). The attributes, if set, indicate from where are we extracting the information.

For example:

```yaml
scraper: simple # Type of scraper to use
struct:                                 # Structure
  - name: Title                       # Data Point (name)
    instructions:                   # Instructions
      - props:                        # Properties
            name: div
            attrs:
                href: /profile/view/
            limit: 1
            attrs:                      # Attributes
              - text
        clean:  (?=\/profile\/view\/)   # Cleaning regex
        many: true                      # This is a list of items
```

### GROUPS

The structure divides the data points in groups or clusters of similar content.
For example, there might be multiple `comments` on a single page each with their own fields. Therefore, we want to group them and create lists of similar items.

```yaml
scraper: groups
struct:
  - name: Comments                # Group Name
    many: true
    fields:                       # Group Fields
      - name: user
        instructions:
          - props:
              attrs:
                  class: username
              limit: 1
              attrs:
                - text

      - name: tags
        many: true
        clean: \w+$
        instructions:
          - props:
            attrs:
                href: /profile/view/
            attrs:
                - text
```

This will yield an object similar to the following.

```json
{
  "comments": [
    // Group
    {
      "user": "some user", // "user" Field
      "tags": ["tag1", "tag2"] // "tags" Field
    }
  ]
}
```
