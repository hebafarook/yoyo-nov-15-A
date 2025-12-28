# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed
- Training endpoints now return HTTP 404 when a required assessment is missing (was 500)
- Elite training endpoints now return HTTP 404 for missing testing data and match schedules (was 500)
- Elite training RTP protocol endpoint returns HTTP 400 for invalid stage (was 500)

### Changed
- Refactored `elite_training_routes.py` to service/repository pattern (PR 2.5)
- Refactored `training_routes.py` to service/repository pattern (PR 2.4)
- Refactored `assessment_routes.py` to service/repository pattern (PR 2.3)
- Added backward compatibility for legacy assessment endpoints (`/api/assessments/public/*`)
- Added `assessment_date` field as alias for `created_at` in `PlayerAssessment` model
