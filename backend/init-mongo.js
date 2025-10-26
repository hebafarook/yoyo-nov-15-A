// Initialize MongoDB with collections and indexes
db = db.getSiblingDB('soccer_training_db');

// Create collections with indexes for performance

// Assessments collection
db.createCollection('assessments');
db.assessments.createIndex({ "player_name": 1 });
db.assessments.createIndex({ "created_at": -1 });
db.assessments.createIndex({ "player_name": 1, "created_at": -1 });

// VO2 Benchmarks collection
db.createCollection('vo2_benchmarks');
db.vo2_benchmarks.createIndex({ "player_id": 1 });
db.vo2_benchmarks.createIndex({ "test_date": -1 });
db.vo2_benchmarks.createIndex({ "player_id": 1, "test_date": -1 });

// Periodized Programs collection
db.createCollection('periodized_programs');
db.periodized_programs.createIndex({ "player_id": 1 });
db.periodized_programs.createIndex({ "created_at": -1 });
db.periodized_programs.createIndex({ "player_id": 1, "created_at": -1 });

// Daily Progress collection
db.createCollection('daily_progress');
db.daily_progress.createIndex({ "player_id": 1 });
db.daily_progress.createIndex({ "date": -1 });
db.daily_progress.createIndex({ "player_id": 1, "date": -1 });

// Weekly Progress collection
db.createCollection('weekly_progress');
db.weekly_progress.createIndex({ "player_id": 1 });
db.weekly_progress.createIndex({ "created_at": -1 });
db.weekly_progress.createIndex({ "player_id": 1, "week_number": 1 });

// Performance Metrics collection
db.createCollection('performance_metrics');
db.performance_metrics.createIndex({ "player_id": 1 });
db.performance_metrics.createIndex({ "measurement_date": -1 });
db.performance_metrics.createIndex({ "player_id": 1, "metric_name": 1, "measurement_date": -1 });

// Training Programs collection (legacy)
db.createCollection('training_programs');
db.training_programs.createIndex({ "player_id": 1 });
db.training_programs.createIndex({ "created_at": -1 });

// Users collection
db.createCollection('users');
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

// User Profiles collection
db.createCollection('user_profiles');
db.user_profiles.createIndex({ "user_id": 1 }, { unique: true });

// Saved Reports collection
db.createCollection('saved_reports');
db.saved_reports.createIndex({ "user_id": 1 });
db.saved_reports.createIndex({ "saved_at": -1 });
db.saved_reports.createIndex({ "user_id": 1, "player_name": 1 });

print('MongoDB initialization completed successfully!');