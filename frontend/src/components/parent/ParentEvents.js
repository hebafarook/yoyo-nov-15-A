import React, { useState } from 'react';
import { Calendar, MapPin, Clock, Trophy, Activity, FileText } from 'lucide-react';

const ParentEvents = ({ child }) => {
  const [viewMode, setViewMode] = useState('list');

  // Mock events data
  const events = [
    {
      id: '1',
      title: 'Match vs Tigers FC',
      type: 'Match',
      startDateTime: '2024-03-25T15:00:00',
      endDateTime: '2024-03-25T17:00:00',
      location: 'City Stadium, Field 3',
      description: 'U14 League match - arrive 30 minutes early for warm-up'
    },
    {
      id: '2',
      title: 'Monthly Assessment',
      type: 'Assessment',
      startDateTime: '2024-03-28T10:00:00',
      endDateTime: '2024-03-28T12:00:00',
      location: 'Training Center',
      description: 'Comprehensive skill and fitness assessment with Coach Mike'
    },
    {
      id: '3',
      title: 'Spring Tournament',
      type: 'Tournament',
      startDateTime: '2024-04-05T09:00:00',
      endDateTime: '2024-04-07T18:00:00',
      location: 'Regional Sports Complex',
      description: '3-day tournament - Schedule and details will be shared closer to date'
    },
    {
      id: '4',
      title: 'Speed & Agility Training',
      type: 'Training',
      startDateTime: '2024-03-20T16:00:00',
      endDateTime: '2024-03-20T17:30:00',
      location: 'Training Center',
      description: 'Focused session on acceleration and change of direction'
    },
    {
      id: '5',
      title: 'Parent Info Session',
      type: 'Announcement',
      startDateTime: '2024-04-10T19:00:00',
      endDateTime: '2024-04-10T20:30:00',
      location: 'Online (Zoom link to be shared)',
      description: 'Q&A session about summer training programs and tournament schedule'
    }
  ];

  const getEventTypeIcon = (type) => {
    switch (type) {
      case 'Match': return <Trophy className="w-5 h-5" />;
      case 'Assessment': return <FileText className="w-5 h-5" />;
      case 'Training': return <Activity className="w-5 h-5" />;
      case 'Tournament': return <Trophy className="w-5 h-5" />;
      case 'Announcement': return <Calendar className="w-5 h-5" />;
      default: return <Calendar className="w-5 h-5" />;
    }
  };

  const getEventTypeColor = (type) => {
    switch (type) {
      case 'Match': return 'bg-green-100 text-green-800';
      case 'Assessment': return 'bg-blue-100 text-blue-800';
      case 'Training': return 'bg-purple-100 text-purple-800';
      case 'Tournament': return 'bg-red-100 text-red-800';
      case 'Announcement': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDateTime = (datetime) => {
    const date = new Date(datetime);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Events</h2>
            <p className="text-gray-600">Upcoming matches, training, and assessments</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              List View
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                viewMode === 'calendar' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Calendar View
            </button>
          </div>
        </div>

        <button className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition">
          Sync to Calendar
        </button>
      </div>

      {/* List View */}
      {viewMode === 'list' && (
        <div className="space-y-4">
          {events.map((event) => {
            const { date, time } = formatDateTime(event.startDateTime);
            return (
              <div key={event.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    getEventTypeColor(event.type)
                  }`}>
                    {getEventTypeIcon(event.type)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-bold text-gray-800 text-lg mb-1">{event.title}</h3>
                        <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                          getEventTypeColor(event.type)
                        }`}>
                          {event.type}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2 mt-3">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Calendar className="w-4 h-4 text-gray-500" />
                        <span>{date}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <span>{time}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <MapPin className="w-4 h-4 text-gray-500" />
                        <span>{event.location}</span>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600 mt-3">{event.description}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Calendar View Placeholder */}
      {viewMode === 'calendar' && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-800 mb-2">Calendar View</h3>
          <p className="text-gray-600">Monthly calendar visualization will be available soon</p>
        </div>
      )}
    </div>
  );
};

export default ParentEvents;