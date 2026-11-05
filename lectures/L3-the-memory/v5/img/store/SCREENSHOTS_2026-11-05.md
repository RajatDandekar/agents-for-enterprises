Qdrant Cloud dashboard screenshots, taken 5 Nov 2026 on cluster RAGProject (free tier, v1.20.0), collection northbridge_docs.
- visualize_all.jpg: Collections → northbridge_docs → Visualize, request {"limit": 3000, "using": "dense", "color_by": {"payload": "folder"}}.
  Qdrant's own UMAP map of a 3,000-point sample of the dense vectors, coloured by the payload field folder. Legend counts are
  of the sample (06_transactions 1849, 05_master_data 713, 03_ledgerline_manuals 178, 04_service_definitions 99,
  02_procedures 42, 01_policies 25, 07_data_dictionary 24, 08_release_notes 22, 09_email_archive 14, 10_meeting_notes 14, Other 20).
- filter_superseded.jpg: Points tab, payload filter superseded:true. First hit: point 192, POL-APR-002 v2.0 Approval Matrix,
  file 01_policies/old/Approval_Matrix_v2.0_2024.docx, status "SUPERSEDED", superseded true; vector dense, length 384.
- ann_recall.jpg: ANN Recall tab → Check Index Quality (100 sampled points, HNSW search at the collection's default
  settings vs exact search): mean recall@10 = 0.835 ± 0.3026; per point "exact" ≈ 9–19 ms vs "regular" ≈ 2–9 ms.
- earlier (4 Nov): cluster_overview.jpg (ID and endpoint blurred), collections.jpg, collection_info.jpg,
  collection_info_json.jpg, point_106.jpg (§6 of D), console_bm25.jpg.
Note: the cluster endpoint is in the browser address bar, not in these page captures; check each before committing.
