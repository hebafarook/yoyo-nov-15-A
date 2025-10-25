from datetime import datetime, date, time, timezone
from typing import Dict, Any

def prepare_for_mongo(data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare data for MongoDB storage by converting Python objects to serializable formats"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, time):
                result[key] = value.strftime('%H:%M:%S')
            elif isinstance(value, dict):
                result[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                result[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result
    return data

def parse_from_mongo(data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse data from MongoDB by converting string dates back to Python objects"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if key in ['created_at', 'updated_at', 'test_date', 'completion_date', 'measurement_date', 
                      'start_date', 'end_date', 'assessment_date', 'program_start_date', 'next_assessment_date', 'retest_date', 'date']:
                if isinstance(value, str):
                    try:
                        # Handle ISO format with timezone
                        if value.endswith('Z'):
                            result[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            result[key] = datetime.fromisoformat(value)
                    except ValueError:
                        result[key] = value
                else:
                    result[key] = value
            elif isinstance(value, dict):
                result[key] = parse_from_mongo(value)
            elif isinstance(value, list):
                result[key] = [parse_from_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result
    return data