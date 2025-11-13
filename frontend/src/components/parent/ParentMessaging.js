import React, { useState } from 'react';
import { Send, Paperclip, User } from 'lucide-react';

const ParentMessaging = ({ child }) => {
  const [selectedThread, setSelectedThread] = useState(null);
  const [messageText, setMessageText] = useState('');

  // Mock message threads
  const threads = [
    {
      id: '1',
      playerName: 'Alex Smith',
      subject: 'Training Progress Update',
      lastMessage: 'Great work this week! Showing improvement in sprint times.',
      timestamp: '2024-03-18 14:30',
      unreadCount: 0,
      messages: [
        {
          id: 'm1',
          senderRole: 'Parent',
          senderName: 'You',
          timestamp: '2024-03-18 10:00',
          text: 'Hi Coach, how is Alex doing with the new training plan?',
          attachments: []
        },
        {
          id: 'm2',
          senderRole: 'Coach',
          senderName: 'Coach Mike',
          timestamp: '2024-03-18 14:30',
          text: 'Great work this week! Showing improvement in sprint times. The focus on left-foot finishing is paying off. Keep up the consistency!',
          attachments: []
        }
      ]
    },
    {
      id: '2',
      playerName: 'Alex Smith',
      subject: 'Knee Injury Update',
      lastMessage: 'Thanks for letting me know. Let\'s adjust the plan.',
      timestamp: '2024-03-15 09:15',
      unreadCount: 1,
      messages: [
        {
          id: 'm3',
          senderRole: 'Parent',
          senderName: 'You',
          timestamp: '2024-03-15 08:00',
          text: 'Alex mentioned some knee discomfort after yesterday\'s session. Should we rest or continue light training?',
          attachments: []
        },
        {
          id: 'm4',
          senderRole: 'Coach',
          senderName: 'Coach Mike',
          timestamp: '2024-03-15 09:15',
          text: 'Thanks for letting me know. Let\'s adjust the plan. No sprinting for 2 days, focus on ball control and passing drills. Monitor and let me know if it persists.',
          attachments: []
        }
      ]
    },
    {
      id: '3',
      playerName: 'Alex Smith',
      subject: 'Assessment Schedule',
      lastMessage: 'Assessment confirmed for next Monday at 10am',
      timestamp: '2024-03-12 16:45',
      unreadCount: 0,
      messages: [
        {
          id: 'm5',
          senderRole: 'System',
          senderName: 'YoYo Elite System',
          timestamp: '2024-03-12 16:45',
          text: 'New assessment scheduled: March 25, 2024 at 10:00 AM. Please ensure Alex arrives 15 minutes early.',
          attachments: []
        }
      ]
    }
  ];

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;

    // Add message logic here
    alert('Message sent!');
    setMessageText('');
  };

  if (selectedThread) {
    const thread = threads.find(t => t.id === selectedThread);
    
    return (
      <div className="space-y-6">
        <button
          onClick={() => setSelectedThread(null)}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Messages
        </button>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Thread Header */}
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-800">{thread.subject}</h2>
            <p className="text-sm text-gray-600">Regarding: {thread.playerName}</p>
          </div>

          {/* Messages */}
          <div className="p-6 space-y-4 max-h-[500px] overflow-y-auto">
            {thread.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.senderRole === 'Parent' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div className={`max-w-[70%] ${
                  message.senderRole === 'Parent' ? 'bg-blue-600 text-white' : message.senderRole === 'System' ? 'bg-gray-100 text-gray-700' : 'bg-gray-200 text-gray-800'
                } rounded-lg p-4`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-sm">{message.senderName}</span>
                    <span className={`text-xs ${
                      message.senderRole === 'Parent' ? 'text-blue-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp}
                    </span>
                  </div>
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-gray-200">
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <button
                type="button"
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <Paperclip className="w-5 h-5 text-gray-600" />
              </button>
              <input
                type="text"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Messages</h2>
        <p className="text-gray-600">Communicate with coaches about {child.first_name}'s training</p>
      </div>

      {/* Thread List */}
      <div className="space-y-3">
        {threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => setSelectedThread(thread.id)}
            className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-start gap-3 flex-1">
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                  <User className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-gray-800">{thread.subject}</h3>
                    {thread.unreadCount > 0 && (
                      <span className="px-2 py-0.5 bg-red-600 text-white rounded-full text-xs font-bold">
                        {thread.unreadCount}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{thread.playerName}</p>
                  <p className="text-sm text-gray-700 line-clamp-2">{thread.lastMessage}</p>
                </div>
              </div>
              <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                {thread.timestamp}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParentMessaging;