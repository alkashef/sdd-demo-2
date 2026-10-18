# Plan — sdd-demo-2

Only unfinished milestones. Delete a milestone's row and block in the commit that finishes it; git
history is the record. Template: `docs/workflow.md`.

**Next milestone number: M17**

## Milestones at a glance

| Milestone | Description | Model | Effort | Status |
| --- | --- | --- | --- | --- |
| **M2** Records, ports and file reader | `src/records.py`, `src/ports.py` and `src/file_reader.py`: read the CV and job-description folders and the prompt files (EXT-001, JOB-001). | sonnet | medium | open |
| **M3** Vector store and ranking | `src/vector_store.py` (installs `chromadb`) and `src/ranking.py` rank by similarity and keep items without a vector (RNK-001, MIS-002). | sonnet | high | open |
| **M4** LLM client | `src/llm_client.py` (installs `openai`, `pydantic`, `pytest-asyncio`): structured completion and embedding; SDK failures become `LlmError`; the key never leaks (ERR-001, NFR-001, NFR-002). | opus | high | open |
| **M5** Calculated attributes | `src/attributes.py` calculates every CAL value (EX-001 to EX-004) and derives EXT-007 to EXT-009. | sonnet | high | open |
| **M6** CV extraction | `prompt_data.py`, `llm_schemas.py`, `extraction.py` and `prompts/extract_cv.md` turn a CV into facts (EXT-002 to EXT-004, EXT-006, EXT-010, MIS-001); contradictory replies are refused; injected tags are escaped (DEC-015, DEC-016). | sonnet | high | open |
| **M7** Recommendation | `recommendation.py` and `prompts/match_cv_to_job.md` build an interview recommendation from the job description and the facts, with no name or contact (REC-001, NFR-001). | sonnet | medium | open |
| **M8** Start-up pipeline | `src/pipeline.py` runs DEC-007 with a concurrency limit; records `LlmError` per item and keeps every other result (PRG-003, MIS-001, MIS-002, ERR-001, ERR-002, RNK-002). | opus | high | open |
| **M9** Workspace views | `src/workspace_views.py` builds the lists, job detail, ranked candidates, candidate detail and ranked jobs (LST-001, LST-002, CND-001 to CND-003, JOB-002, JOB-003, RNK-003). | sonnet | medium | open |
| **M10** JSON API | `src/api/*` (installs `fastapi`, `httpx`) serves the read endpoints, the 404s and `/api/failures`; end-to-end tests with a fake workspace. | sonnet | medium | open |
| **M11** Entry point | `main.py` (installs `uvicorn`) runs the pipeline, then serves; start-up end-to-end test with a fake LLM; README Setup and How to run. | sonnet | medium | open |
| **M12** Front end: shell, lists, job view | `src/web/` (installs `playwright`): sticky header, navigation, job text panel, ranked candidate cards with recommendations; browser tests. | sonnet | high | open |
| **M13** Front end: candidate view and failures | Candidate view (raw CV, attributes, ranked jobs), failure panel, "Not available" against "Present"; browser tests. | sonnet | medium | open |
| **M14** Evaluation | `src/evaluation.py` and `python main.py --evaluate` check the ranking and the job dates; commits `gold_jobs.json` through a `.gitignore` exception (NFR-004, NFR-005). | sonnet | high | open |
| **M15** Sample builder | `scripts/build_sample.py` rebuilds `data/sample/` from the raw TalentCLEF files (DEC-010). | sonnet | medium | open |
| **M16** Lock file and CI | `scripts/lock.py`, `constraints.txt`, a lock check in `scripts/check.py`, and `.github/workflows/check.yml` (DEC-018). | sonnet | high | open |

## Milestones

### M2 — Records, ports and file reader

- **Refs:** EXT-001, JOB-001, ERR-001, DEC-008, DEC-009, design sections 2.1 and 3.
- **Owner:** `src/records.py`, `src/ports.py`, `src/file_reader.py`.
- **Tests first:** `test_ext_001_reads_every_txt_cv_in_the_folder`, `test_job_001_reads_every_job_description_in_the_folder`, `test_document_id_is_the_file_name`, `test_missing_folder_fails_with_a_clear_message`, `test_prompt_file_text_is_read`, `test_llm_output_error_is_an_llm_error_and_keeps_the_raw_output`, `test_records_are_frozen`.
- **Build:** the frozen records of section 3 (with `Workspace`); the three protocols and `LlmError` / `LlmOutputError`; the file reader as the only module that reads plain-text files, returning `Document` records.
- **Gate:** the tests and the checks pass; mypy accepts the protocols.

### M3 — Vector store and ranking

- **Refs:** RNK-001, MIS-002, DEC-004, DEC-011.
- **Owner:** `src/vector_store.py`, `src/ranking.py`.
- **Tests first:** `test_rnk_001_nearest_by_cosine_similarity_not_keyword_overlap`, `test_rnk_001_ties_broken_by_file_name`, `test_rnk_001_nearest_returns_every_stored_item_best_first`, `test_mis_002_item_without_vector_is_appended_last_with_no_score`, `test_dec_004_chroma_telemetry_is_off`.
- **Build:** install `chromadb` into `sdd-demo-2` and pin it in `requirements.txt`; `vector_store.py` implements `VectorIndex` on an in-memory Chroma collection with cosine distance, our vectors and no model download; `ranking.py` appends unscored items ordered by ID.
- **Gate:** the tests and the checks pass. If the install or the checks fail, block the milestone; there is no fallback store (DEC-011).

### M4 — LLM client

- **Refs:** ERR-001, NFR-001, NFR-002, DEC-003, DEC-006, DEC-011.
- **Owner:** `src/llm_client.py`.
- **Tests first:** `test_err_001_provider_failure_raises_llm_error_naming_the_cause`, `test_err_001_refusal_raises_llm_output_error_with_the_raw_output`, `test_err_001_invalid_shape_raises_llm_output_error`, `test_nfr_002_error_message_does_not_contain_the_api_key`, `test_nfr_001_complete_sends_only_the_given_system_and_user_text`, `test_embed_returns_the_vector_for_the_given_text`, `test_timeout_and_max_tokens_come_from_settings`.
- **Build:** install and pin `openai`, `pydantic` and `pytest-asyncio`. The client takes the SDK client and typed settings, and implements `StructuredCompleter` (Structured Outputs with a Pydantic model) and `Embedder`. Tests use a fake SDK client.
- **Gate:** the tests and the checks pass; no test calls the real service. The model IDs stay untested until the user's first run (DEC-003).

### M5 — Calculated attributes

- **Refs:** CAL-001 to CAL-005, CAL-007 to CAL-010, EXT-007 to EXT-009, EX-001 to EX-004, DEC-005, DEC-015, design section 3 (calculation rules).
- **Owner:** `src/attributes.py`.
- **Tests first:** `test_cal_001_total_employment_period`, `test_cal_002_job_count`, `test_cal_003_average_time_per_job`, `test_cal_004_employment_gaps`, `test_cal_005_months_since_graduation`, `test_cal_007_currently_employed_yes_no_and_not_available`, `test_cal_008_counts_both_months_and_present_is_current_month`, `test_cal_009_unknown_end_makes_average_and_gaps_not_available`, `test_cal_010_bad_dates_make_dependent_attributes_not_available`, `test_ext_007_distinct_job_countries`, `test_ext_008_distinct_employers`, `test_ext_009_last_job_is_latest_start`, `test_ex_001_three_jobs_to_present`, `test_ex_002_graduation_may_2018`, `test_ex_003_unknown_end_on_last_job`, `test_ex_004_reversed_range_and_future_graduation`.
- **Build:** pure functions of the facts and a given date, returning `CalculatedAttributes` with `None` for "Not available".
- **Gate:** the tests and the checks pass; the examples give exactly the values in the spec.

### M6 — CV extraction

- **Refs:** EXT-002, EXT-003, EXT-004, EXT-006, EXT-009, EXT-010, MIS-001, NFR-001, DEC-015, DEC-016.
- **Owner:** `src/extraction.py`, with `src/prompt_data.py`, `src/llm_schemas.py` and `prompts/extract_cv.md`.
- **Tests first:** `test_ext_002_name_is_extracted`, `test_ext_003_current_title_is_extracted`, `test_ext_004_skills_are_extracted`, `test_ext_006_city_and_country_are_extracted`, `test_ext_009_job_fields_are_extracted`, `test_ext_010_highest_degree_is_extracted`, `test_mis_001_null_field_becomes_none`, `test_dec_015_is_current_with_an_end_is_refused_as_llm_output_error`, `test_dec_016_user_text_tags_the_cv_and_escapes_an_injected_tag`, `test_dec_016_braces_marker_in_a_cv_is_unchanged`, `test_dec_016_prompt_file_has_no_placeholders`, `test_nfr_001_cv_text_is_only_in_the_user_text`.
- **Build:** the tag enum and escaping; the Pydantic reply models; extraction builds the user text and turns the validated reply into `CvFacts`. The prompt file is system text only and says tagged content is untrusted data.
- **Gate:** the tests and the checks pass; no test uses the real service.

### M7 — Recommendation

- **Refs:** REC-001, NFR-001, DEC-006, DEC-016.
- **Owner:** `src/recommendation.py`, with `prompts/match_cv_to_job.md`.
- **Tests first:** `test_rec_001_reply_becomes_an_interview_decision_with_a_reason`, `test_dec_006_request_has_no_name_address_or_contact`, `test_rec_001_facts_carry_is_current_beside_end`, `test_dec_016_job_description_and_facts_are_tagged_and_escaped`, `test_rec_001_invalid_reply_raises_llm_output_error`.
- **Build:** build the user text (tagged job description and the candidate facts as JSON, without name, address or contact) and turn the validated reply into a `Recommendation`.
- **Gate:** the tests and the checks pass.

### M8 — Start-up pipeline

- **Refs:** EXT-001, JOB-001, PRG-003, MIS-001, MIS-002, ERR-001, ERR-002, RNK-001, RNK-002, REC-001, DEC-007, DEC-008, DEC-014.
- **Owner:** `src/pipeline.py`.
- **Tests first:** `test_prg_003_each_cv_is_extracted_once`, `test_dec_014_embeds_the_raw_document_text`, `test_rnk_001_ranks_both_ways_by_similarity`, `test_rnk_002_rank_is_unchanged_by_calculated_attributes`, `test_rec_001_one_recommendation_per_pair`, `test_err_002_failed_extraction_keeps_every_other_result`, `test_err_001_failure_list_names_the_step_and_the_cause`, `test_mis_001_failed_extraction_has_no_facts`, `test_mis_002_cv_with_failed_extraction_stays_in_every_ranking`, `test_failed_embedding_ranks_last_with_no_score`, `test_failed_recommendation_is_recorded_and_not_available`, `test_dec_008_other_exceptions_propagate`, `test_dec_007_concurrency_is_limited_by_the_setting`.
- **Build:** the pipeline receives the file reader, the LLM client, the two vector stores and today's date. It reads, extracts, calculates, embeds, ranks and recommends, and returns one `Workspace`. Only `LlmError` is caught, per item (DEC-008).
- **Gate:** the tests and the checks pass; the catch is the only one in `src/`.

### M9 — Workspace views

- **Refs:** LST-001, LST-002, CND-001, CND-002, CND-003, JOB-002, JOB-003, RNK-003, REC-001, MIS-001, DEC-015, DEC-020.
- **Owner:** `src/workspace_views.py`.
- **Tests first:** `test_lst_001_job_list_has_id_and_title`, `test_lst_002_candidate_list_has_id_and_name`, `test_job_003_job_detail_has_the_raw_text`, `test_job_002_ranked_candidates_best_first_with_all_candidates`, `test_rnk_003_ranked_candidate_has_extracted_and_calculated_attributes`, `test_rec_001_ranked_candidate_has_the_recommendation`, `test_cnd_001_candidate_detail_has_the_raw_cv`, `test_cnd_002_candidate_detail_has_the_attributes`, `test_cnd_003_ranked_jobs_best_first`, `test_mis_001_missing_values_stay_none`, `test_dec_015_last_job_carries_is_current`, `test_unknown_id_is_reported_to_the_api_layer`.
- **Build:** pure functions over the workspace, using the pure helpers of `attributes` for the last job, countries and employers.
- **Gate:** the tests and the checks pass.

### M10 — JSON API

- **Refs:** LST-001, LST-002, CND-001, CND-002, CND-003, JOB-002, JOB-003, RNK-003, REC-001, ERR-001, MIS-001, DEC-002, DEC-012, DEC-013, DEC-020, design section 4.
- **Owner:** `src/api/app.py`, `src/api/jobs.py`, `src/api/candidates.py`, `src/api/status.py`, `src/api/schemas.py`.
- **Tests first:** `test_health_is_alive`, `test_lst_001_get_jobs`, `test_lst_002_get_candidates`, `test_job_003_get_job_returns_id_title_and_text`, `test_job_002_get_ranked_candidates`, `test_rnk_003_and_rec_001_ranked_candidate_fields`, `test_cnd_001_get_candidate_has_the_raw_cv`, `test_cnd_002_get_candidate_has_the_attributes`, `test_cnd_003_get_ranked_jobs`, `test_err_001_get_failures_lists_item_and_cause`, `test_mis_001_missing_value_is_null`, `test_unknown_id_returns_404_with_a_detail_message`, `test_dec_013_no_cors_headers`.
- **Build:** install and pin `fastapi` and `httpx`. The app factory takes a workspace and the web root, includes the routers and mounts the static folder. One handler calls one `workspace_views` function. The tests use the framework's test client and a fake workspace.
- **Gate:** the tests and the checks pass; a handler imports no gateway, pipeline or domain module.

### M11 — Entry point

- **Refs:** EXT-001, JOB-001, LST-001, LST-002, CAL-001, PRG-003, NFR-002, DEC-007, DEC-009, DEC-013.
- **Owner:** `main.py`.
- **Tests first:** `test_ext_001_start_reads_every_cv_and_lists_the_candidates`, `test_job_001_start_reads_every_job_description_and_lists_them`, `test_cal_001_start_calculates_attributes_that_the_api_returns`, `test_prg_003_later_requests_make_no_llm_call`, `test_dec_007_app_is_created_only_from_a_finished_workspace`, `test_dec_013_server_starts_on_the_settings_host`, `test_nfr_002_log_output_never_contains_the_api_key`.
- **Build:** install and pin `uvicorn`. `main.py` loads config, sets up logging, builds the objects, runs the pipeline, creates the app and starts the server, with no logic. The end-to-end test drives the same wiring with a fake LLM and temporary folders. Fill the README sections Setup (conda, `requirements.txt`, `config/.env`, the OpenAI key) and How to run.
- **Gate:** the tests and the checks pass; the README lists the run command.

### M12 — Front end: shell, lists, job view

- **Refs:** LST-001, LST-002, JOB-002, JOB-003, RNK-003, REC-001, DEC-002, DEC-012, DEC-019, DEC-020, `docs/frontend/README.md`.
- **Owner:** `src/web/` (`index.html`, `css/`, and `js/` up to `job-view.js`).
- **Tests first:** `tests/unit/format.test.js`; in `tests/e2e/ui/`: `test_lst_001_ui_lists_the_job_descriptions`, `test_lst_002_ui_lists_the_candidates`, `test_job_002_ui_selecting_a_job_shows_ranked_candidates_best_first`, `test_job_003_ui_job_text_panel_is_above_the_cards`, `test_rnk_003_ui_card_shows_the_attributes`, `test_rec_001_ui_card_shows_the_recommendation`, `test_dec_019_header_stays_at_the_top_when_scrolled`, `test_dec_019_file_name_sits_below_the_name_in_a_smaller_size`.
- **Build:** install and pin `playwright` (drives the installed Edge or Chrome, no download). Build the page from the mockups in `docs/frontend/` with CSS tokens in `theme.css`, no inline styles, and data only through `api.js`.
- **Gate:** the tests and the checks (ESLint, tsc, Prettier, Stylelint, `node --test`) pass; the browser tests run against the app with a fake workspace.

### M13 — Front end: candidate view and failures

- **Refs:** CND-001, CND-002, CND-003, ERR-001, ERR-002, MIS-001, MIS-002, DEC-015, `docs/frontend/README.md`.
- **Owner:** `src/web/js/candidate-view.js`, `src/web/js/failures-view.js`.
- **Tests first:** in `tests/e2e/ui/`: `test_cnd_001_ui_shows_the_raw_cv`, `test_cnd_002_ui_shows_extracted_and_calculated_attributes`, `test_cnd_003_ui_shows_ranked_jobs_best_first`, `test_err_001_ui_failure_panel_names_the_cause`, `test_err_002_ui_keeps_the_lists_and_shows_not_available`, `test_mis_001_ui_shows_not_available_for_null`, `test_mis_002_ui_candidate_without_a_score_is_ranked_last`, `test_dec_015_ui_shows_present_only_for_a_current_job`, `test_job_and_candidate_with_the_same_id_show_the_right_view`.
- **Build:** the candidate view and the failure panel, following the mockups; "Present" only for a current job, "Not available" for `null`.
- **Gate:** the tests and the checks pass.

### M14 — Evaluation

- **Refs:** NFR-004, NFR-005, RNK-001, EXT-009, DEC-017, design section 3 (evaluation files).
- **Owner:** `src/evaluation.py`, with `main.py` (`--evaluate`), `src/file_reader.py` (the two files) and `.gitignore`.
- **Tests first:** `test_nfr_004_passes_when_two_of_the_top_three_are_relevant`, `test_nfr_004_fails_when_only_one_is`, `test_nfr_004_fails_with_no_labeled_job_description`, `test_nfr_005_match_rate_over_gold_jobs`, `test_nfr_005_failed_extraction_counts_as_misses`, `test_nfr_005_extra_extracted_jobs_are_not_penalized`, `test_nfr_005_fails_with_no_gold_job`, `test_report_has_counts_and_never_cv_content`, `test_unreadable_or_malformed_file_stops_before_any_llm_call`, `test_evaluate_exits_1_when_a_check_fails_and_0_when_all_pass`.
- **Build:** a pure module that parses `ground_truth.tsv` and `gold_jobs.json` and checks the workspace; `--evaluate` builds the same workspace as the server, prints the report and exits. Add the `.gitignore` exception so `data/sample/gold_jobs.json` is committed as it stands, with its attribution line unchanged. Document `--evaluate` in the README.
- **Gate:** the tests and the checks pass; the report says NFR-005 counts only after the user reviews the gold file; the manual run is the user's, and no result is recorded in `docs/design.md`.

### M15 — Sample builder

- **Refs:** DEC-010, spec section 1 (sample).
- **Owner:** `scripts/build_sample.py`.
- **Tests first:** `test_dec_010_builds_the_requested_jobs_and_cvs_with_a_txt_extension`, `test_dec_010_writes_ground_truth_and_attribution`, `test_dec_010_refuses_a_job_with_fewer_than_three_labeled_cvs`, `test_dec_010_leaves_the_raw_files_unchanged`.
- **Build:** `python scripts/build_sample.py RAW OUT --jobs ID... --cvs ID...`, using invented files in temporary folders for the tests.
- **Gate:** the tests and the checks pass; run once into a scratch folder with jobs 29243, 32447, 38671 and the 10 CVs of `data/sample/ground_truth.tsv`, and the output matches the existing `data/sample/`; delete the scratch folder.

### M16 — Lock file and CI

- **Refs:** DEC-018, `CLAUDE.md` (Dependencies, Testing).
- **Owner:** `scripts/lock.py`, `constraints.txt`, `scripts/check.py`, `.github/workflows/check.yml`, `CLAUDE.md`.
- **Tests first:** `test_dec_018_lock_check_passes_when_every_pin_is_in_constraints`, `test_dec_018_lock_check_fails_on_a_missing_or_different_version`, `test_dec_018_lock_script_writes_the_freeze_output`.
- **Build:** the thin `pip freeze` wrapper; generate `constraints.txt` from the conda environment; add the lock check to `scripts/check.py`; add the workflow described in DEC-018 with each action pinned to an exact version resolved at build time. Edit `CLAUDE.md` with the two changes the user approved (the `constraints.txt` rule under Dependencies, and the directory table rows for `lock.py`, `.github/` and `constraints.txt`).
- **Gate:** the tests and the checks pass; the README mentions `scripts/lock.py`. The edits to `scripts/check.py` and `CLAUDE.md` are on the "ask" list in `.claude/settings.json`; if they are denied, block the milestone. The first CI run is watched by the user.
