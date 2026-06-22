---
tags:
  - completed
date: <% tp.date.now("YYYY-MM-DD") %>
---
---

## TODO

### HToWW Analysis


- [ ] Take CERN security course: https://cern.ch/computersecuritycourse
> [!important]
> ```dataview
>TASK
>FROM "Projects/HToWW" AND #meeting
>WHERE !completed AND file.frontmatter.status = "active"
>GROUP BY file.link
>```

> [!todo]
> ```dataview
>TASK
>FROM "Projects/HToWW" AND -#meeting
>WHERE !completed AND file.frontmatter.status = "active"
>GROUP BY file.link
>```

#### Alpaka
> [!important]
> ```dataview
>TASK
>FROM "Projects/Alpaka" AND #meeting
>WHERE !completed AND file.frontmatter.status = "active"
>GROUP BY file.link
>```

> [!todo]
> ```dataview
>TASK
>FROM "Projects/Alpaka" AND -#meeting
>WHERE !completed AND file.frontmatter.status = "active"
>GROUP BY file.link
>```
## Log

-
