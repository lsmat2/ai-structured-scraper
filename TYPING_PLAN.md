# Type Annotation Implementation Plan

**Goal:** Add complete type annotations to all Python files to eliminate Pylance errors

**Estimated Time:** 4-5 hours
**Files to Modify:** 5 files (ai_data_cleaner.py, backend_CLI.py, clean_nearby_places.py, fetch_nearby_places.py, BackendClient.py)

---

## File 1: ai_data_cleaner.py

### Import Additions Needed
```python
from typing import Optional, cast, Tuple, List, Dict, Any
```

### Variables and Functions Requiring Type Annotations

| Line | Current | Type Needed | Notes |
|------|---------|-------------|-------|
| 26 | `def __init__(self, api_key=None)` | `api_key: Optional[str] = None` | |
| 31 | `self.api_key` | `self.api_key: Optional[str]` | Instance variable |
| 32 | `self.client` | `self.client: OpenAI` | Instance variable |
| 33 | `self.OUTPUT_DIR` | `self.OUTPUT_DIR: str` | Instance variable |
| 36 | `self.schema_description` | `self.schema_description: str` | Instance variable |
| 38 | `-> dict` | `-> Dict[str, Any]` | Return type |
| 47 | `def _is_same_domain(self, link_url, root_url)` | `link_url: str, root_url: str) -> bool` | |
| 51 | `link_domain` | `link_domain: str` | Local variable |
| 52 | `root_domain` | `root_domain: str` | Local variable |
| 56 | `def _fetch_page_content(self, url)` | `url: str) -> Tuple[str, List[str]]` | |
| 59 | `response` | Already typed by requests | |
| 61 | `soup` | `soup: BeautifulSoup` | Local variable |
| 64 | `text_elements` | Already inferred | |
| 65 | `text` | `text: str` | Local variable |
| 68 | `subpage_links` | `subpage_links: List[str]` | Local variable |
| 70 | `href` | `href: str` | Local variable |
| 74 | `full_url` | `full_url: str` | Local variable |
| 84 | `def _collect_site_content(self, root_url, max_pages=10)` | `root_url: str, max_pages: int = 10) -> str` | |
| 87 | `visited` | `visited: set[str]` | Local variable |
| 88 | `to_visit` | `to_visit: List[str]` | Local variable |
| 89 | `all_content` | `all_content: List[str]` | Local variable |
| 92 | `current_url` | `current_url: str` | Local variable |
| 99 | `text, new_links` | Already typed by return | |
| 111 | `-> dict[str]` | `-> PlaceDataExtraction` | Wrong return type |
| 131 | `input_tokens` | `input_tokens: int` | Local variable |
| 132 | `output_tokens` | `output_tokens: int` | Local variable |
| 133 | `total_tokens` | `total_tokens: int` | Local variable |
| 145 | `def _write_to_output_file(self, content:str, subdirectory:Optional[str], filename:str)` | Add `-> None` | |
| 152 | `full_path` | `full_path: str` | Local variable |
| 158 | `data` | `data: Any` | Local variable (JSON) |
| 170 | `def process_url(self, place_data:dict, output_filename:str, verbose:bool=False)` | `place_data: Dict[str, Any]` and add `-> None` | |
| 172 | `website_url` | `website_url: Optional[str]` | Local variable |
| 177 | `scraped_website_content:str` | Already typed | |
| 184 | `structured_place_data_dict` | `structured_place_data_dict: Dict[str, Any]` | Local variable |
| 189 | `value` | `value: Any` | Local variable |
| 197 | `place_id` | `place_id: Optional[Any]` | Local variable |
| 201 | `structured_place_data_json` | `structured_place_data_json: str` | Local variable |
| 214 | `filename` | `filename: str` | Local variable |
| 215 | `filename_removed_suffix` | `filename_removed_suffix: str` | Local variable |
| 216 | `ai_cleaned_filename` | `ai_cleaned_filename: str` | Local variable |
| 220 | `def clean_place_data(self, place_data_filepath: str, verbose:bool = True)` | Add `-> None` | |
| 226 | `new_filename` | `new_filename: str` | Local variable |

**Total Annotations:** ~35

---

## File 2: backend_CLI.py

### Import Additions Needed
```python
from typing import Optional, List, Dict, Any, Union
```

### Variables and Functions Requiring Type Annotations

| Line | Current | Type Needed | Notes |
|------|---------|-------------|-------|
| 13 | `backendClient` | `backendClient: BackendClient` | Module-level variable |
| 53 | `def _process_place_interactive(place_id:int)` | Add `-> None` | Already has param type |
| 57 | `place_response` | `place_response: requests.Response` | Local variable |
| 58 | `status_code` | `status_code: int` | Local variable |
| 73 | `action` | `action: str` | Local variable |
| 89 | `start_id` | `start_id: int` | Local variable |
| 90 | `end_id` | `end_id: int` | Local variable |
| 91 | `is_interactive` | `is_interactive: bool` | Local variable |
| 94 | `id` | `place_id: int` (rename) | Loop variable |
| 98 | `not_found_action` | `not_found_action: str` | Local variable |
| 102 | `internal_server_error_action` | `internal_server_error_action: str` | Local variable |
| 106 | `success_action` | `success_action: str` | Local variable |
| 110 | `id` | `place_id: int` (rename) | Loop variable |
| 125 | `place_data:dict` | `place_data: Dict[str, Any]` | Already has type hint but wrong format |
| 135 | `id_local` | `id_local: Optional[Any]` | Local variable |
| 137 | `id_backend` | `id_backend: Optional[str]` | Already typed |
| 154 | `response` | `response: requests.Response` | Local variable |
| 164 | `response` | `response: requests.Response` | Local variable |
| 182 | `data:dict` | `data: Dict[str, Any]` | Already has type hint |
| 186 | `place_data: dict` | `place_data: Optional[Dict[str, Any]]` | Already has type hint |
| 190 | `place_id: str` | `place_id: Optional[str]` | Wrong type, should be Optional |
| 197 | `promotion_list` | `promotion_list: Optional[Any]` | Local variable |
| 205 | `promo_data` | `promo_data: Any` | Loop variable |
| 227 | `nearby_data_filepath` | `nearby_data_filepath: str` | Local variable |
| 230 | `root, dirs, _` | `root: str, dirs: List[str], _: List[str]` | os.walk tuple |
| 231 | `dir` | `directory: str` (rename, `dir` shadows builtin) | Loop variable |
| 233 | `subdirectory_path` | `subdirectory_path: str` | Local variable |
| 234 | `subroot, _, subfiles` | `subroot: str, _: List[str], subfiles: List[str]` | os.walk tuple |
| 235 | `subfilename` | `subfilename: str` | Loop variable |
| 252 | `type_of_data_option` | `type_of_data_option: str` | Local variable |
| 258 | `nearby_data_filepath` | `nearby_data_filepath: str` | Local variable |
| 261 | `root, dirs, files` | `root: str, dirs: List[str], files: List[str]` | os.walk tuple |
| 262 | `filename` | `filename: str` | Loop variable |
| 270 | `ai_data_filepath` | `ai_data_filepath: str` | Local variable |
| 273 | `root, dirs, files` | `root: str, dirs: List[str], files: List[str]` | os.walk tuple |
| 274 | `filename` | `filename: str` | Loop variable |
| 291 | `def main()` | Add `-> None` | |
| 308 | `input_option` | `input_option: str` | Local variable |

**Total Annotations:** ~40

---

## File 3: clean_nearby_places.py

### Import Additions Needed
```python
from typing import List, Dict, Any
```

### Variables and Functions Requiring Type Annotations

| Line | Current | Type Needed | Notes |
|------|---------|-------------|-------|
| 19 | `def _get_nearby_places(filename:str)` | Add `-> List[Dict[str, Any]]` | |
| 23 | `places: List[Dict]` | `places: List[Dict[str, Any]]` | More specific |
| 60 | `def _format_place_data(place_data:Dict)` | `place_data: Dict[str, Any]) -> Dict[str, Any]` | |
| 64 | `formatted_place_data: Dict` | `formatted_place_data: Dict[str, Any]` | |
| 65 | `missing_fields: List[str]` | Already typed | |
| 67 | `google_places_id: str` | Already typed | |
| 72 | `name: str` | Already typed | |
| 77 | `latitude: float` | Already typed | |
| 78 | `longitude: float` | Already typed | |
| 94 | `primary_type` | `primary_type: Optional[str]` | Local variable |
| 96 | `secondary_types: List[str]` | Already typed | |
| 100 | `rating` | `rating: Optional[float]` | Local variable |
| 105 | `postalAddress: Dict` | `postalAddress: Optional[Dict[str, Any]]` | |
| 108 | `city: str` | Already typed | |
| 113 | `state_code: str` | Already typed | |
| 118 | `zip` | `postal_code: Optional[str]` (rename) | Local variable |
| 127 | `street: str` | Already typed | |
| 133 | `periods` | `periods: List[Dict[str, Any]]` | Local variable |
| 136 | `day_map: Dict` | `day_map: Dict[int, str]` | More specific |
| 137 | `formatted_weekly_hours: List[Dict]` | `formatted_weekly_hours: List[Dict[str, Any]]` | |
| 138 | `place_name` | `place_name: str` | Local variable |
| 141-158 | Multiple hour variables | Already typed | |
| 176 | `phone` | `phone: Optional[str]` | Local variable |
| 181 | `website` | `website: Optional[str]` | Local variable |
| 189 | `def _post_nearby_places(places:List[Dict])` | Add `-> None` | |
| 193 | `i, place_data` | `i: int, place_data: Dict[str, Any]` | Loop variables |
| 196 | `place_status: str` | Already typed | |
| 202 | `formatted_place_data` | `formatted_place_data: Dict[str, Any]` | Local variable |
| 225 | `def _save_nearby_places(places: List[Dict])` | `places: List[Dict[str, Any]]` | |
| 228 | `output_dir` | `output_dir: str` | Local variable |
| 236 | `i, place_data` | `i: int, place_data: Dict[str, Any]` | Loop variables |
| 240 | `place_status: str` | Already typed | |
| 246 | `formatted_place_data` | `formatted_place_data: Dict[str, Any]` | Local variable |
| 252 | `place_name` | `place_name: str` | Local variable |
| 253 | `safe_filename` | `safe_filename: str` | Local variable |
| 254 | `filename` | `filename: str` | Local variable |
| 257 | `subdirectory` | `subdirectory: str` | Local variable |
| 258 | `subdirectory_path` | `subdirectory_path: str` | Local variable |
| 262 | `filepath` | `filepath: str` | Local variable |
| 274 | `def process_places(filename: str)` | Add `-> None` | |
| 279 | `places` | `places: List[Dict[str, Any]]` | Local variable |
| 291 | `def main()` | Add `-> None` | |
| 298 | `filename:str` | `filename: str` (add space) | Already typed |

**Total Annotations:** ~45

---

## File 4: fetch_nearby_places.py

### Import Additions Needed
```python
from typing import List, Dict, Any, Optional
```

### Variables and Functions Requiring Type Annotations

| Line | Current | Type Needed | Notes |
|------|---------|-------------|-------|
| 35 | `def __init__(self, api_key: str = None)` | `api_key: Optional[str] = None` | |
| 39 | `self.api_key` | `self.api_key: Optional[str]` | Instance variable |
| 50 | `) -> List[Dict]` | `) -> List[Dict[str, Any]]` | More specific |
| 53 | `headers` | `headers: Dict[str, str]` | Local variable |
| 59 | `payload` | `payload: Dict[str, Any]` | Local variable |
| 77 | `response` | Already typed | |
| 79 | `data` | `data: Dict[str, Any]` | Local variable |
| 109 | `) -> None` | Already typed | |
| 123 | `places` | `places: List[Dict[str, Any]]` | Local variable |
| 129 | `output_file` | `output_file: str` | Local variable |
| 138 | `def main()` | Add `-> None` | |
| 148 | `lat` | `lat: str` | Local variable |
| 149 | `lon` | `lon: str` | Local variable |
| 150 | `lat_rounded` | `lat_rounded: float` | Local variable |
| 151 | `lon_rounded` | `lon_rounded: float` | Local variable |
| 157 | `fetcher` | `fetcher: PlacesFetcher` | Local variable |

**Total Annotations:** ~20

---

## File 5: BackendClient.py

### Import Additions Needed
```python
from typing import Optional, List, Dict, Any
```

### Variables and Functions Requiring Type Annotations

| Line | Current | Type Needed | Notes |
|------|---------|-------------|-------|
| 14 | `self.api_url` | `self.api_url: str` | Instance variable |
| 20 | `root, _, files` | `root: str, _: List[str], files: List[str]` | os.walk tuple |
| 21 | `filename` | `filename: str` | Loop variable |
| 22 | `full_path` | `full_path: str` | Local variable |
| 26 | `data` | `data: Any` | Local variable |
| 56 | `box_distance: float` | Already typed | |
| 57-60 | SWlat, SWlng, etc. | Already typed via inline | |
| 61 | `params_string: str` | Already typed | |
| 62 | `url: str` | Already typed | |
| 65 | `response` | Already typed | |
| 77 | `places_list: list[dict]` | `places_list: List[Dict[str, Any]]` | Python 3.9+ syntax |
| 78 | `place` | `place: Dict[str, Any]` | Loop variable |
| 100 | `def update_place(self, place_id: int, place_data: dict)` | `place_data: Dict[str, Any]` | |
| 114 | `def create_place(self, place_data: dict)` | `place_data: Dict[str, Any]` | |
| 128 | `def create_promotion(self, place_id: int, promo_data: dict)` | `promo_data: Dict[str, Any]` | |

**Total Annotations:** ~20

---

## Summary Statistics

### By File:
- **ai_data_cleaner.py:** ~35 annotations
- **backend_CLI.py:** ~40 annotations
- **clean_nearby_places.py:** ~45 annotations
- **fetch_nearby_places.py:** ~20 annotations
- **BackendClient.py:** ~20 annotations

**Total Annotations to Add:** ~160

---

## Implementation Order

### Phase 1: Simple Files (1 hour)
1. **BackendClient.py** - Cleanest, fewest changes
2. **fetch_nearby_places.py** - Already mostly typed

### Phase 2: Medium Complexity (1.5 hours)
3. **clean_nearby_places.py** - Many local variables
4. **ai_data_cleaner.py** - Complex return types

### Phase 3: Most Complex (1.5 hours)
5. **backend_CLI.py** - Most variables, os.walk tuples

### Phase 4: Testing & Verification (1 hour)
- Run Pylance/mypy to verify
- Fix any missed annotations
- Test imports still work

---

## Common Type Patterns

### Dict Types
```python
# Before
place_data: dict

# After
place_data: Dict[str, Any]
```

### Optional Types
```python
# Before
api_key = None

# After
api_key: Optional[str] = None
```

### List Types
```python
# Before
places: List[Dict]

# After
places: List[Dict[str, Any]]
```

### os.walk Unpacking
```python
# Before
for root, dirs, files in os.walk(path):

# After
for root, dirs, files in os.walk(path):
    root: str
    dirs: List[str]
    files: List[str]
```

Or inline:
```python
for root_path, directories, filenames in os.walk(path):
    # More descriptive names avoid need for type hints
```

---

## Known Issues to Fix

### Issue 1: Variable Name Shadowing
**Location:** `backend_CLI.py:94, 110, 231`
```python
# Bad: 'id' shadows builtin
for id in range(start_id, end_id):

# Good: Use descriptive name
for place_id in range(start_id, end_id):
```

**Location:** `backend_CLI.py:231`
```python
# Bad: 'dir' shadows builtin
for dir in dirs:

# Good: Use descriptive name
for directory in dirs:
```

### Issue 2: Wrong Return Type
**Location:** `ai_data_cleaner.py:111`
```python
# Wrong
def call_openai_api(self, scraped_website_content: str) -> dict[str]:

# Correct
def call_openai_api(self, scraped_website_content: str) -> PlaceDataExtraction:
```

### Issue 3: Inconsistent Type Syntax
**Location:** `BackendClient.py:77`
```python
# Old Python 3.9+ syntax
places_list: list[dict]

# Compatible syntax (Python 3.7+)
places_list: List[Dict[str, Any]]
```

**Location:** `backend_CLI.py:137`
```python
# Union type using | (Python 3.10+)
id_backend: str | None

# Compatible syntax
id_backend: Optional[str]
```

---

## Verification Checklist

After implementation, verify:
- [ ] All function signatures have return types
- [ ] All function parameters have types
- [ ] All instance variables have types (in `__init__`)
- [ ] All local variables with ambiguous types are annotated
- [ ] No use of deprecated lowercase `list`, `dict` (use `List`, `Dict`)
- [ ] No use of `|` union operator (use `Optional` or `Union`)
- [ ] No variable names shadow builtins (`id`, `dir`, `zip`, etc.)
- [ ] Pylance shows no errors
- [ ] Code still runs (type hints are runtime no-ops)

---

## Next Steps

1. **Review this plan** with user
2. **Get approval** to proceed
3. **Implement in order** (Phase 1 → 4)
4. **Commit changes** incrementally per file
5. **Run type checker** to verify completion

---

**Plan Version:** 1.0
**Created:** 2025-12-08
