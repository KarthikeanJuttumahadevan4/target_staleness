# Sample File: test.txt Template

This file is a **template** for creating `test.txt`. Copy the content below and save it as `samples/test.txt`.

---

## Create This File

Run this command to create the actual test.txt:

```bash
cat > samples/test.txt << 'ENDOFFILE'
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
## Introduction
Added introduction section.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify -->
## Revised Introduction
Updated the introduction with more details.
ENDOFFILE
```

---

## File Content (for manual creation)

```
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
# Report
Initial content.

<!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
## Introduction
Added introduction section.

<!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify -->
## Revised Introduction
Updated the introduction with more details.
```

---

## What It Tests

| Aspect | Value |
|--------|-------|
| Number of edits | 3 |
| Number of authors | 2 (alice, bob) |
| Number of edit types | 3 (create, add, modify) |
| Expected nodes | 3 |
| Expected edges | 2 |
| Expected confidence | All high |
| Expected source | embedded_marker |

---

## Expected Knowledge Graph

```
NODES:
  edit_20240202T203100Z_0: create by alice at 2024-02-02T20:31:00Z
  edit_20240203T192900Z_0: add by bob at 2024-02-03T19:29:00Z
  edit_20240204T101500Z_0: modify by alice at 2024-02-04T10:15:00Z

EDGES:
  edit_20240202T203100Z_0 -> edit_20240203T192900Z_0 (adds_to)
  edit_20240203T192900Z_0 -> edit_20240204T101500Z_0 (adds_to)
```

---

## What to Do With This File

1. **Create the actual file**:
   ```bash
   # Navigate to prototype directory
   cd /home/karthikean.juttumaha/mini-extract/prototype
   
   # Create samples directory if it doesn't exist
   mkdir -p samples
   
   # Create the file using the command above
   cat > samples/test.txt << 'ENDOFFILE'
   <!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
   # Report
   Initial content.
   
   <!-- EDIT: 2024-02-03T19:29:00Z | AUTHOR: bob | TYPE: add -->
   ## Introduction
   Added introduction section.
   
   <!-- EDIT: 2024-02-04T10:15:00Z | AUTHOR: alice | TYPE: modify -->
   ## Revised Introduction
   Updated the introduction with more details.
   ENDOFFILE
   ```

2. **Verify it was created**:
   ```bash
   cat samples/test.txt
   ```

3. **Run the extractor**:
   ```bash
   python3 extract.py samples/test.txt --output results/test.txt.json
   ```

4. **Check results**:
   ```bash
   cat results/test.txt.json | python3 -m json.tool
   ```

---

## Marker Syntax Reference

| Field | Format | Example | Required |
|-------|--------|---------|----------|
| EDIT prefix | `<!-- EDIT:` | `<!-- EDIT:` | Yes |
| Timestamp | ISO 8601 | `2024-02-02T20:31:00Z` | Yes |
| AUTHOR | Any string (no pipes) | `alice` or `Alice User` or `NONE` | Yes |
| TYPE | create/add/modify/delete | `create` | Yes |
| SECTION | Any string (optional) | `section:header` | No |
| Suffix | ` -->` | ` -->` | Yes |

**Example minimum marker:**
```
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create -->
```

**Example full marker:**
```
<!-- EDIT: 2024-02-02T20:31:00Z | AUTHOR: alice | TYPE: create | SECTION: header -->
```

---

## Notes

1. **Timestamps must be in ISO 8601 format**: `YYYY-MM-DDTHH:MM:SSZ`
2. **AUTHOR can be NONE**: Use `NONE` or `none` if no author
3. **TYPE must be lowercase**: `create`, `add`, `modify`, `delete`
4. **Markers must be at the start of a line** (no indentation)
5. **Content after marker is assigned to that edit**
6. **Content before next marker belongs to current edit**
