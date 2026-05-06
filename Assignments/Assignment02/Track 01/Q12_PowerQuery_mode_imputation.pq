// =====================================================================
// Q12 — POWER QUERY M-SCRIPT
// Handle missing values in Customer_Type by replacing them with the MODE
// =====================================================================
//
// Context:
//   - Source file:  synthetic_sales_data_400k.csv  (400,000 rows)
//   - Target column: Customer_Type   (values: "New" or "Returning")
//   - Note: the synthetic CSV has no native nulls in Customer_Type,
//     so we artificially null ~5% of rows in step 4 to demonstrate
//     the imputation workflow. In a real Meritshot retail dataset
//     this step would be skipped.
//
// To use:
//   Power BI Desktop  ->  Home  ->  Transform data  ->  Advanced Editor
//   Paste this entire script into the Advanced Editor of a new query.
// =====================================================================

let

    // -----------------------------------------------------------------
    // STEP 1 — Load the CSV
    // -----------------------------------------------------------------
    Source = Csv.Document(
        File.Contents("C:\Data\synthetic_sales_data_400k.csv"),
        [Delimiter = ",", Columns = 14, Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),

    // -----------------------------------------------------------------
    // STEP 2 — Promote the first row to headers
    // -----------------------------------------------------------------
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // -----------------------------------------------------------------
    // STEP 3 — Set explicit data types (so blanks are treated as null,
    // not as the empty string "")
    // -----------------------------------------------------------------
    TypedTable = Table.TransformColumnTypes(PromotedHeaders, {
        {"Product_ID",           Int64.Type},
        {"Sale_Date",             type date},
        {"Sales_Rep",             type text},
        {"Region",                type text},
        {"Sales_Amount",          type number},
        {"Quantity_Sold",         Int64.Type},
        {"Product_Category",      type text},
        {"Unit_Cost",             type number},
        {"Unit_Price",            type number},
        {"Customer_Type",         type text},
        {"Discount",              type number},
        {"Payment_Method",        type text},
        {"Sales_Channel",         type text},
        {"Region_and_Sales_Rep",  type text}
    }),

    // -----------------------------------------------------------------
    // STEP 4 — DEMONSTRATION ONLY: introduce ~5% nulls into
    // Customer_Type so we have something to impute.
    // Remove this step on real production data.
    // -----------------------------------------------------------------
    WithSyntheticNulls = Table.AddColumn(
        TypedTable,
        "Customer_Type_Dirty",
        each if Number.Mod(Number.RandomBetween(0, 100), 20) = 0
             then null
             else [Customer_Type],
        type text
    ),
    DropOriginal      = Table.RemoveColumns(WithSyntheticNulls, {"Customer_Type"}),
    RenameDirtyAsLive = Table.RenameColumns(DropOriginal,
                            {{"Customer_Type_Dirty", "Customer_Type"}}),

    // -----------------------------------------------------------------
    // STEP 5 — Diagnostic: count how many nulls we now have
    // (Surface this in a separate query if you want to see the number.)
    // -----------------------------------------------------------------
    NullCount = Table.RowCount(
        Table.SelectRows(RenameDirtyAsLive, each [Customer_Type] = null)
    ),

    // -----------------------------------------------------------------
    // STEP 6 — CALCULATE THE MODE OF Customer_Type
    //   (a) drop nulls
    //   (b) group, count, sort, take the top label
    // -----------------------------------------------------------------
    NonNullRows = Table.SelectRows(RenameDirtyAsLive, each [Customer_Type] <> null),

    GroupedCounts = Table.Group(
        NonNullRows,
        {"Customer_Type"},
        {{"Frequency", each Table.RowCount(_), Int64.Type}}
    ),

    SortedDescending = Table.Sort(
        GroupedCounts,
        {{"Frequency", Order.Descending}}
    ),

    ModeValue = SortedDescending{0}[Customer_Type],   // <-- the mode
    ModeFreq  = SortedDescending{0}[Frequency],

    // -----------------------------------------------------------------
    // STEP 7 — Impute: replace nulls with the mode value
    // -----------------------------------------------------------------
    Imputed = Table.ReplaceValue(
        RenameDirtyAsLive,
        null,
        ModeValue,
        Replacer.ReplaceValue,
        {"Customer_Type"}
    ),

    // -----------------------------------------------------------------
    // STEP 8 — Audit: confirm zero nulls remain
    // -----------------------------------------------------------------
    PostImputeNullCount = Table.RowCount(
        Table.SelectRows(Imputed, each [Customer_Type] = null)
    ),

    // -----------------------------------------------------------------
    // Final output table
    // -----------------------------------------------------------------
    Result = Imputed

in
    Result


// =====================================================================
// WHY MODE (and not mean / median)?
// =====================================================================
// Customer_Type is a categorical / nominal field — its values ("New",
// "Returning") have no numeric ordering or magnitude. Mean is undefined
// for text. Median requires an ordering. Mode — the most frequently
// occurring category — is the only central-tendency measure that
// makes statistical sense for a nominal variable, which is why it is
// the standard imputation strategy for missing categorical data.
// =====================================================================
//
// EXPECTED OUTPUT (after running on the 400K-row file):
//   ModeValue            -> "Returning"  (≈ 50.0% of non-null rows)
//   ModeFreq             -> ~190,000
//   NullCount            -> ~20,000   (≈ 5% synthetic nulls)
//   PostImputeNullCount  -> 0
// =====================================================================
