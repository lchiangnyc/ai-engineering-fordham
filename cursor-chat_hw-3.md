# homework-3
_Exported on 2/4/2026 at 23:43:19 EST from Cursor (2.4.27)_

---

**User**

Hey there-- having trouble figuring out function design: need to search across all queries, given the following helper functions:

@Chiang-Leonard_homework-3.ipynb (1-81) 

---

**Cursor**

Checking the notebook for your search implementation and how it should work with the evaluation helpers.


Checking how the search function is used and whether a BM25/search implementation exists:


Checking the signature of `search_products_bm25_mfn` and how you're calling `evaluate_search`:


Here’s the core issue and how to fix it.

---

## What the evaluator expects

From the helpers:

- **`evaluate_search(search_func, products_df, queries_df, labels_df, ...)`**  
  Loops over every row in `queries_df` and, for each row, does:
  - `query_text = row['query']`
  - `ndcg = evaluate_single_query(query_text, query_id, products_df, labels_df, search_func, k)`

- **`evaluate_single_query(..., search_func, k)`**  
  Does:
  - `results = search_func(query_text)`  
  So it calls `search_func` with **only** the query string.

So **`search_func` must be a callable that takes a single argument (the query string) and returns a DataFrame that has a `product_id` column.**  
“Search across all queries” is already done by `evaluate_search`; you don’t loop over queries yourself. You only need to give it a function that knows how to run **one** query.

---

## Why your current attempts break

1. **Passing `search_products_bm25_mfn` directly**  
   That function has signature  
   `(query, products_df, fields, tokenizer=..., k=...)`.  
   The evaluator will only call `search_func(query_text)`, so it never passes `products_df` or `fields` → you get “missing 2 required positional arguments: 'products_df' and 'fields'”.

2. **Using `search_func = search_products_bm25_mfn(products_DF, fields=...)`**  
   That **calls** `search_products_bm25_mfn` once (and with the wrong arguments). The **return value** is a DataFrame, not a function. Then the evaluator does `search_func(query_text)`, i.e. “call a DataFrame with a string” → not what you want.

3. **Using `search_func = search_products(query=..., products_df=..., index=...)`**  
   Same idea: that’s one call to `search_products`, so `search_func` is again a **result** (DataFrame), not a function that can be called again for each new query.

So the design rule: **`search_func` must be a function (or callable) of one variable: `query_text`.**  
Any extra data (products DataFrame, index, fields, tokenizer, k) must be “baked in” via a wrapper, not passed by the evaluator.

---

## Correct function design: wrap your search

You need a **wrapper** that:

- Takes only **one argument**: `query_text`.
- Uses your pre-built data (e.g. `products_DF`, `fields_nd`, index, tokenizer) from the surrounding scope.
- Returns the same kind of DataFrame your current search returns (with `product_id`).

**Option 1 – Lambda (compact)**

```python
# Assume you already have: products_DF, fields_nd (your multi-field index), etc.

search_func = lambda query_text: search_products_bm25_mfn(
    query_text, products_DF, fields_nd, k=10
)

evaluate_search(
    search_func=search_func,
    products_df=products_DF,
    queries_df=queries_DF,
    labels_df=labels_DF,
)
```

**Option 2 – Named wrapper (clear for debugging)**

```python
def my_search(query_text):
    return search_products_bm25_mfn(
        query_text, products_DF, fields_nd, k=10
    )

evaluate_search(
    search_func=my_search,
    products_df=products_DF,
    queries_df=queries_DF,
    labels_df=labels_DF,
)
```

**Option 3 – `functools.partial`**

```python
from functools import partial

search_func = partial(
    search_products_bm25_mfn,
    products_df=products_DF,
    fields=fields_nd,
    k=10
)
# partial leaves the first positional arg (query) to be filled when called
evaluate_search(search_func=search_func, ...)
```

For **`evaluate_single_query`**, you pass the **same** kind of wrapper (a callable that takes only `query_text`), plus the other required args:

```python
evaluate_single_query(
    query_text=queries_DF.iloc[0]["query"],
    query_id=queries_DF.iloc[0]["query_id"],
    products_df=products_DF,
    labels_df=labels_DF,
    search_func=my_search,   # or the lambda / partial from above
    k=10,
)
```

**Summary:**  
- Evaluator already iterates over all queries and calls `search_func(query_text)` for each.  
- Your job is to give it a **single-argument function** that, for any query string, returns the search result DataFrame with `product_id`. Use a lambda, a small wrapper, or `partial` to fix the extra arguments (`products_df`, `fields`, etc.) once and expose only `query_text` as the argument.

---

**User**

Seems promising, thanks. However, remains unclear over which space/data hypothetical search function will be looking

---

**Cursor**

Here’s exactly what “space/data” the search function is looking at.

---

## Who provides the search space?

The evaluator does **not** pass the product corpus or index. It only does:

```text
results = search_func(query_text)
```

So **the search function you pass in must already “know” what to search over.** That “knowledge” comes from the wrapper you define in your notebook.

---

## Where the data comes from (closure)

When you define the wrapper in your notebook, it **captures** the variables in scope at that moment:

```python
# In your notebook you already have:
# - products_DF
# - fields_nd  (or index + doc_lengths for single-field BM25)

search_func = lambda query_text: search_products_bm25_mfn(
    query_text, products_DF, fields_nd, k=10
)
```

- **`query_text`** is the only thing that changes on each call (provided by the evaluator).
- **`products_DF`** and **`fields_nd`** are captured from the notebook scope when you define the lambda. They are the same on every call.

So the “space” the hypothetical search function is looking at is:

- **Corpus:** the DataFrame you close over (e.g. `products_DF`) — same product catalog every time.
- **Index:** the index structure you close over (e.g. `fields_nd`, or `index` + `doc_lengths` for single-field) — built from that same catalog.

No other data is injected by `evaluate_search`; it only feeds one query string per call.

---

## Summary

| Provided by evaluator | Provided by you (in the wrapper) |
|------------------------|----------------------------------|
| `query_text` (string)  | `products_DF`, index/`fields_nd`, tokenizer, `k`, etc. |

So: **the search always runs over the exact products and index you baked into the wrapper** (the DataFrame and index you built earlier in the notebook). The evaluator only supplies the query; the “space” is fixed by what you capture in `search_func`.

---

**User**

Should any other columns/Series appear alongside product_id in results search_func() returns?

---

**Cursor**

Checking what the evaluation code uses from the DataFrame returned by `search_func`:


From the evaluation helper:

```python
results = search_func(query_text)
product_ids = results['product_id'].tolist()[:k]
```

So the evaluator only uses:

- The **`product_id`** column (and that it has a `.tolist()` and can be sliced with `[:k]`).

No other columns are read. So:

- **Required:** a column named **`product_id`** (and enough rows for `[:k]` to make sense).
- **Optional:** any other columns (e.g. `score`, `rank`, `product_name`, `bm25_mfn score`) are allowed and ignored by the evaluator.

Your `search_products` / `search_products_bm25_mfn` already return DataFrames that include `product_id` (from `products_df.iloc[top_k_idx].copy()`), plus extra columns. That’s fine: the evaluator will work as long as `product_id` is present; extra columns don’t need to be removed.

---

**User**

Appreciate help given so far.
How to resolve

UFuncTypeError                            Traceback (most recent call last)
Cell In[300], line 14
      2 search_query = "chair"
      3 fields_dict = {
      4     "indices" : {
      5         "product_name" : name_index,
   (...)     11         }
     12     }
---> 14 results_bm25f_nd = search_products_bm25f_blend(     # nd for name and description
     15     query = search_query,
     16     products_df = products_DF,
     17     fields = fields_dict,
     18     )
     20 # Slicing DataFrame of results for improved readability, reindexing by bm25 rank
     21 # Extracting DataFrame from returned tuple
     22 results_bm25f_nd_DF = results_bm25f_nd[0]

Cell In[299], line 63, in search_products_bm25f_blend(query, products_df, fields, tokenizer, k)
     60 indices = fields["indices"]
     61 doc_lengths_dict = fields["lengths"]
---> 63 scores_bm25f_blended = score_bm25f_blended(
     64     query, indices, doc_lengths_dict, num_docs)
     65 top_k_idx = np.argsort(-scores_bm25f_blended)[:k]
     67 results_bm25f_DF = products_df.iloc[top_k_idx].copy()

Cell In[299], line 17, in score_bm25f_blended(query, indices, doc_lengths_dict, num_docs, tokenizer, k1, b)
     15 total_lengths = np.zeros(num_docs)
     16 for field_lengths in doc_lengths_dict.values():
---> 17     total_lengths += np.array(field_lengths)
     18 avg_doc_len = np.mean(total_lengths)
     20 for token in query_tokens:
     21     # Calculate combined DF (max across fields)

UFuncTypeError: Cannot cast ufunc 'add' output from dtype('O') to dtype('float64') with casting rule 'same_kind'

---

**Cursor**

The traceback plus your code snippet basically tell us two things:

1. **Where it blows up**

In `score_bm25f_blended`:

```python
total_lengths = np.zeros(num_docs)
for field_lengths in doc_lengths_dict.values():
    total_lengths += np.array(field_lengths)
```

`total_lengths` is a `float64` array. One of the `field_lengths` being looped over is **not** a numeric list/array, so `np.array(field_lengths)` becomes `dtype('O')` (object). Numpy then refuses to add `float64` + `object` → the `UFuncTypeError`.

2. **Why it happens (your `fields_dict` wiring)**

From your test cell (the one that raised the error):

```python
fields_dict = {
    "indices" : {
        "product_name"        : name_index,
        "product_description" : name_lengths,   # <‑‑ WRONG: should be an index, not lengths
    },
    "lengths" : {
        "product_name"        : desc_index,     # <‑‑ WRONG: this is an *index* dict, not lengths
        "product_description" : desc_lengths,
    }
}
```

- Under `"indices"`:
  - `product_name` → `name_index` ✅
  - `product_description` → **`name_lengths`** ❌ (this is a list/array of lengths, not an index)

- Under `"lengths"`:
  - `product_name` → **`desc_index`** ❌ (this is an inverted index dict, not a numeric lengths array)
  - `product_description` → `desc_lengths` ✅

Then, inside `score_bm25f_blended`:

- `doc_lengths_dict = fields["lengths"]`
- So `doc_lengths_dict.values()` is something like `[desc_index, desc_lengths]`

When the loop hits `field_lengths = desc_index` (a dict), `np.array(field_lengths)` becomes an object array of its keys, not a numeric array, and you get the `dtype('O')` addition error.

---

### How to fix it

Ensure that:

- All entries under `fields["indices"]` are **indices** (your inverted index dicts).
- All entries under `fields["lengths"]` are **numeric length sequences** (lists/arrays of document lengths of equal length).

Concretely, if you have:

- `name_index`, `name_lengths` from `product_name`
- `desc_index`, `desc_lengths` from `product_description`

then define:

```python
fields_dict = {
    "indices": {
        "product_name":        name_index,
        "product_description": desc_index,
    },
    "lengths": {
        "product_name":        name_lengths,
        "product_description": desc_lengths,
    },
}
```

With that wiring:

- `doc_lengths_dict.values()` will be `[name_lengths, desc_lengths]`, both numeric, same length (`num_docs`), so `total_lengths += np.array(field_lengths)` works fine.
- `indices.values()` will be your actual indices for BM25F scoring.

If you still see errors after fixing the dict, you can quickly sanity‑check in a cell:

```python
for field_name, lens in fields_dict["lengths"].items():
    print(field_name, type(lens), len(lens), np.array(lens).dtype)
```

You want both lens to produce a numeric dtype (e.g. `int64` or `float64`), and `len(lens) == num_docs`.

---

**User**

Hiya -- could you clue me into 1) why cell below has such a long runtime and 2) how to rewrite functions to avoid that?

---

**Cursor**


Checking which cell is slow. Searching for evaluation or search calls that might be slow:



Reviewing the slow cell and the search function it calls:



Checking how the naive multi-field version handles this:



Checking how the efficient single-field version handles this:



## Why it's slow

The bottleneck is in `score_bm25f_blended` at line 2036:

```python
for doc_id in range(num_docs):  # ❌ Loops through ALL 42,994 documents!
    for field_name, index in indices.items():
        tf = get_tf(token, doc_id, index)  # Most return 0!
```

This iterates over all documents for every token, even when most don't contain the token.

Compare to the efficient `score_bm25` (around line 1158):

```python
if token in index:
    for doc_id, tf in index[token].items():  # ✅ Only docs that contain the token!
        # score this doc
```

The efficient version uses the inverted index to only visit documents that contain the token.

---

## Performance impact

- 480 queries × ~3 tokens × 42,994 docs × 3 fields ≈ 186 million iterations
- Most `get_tf()` calls return 0 (token not in doc)
- Each call does a dictionary lookup

---

## How to fix: use the inverted index

Rewrite `score_bm25f_blended` to iterate only over documents that contain each token, similar to `score_bm25`:

```python
def score_bm25f_blended(
    query: str, indices: dict, doc_lengths_dict: dict, num_docs: int,
    agg: Literal[max|sum] = max, tokenizer = snowball_tokenize,
    k1: float = 1.2, b: float = 0.75):
    """
    BM25F scoring: blend TF across fields before applying IDF.
    """
    query_tokens = tokenizer(query)
    scores = np.zeros(num_docs)
    
    # Calculate average doc length across all fields (do this once)
    total_lengths = np.zeros(num_docs)
    for field_lengths in doc_lengths_dict.values():
        total_lengths += np.array(field_lengths)
    avg_doc_len = np.mean(total_lengths)
    
    for token in query_tokens:
        # Calculate combined DF (max/sum across fields)
        combined_df = 0
        for index in indices.values():
            if agg == max:
                combined_df = max(combined_df, get_df(token, index))
            elif agg == sum:
                combined_df += get_df(token, index)
        
        if combined_df == 0:
            continue
        
        idf = bm25_idf(combined_df, num_docs)
        
        # ✅ FIX: Collect all doc_ids that contain this token in ANY field
        docs_with_token = set()
        for index in indices.values():
            if token in index:
                docs_with_token.update(index[token].keys())
        
        # ✅ FIX: Only iterate over documents that contain the token
        for doc_id in docs_with_token:
            combined_impact = 0
            
            for field_name, index in indices.items():
                # Direct lookup instead of get_tf() - faster!
                if token in index and doc_id in index[token]:
                    tf = index[token][doc_id]
                    doc_len = doc_lengths_dict[field_name][doc_id]
                    avg_field_len = np.mean(doc_lengths_dict[field_name])
                    impact = tf / (1 - b + b * doc_len / avg_field_len)
                    combined_impact += impact
            
            if combined_impact > 0:
                saturated = combined_impact / (combined_impact + k1)
                scores[doc_id] += idf * saturated
    
    return scores
```

---

## Key changes

1. Collect `docs_with_token` by unioning `index[token].keys()` across all fields.
2. Iterate only over `docs_with_token` instead of `range(num_docs)`.
3. Use direct `index[token][doc_id]` when the token exists, avoiding `get_tf()` overhead.

---

## Expected speedup

- Before: O(tokens × num_docs × fields) ≈ 186M iterations
- After: O(tokens × avg_docs_per_token × fields) ≈ maybe 1–5M iterations (depends on token frequency)

This should reduce runtime from minutes to seconds. The same pattern applies to `score_bm25_mf_naive` if it also loops over all documents.

---

**User**

Traceback hot off the grill

ValueError                                Traceback (most recent call last)
Cell In[62], line 1
----> 1 evaluation_ndc_3 = evaluate_search(
      2     query_search_ndc_take2,
      3     products_DF[:3], queries_DF[:3], labels_DF[:3]
      4     )
      5 display(evaluation_ndc_3)
      6 print(f"[:3] test completed")

Cell In[38], line 65, in evaluate_search(search_func, products_df, queries_df, labels_df, k, verbose)
     62     query_id = row['query_id']
     63     query_text = row['query']
---> 65     ndcg = evaluate_single_query(query_text, query_id, products_df, 
     66                                  labels_df, search_func, k)
     67     results.append({
     68         'query_id': query_id,
     69         'query': query_text,
     70         'ndcg': ndcg
     71     })
     73 results_df = pd.DataFrame(results)

Cell In[38], line 38, in evaluate_single_query(query_text, query_id, products_df, labels_df, search_func, k)
     22 def evaluate_single_query(query_text: str, query_id: int, products_df: pd.DataFrame,
     23                           labels_df: pd.DataFrame, search_func, k: int = 10) -> float:
     24     """
     25     Evaluate search for a single query.
     26 
   (...)     36         NDCG@k score for this query
     37     """
---> 38     results = search_func(query_text)
     39     product_ids = results['product_id'].tolist()[:k]
     40     relevances = get_relevance_grades(product_ids, query_id, labels_df)

Cell In[61], line 4, in query_search_ndc_take2(query_text)
      2 def query_search_ndc_take2(query_text):     # take2 for this being second attempt
      3     # Using naive multi-field now
----> 4     product_results_DF = search_products_bm25_mfn(
      5         query = query_text,
      6         products_df = products_DF,
      7         fields = bm25_mfn_ndc_dict
      8         )
      9     return product_results_DF[0]

Cell In[23], line 65, in search_products_bm25_mfn(query, products_df, fields, tokenizer, k)
...
     25         # print(field_name, (len(field_index), len(field_doc_lengths)))
     26         avg_doc_len = np.mean(field_doc_lengths)
     28         df = get_df(token, field_index)

ValueError: too many values to unpack (expected 2, got 3)

---

**Cursor**


Checking how `search_products_bm25_mfn` expects `fields` and how `bm25_mfn_ndc_dict` is defined:



Checking the full structure of `bm25_mfn_ndc_dict` and the `mfn_nd_dict` format that works:



Checking what `build_index` returns and whether any field value is a 3-tuple:



Checking for a `bm25_mfn_ndc_dict` definition that uses the nested "indices"/"lengths" structure:



The traceback comes from a **format mismatch** between what `search_products_bm25_mfn` expects and what `bm25_mfn_ndc_dict` is.

---

## What’s wrong

`search_products_bm25_mfn` (and `score_bm25_mf_naive`) expect **flat** `fields`: each key is a field name and each value is a **2-tuple** `(index, doc_lengths)`:

```python
for field_name, (field_index, field_doc_lengths) in fields.items():
```

So the contract is:

- `fields = { "field_name": (index, doc_lengths), ... }`

Your **current** `bm25_mfn_ndc_dict` is the **nested** layout (used by the BM25F blend function):

```python
bm25_mfn_ndc_dict = {
    "indices" : {
        "product_name" : name_index,
        "product_description" : desc_index,
        "product_class" : class_index
    },
    "lengths" : {
        "product_name" : name_lengths,
        "product_description" : desc_lengths,
        "product_class" : class_lengths
    }
}
```

When the loop runs `for field_name, (field_index, field_doc_lengths) in fields.items()`:

1. First pair: `field_name = "indices"`, value = `{"product_name": ..., "product_description": ..., "product_class": ...}` (a dict with **3** keys).
2. It then does `(field_index, field_doc_lengths) = that_dict`.
3. Unpacking a dict yields its keys, so Python tries to assign **3** keys into **2** variables → **ValueError: too many values to unpack (expected 2, got 3)**.

So the bug is: you’re passing the **nested** structure to a function that expects the **flat** structure.

---

## Fix

Use the **flat** format for `search_products_bm25_mfn`: one entry per field, value = `(index, lengths)`.

Define a dedicated dict for the naive multi-field search, e.g.:

```python
# For search_products_bm25_mfn (flat: field_name -> (index, lengths))
bm25_mfn_ndc_dict = {
    "product_name"        : (name_index, name_lengths),
    "product_description"  : (desc_index, desc_lengths),
    "product_class"        : (class_index, class_lengths),
}
```

Use this `bm25_mfn_ndc_dict` in `query_search_ndc_take2` when calling `search_products_bm25_mfn`.

Keep the **nested** structure (with `"indices"` and `"lengths"`) only for the BM25F blend function (e.g. `search_products_bm25f_blend`). So you can have two dicts:

- **Flat** (for MFN):  
  `{ "product_name": (name_index, name_lengths), ... }`  
  → use with `search_products_bm25_mfn` and `query_search_ndc_take2`.
- **Nested** (for BM25F):  
  `{ "indices": { ... }, "lengths": { ... } }`  
  → use with `search_products_bm25f_blend` / `query_search_ndc` if you use that path.

After changing `bm25_mfn_ndc_dict` to the flat form above, the “expected 2, got 3” error should go away.

