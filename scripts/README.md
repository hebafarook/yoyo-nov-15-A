# Scripts Directory

## Overview
This directory contains test scripts, debugging utilities, and manual validation tools.

**⚠️ Important**: These are NOT automated tests. They are:
- Manual testing scripts
- Debugging utilities
- One-off validation tools
- Interactive exploration scripts

For automated tests, see `/app/tests/`

## Script Categories

### Backend API Testing
Manual scripts to test backend endpoints:
- `ai_coach_backend_test.py` - AI coach features
- `ai_coach_insights_final_test.py` - AI insights validation
- `ai_coach_insights_focused_test.py` - Focused AI testing
- `ai_coach_player_insights_test.py` - Player insights
- `arabic_backend_test.py` - Arabic/RTL support
- `backend_test.py` - General backend testing
- `comprehensive_backend_test.py` - Full backend validation

### Feature Validation
Scripts for specific feature testing:
- `comprehensive_benchmark_test.py` - Benchmark system
- `comprehensive_program_test.py` - Training programs
- `comprehensive_validation_test.py` - General validation
- `training_program_test.py` - Program generation
- `training_session_test.py` - Session management

### Bug Investigation
Debugging and troubleshooting:
- `debug_program_structure.py` - Program structure analysis
- `error_debug_test.py` - Error investigation
- `vo2_edge_case_tests.py` - VO2 edge cases

### User Flow Testing
End-to-end flow validation:
- `forgot_password_test.py` - Password reset flow
- `get_started_routing_test.py` - Onboarding routing
- `interactive_program_test.py` - Interactive features
- `multi_user_backend_test.py` - Multi-user scenarios

### Specialized Testing
- `dynamic_duration_test.py` - Duration calculations
- `dynamic_frequency_test.py` - Frequency handling
- `dynamic_report_test.py` - Report generation
- `freq3_test.py` - Frequency edge cases
- `detailed_analysis_test.py` - Analysis features
- `youth_handbook_test.py` - Youth features
- `yoyo_fire_boy_test.py` - Specific scenario testing
- `test_benchmark_only.py` - Benchmark isolation

## Usage

### Running a script
```bash
cd /app/scripts
python script_name.py
```

### Common patterns
Most scripts:
1. Connect to backend API
2. Create test data
3. Execute test scenario
4. Print results
5. May require manual verification

### Example
```bash
# Run AI coach testing
python ai_coach_backend_test.py

# Check output manually
# Verify results in console
```

## Key Differences from Tests

| Scripts (this dir) | Tests (/app/tests) |
|-------------------|--------------------|
| Manual execution | Automated |
| Interactive | Unattended |
| Print to console | Assert/Fail |
| One-off validation | Repeatable |
| Human verification | Machine verification |
| Debugging focus | Quality assurance |

## Best Practices

### When to use scripts
- Exploring new features
- Debugging complex issues
- Manual validation needed
- Interactive testing
- One-time data verification

### When to write tests instead
- Repeatable validation
- CI/CD integration
- Regression prevention
- Automated quality checks

## Maintenance

These scripts:
- May become outdated as APIs change
- Are not maintained for automation
- Should be migrated to `/app/tests/` if automation needed
- Can be deleted if no longer useful

## Migration to Tests

If a script proves valuable for automation:
1. Extract core assertions
2. Create proper test in `/app/tests/`
3. Use pytest fixtures
4. Remove print statements
5. Add proper error handling
6. Mark script as deprecated

## Contributing

When adding scripts:
1. Give descriptive names
2. Add comments explaining purpose
3. Include usage instructions
4. Note if manual verification needed
5. Update this README
