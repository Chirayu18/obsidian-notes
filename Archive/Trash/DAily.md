---
date: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.date.now("dddd MMMM Do YYYY") %>

## TODO

### HToWW Analysis
```dataview
TASK
FROM "Projects/HToWW"
WHERE !completed AND file.frontmatter.status = "active"
GROUP BY file.link
```

### EPR Task 1
```dataview
TASK
FROM #active AND "Projects/EPR-Task-1"
WHERE !completed
```

### EPR Task 2
```dataview
TASK
FROM #active AND "Projects/EPR-Task-2"
WHERE !completed
```

### Other
```dataview
TASK
FROM #active AND -"Projects"
WHERE !completed
```

## Log
- 

## Notes
- 

## Bugs / Issues