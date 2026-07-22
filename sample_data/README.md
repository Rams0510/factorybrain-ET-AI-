# Sample Industrial Documents

Upload these through the **Upload Documents** page to see the full
pipeline (parsing -> entity extraction -> MySQL -> embeddings -> ChromaDB
-> Neo4j) working end to end without needing your own document set:

| File | Type | Exercises |
|---|---|---|
| `maintenance_report_P101.txt` | Maintenance Report | Entity extraction (equipment ID, pressure, temperature, engineer, regulation), Equipment auto-creation |
| `sop_boiler_B12.txt` | SOP | Safety-rule pattern extraction, regulatory references |
| `inspection_report_TK305.txt` | Inspection Report | Inspection-finding extraction, severity mentions |
| `incident_report_P101_nearmiss.txt` | Incident Report | Lessons Learned module, links back to P-101 |
| `maintenance_log.csv` | Tabular maintenance log | XLSX/CSV parser, multiple equipment tags |

After uploading all five, try in **AI Chat**:
- "Why did Pump P-101 fail?"
- "What does the SOP for Boiler B-12 say about startup pressure limits?"
- "What did the inspection find on TK-305?"

And check the **Knowledge Graph** page — it should show `Equipment(P-101)`
connected to `Engineer(Arvind Rao)` and an `Incident` node via
`FAILED_DUE_TO`.

To exercise the OpenCV P&ID pipeline, upload any PDF whose filename or
early text contains "P&ID" or "Piping and Instrumentation" — the pipeline
will rasterize the first page and run the heuristic shape/tag detector.
