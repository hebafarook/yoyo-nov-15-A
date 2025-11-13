import React, { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

const PlayerMessages = () => {
  const [selectedChat, setSelectedChat] = useState(null);
  const [messageText, setMessageText] = useState('');

  const conversations = [
    {
      id: 'coach',
      name: 'Coach Mike',
      avatar: 'CM',
      lastMessage: 'Great work today! Keep it up.',
      time: '2h ago',
      unread: 0,
      messages: [
        { id: 1, sender: 'coach', text: 'Hey! How are you feeling after yesterday\'s session?', time: '10:00 AM' },
        { id: 2, sender: 'player', text: 'Feeling good! A bit tired but excited for today.', time: '10:15 AM' },
        { id: 3, sender: 'coach', text: 'Great work today! Keep it up.', time: '2:00 PM' }
      ]
    },
    {
      id: 'team',
      name: 'Team Group',
      avatar: 'T',
      lastMessage: 'Match on Saturday at 3pm',
      time: '5h ago',
      unread: 2,
      messages: [
        { id: 1, sender: 'coach', text: 'Match on Saturday at 3pm. Please arrive by 2pm.', time: '1:00 PM' }
      ]
    },
    {
      id: 'ai',
      name: 'YoYo AI Assistant',
      avatar: '🤖',
      lastMessage: 'How can I help you?',
      time: '1d ago',
      unread: 0,
      messages: [
        { id: 1, sender: 'ai', text: 'Hi! I\'m your AI training assistant. I can help you with drills, technique tips, and answer questions about your training plan.', time: 'Yesterday' }
      ]
    }
  ];

  const quickReplies = [
    'I finished my session',
    'I need help with this skill',
    'Can you explain this drill?'
  ];

  const handleSend = () => {
    if (!messageText.trim()) return;
    // Add message logic here
    setMessageText('');
  };

  if (selectedChat) {
    const chat = conversations.find(c => c.id === selectedChat);
    
    return (
      <div className="max-w-4xl mx-auto h-screen flex flex-col bg-white">
        {/* Chat Header */}
        <div className="p-4 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white border-b-2 border-yellow-400">
          <button
            onClick={() => setSelectedChat(null)}
            className="text-white/80 hover:text-white mb-2 text-sm"
          >
            ← Back
          </button>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-yellow-400 rounded-full flex items-center justify-center text-indigo-900 font-bold text-lg">
              {chat.avatar}
            </div>
            <div>
              <h3 className="font-bold text-lg">{chat.name}</h3>
              <p className="text-sm text-white/80">Online</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          {chat.messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.sender === 'player' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                message.sender === 'player'
                  ? 'bg-blue-600 text-white'
                  : message.sender === 'ai'
                  ? 'bg-purple-100 text-gray-800'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}>
                <p className="text-sm mb-1">{message.text}</p>
                <p className={`text-xs ${
                  message.sender === 'player' ? 'text-white/80' : 'text-gray-500'
                }`}>
                  {message.time}
                </p>
              </div>
            </div>
          ))}

          {/* Quick Replies for AI */}
          {chat.id === 'ai' && (
            <div className="flex flex-wrap gap-2 mt-4">
              {quickReplies.map((reply, idx) => (
                <button
                  key={idx}
                  onClick={() => setMessageText(reply)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-full text-sm hover:bg-gray-50 transition"
                >
                  {reply}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Message Input */}
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={handleSend}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-2">Messages</h2>
        <p className="text-white/90">Chat with your coach and AI assistant</p>
      </div>

      <div className="space-y-3">
        {conversations.map((chat) => (
          <div
            key={chat.id}
            onClick={() => setSelectedChat(chat.id)}
            className="bg-white rounded-2xl p-4 shadow-lg border border-gray-200 hover:shadow-xl transition cursor-pointer"
          >
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {chat.avatar}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-gray-800">{chat.name}</h3>
                  <span className="text-xs text-gray-500">{chat.time}</span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-1">{chat.lastMessage}</p>
              </div>
              {chat.unread > 0 && (
                <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  {chat.unread}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlayerMessages;