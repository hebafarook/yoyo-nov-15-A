import React, { useState } from 'react';
import { Send, Paperclip, Mic, Bot, User } from 'lucide-react';

const CoachMessages = () => {
  const [selectedThread, setSelectedThread] = useState(null);
  const [messageText, setMessageText] = useState('');

  const threads = [
    {
      id: 1,
      playerName: 'Marcus Silva',
      lastMessage: 'Thanks Coach! Will focus on that drill tomorrow.',
      timestamp: '10 min ago',
      unread: 0,
      messages: [
        {
          id: 'm1',
          sender: 'coach',
          text: 'Great work today Marcus! Your sprint times are improving significantly.',
          timestamp: '2 hours ago'
        },
        {
          id: 'm2',
          sender: 'player',
          text: 'Thanks Coach! I\'ve been working extra on my acceleration.',
          timestamp: '1 hour ago'
        },
        {
          id: 'm3',
          sender: 'coach',
          text: 'I noticed. Let\'s add some resistance band work to build more power. I\'ll send you the drill video.',
          timestamp: '30 min ago'
        },
        {
          id: 'm4',
          sender: 'player',
          text: 'Thanks Coach! Will focus on that drill tomorrow.',
          timestamp: '10 min ago'
        }
      ]
    },
    {
      id: 2,
      playerName: 'Alex Johnson',
      lastMessage: 'Should I do the recovery session today?',
      timestamp: '1 hour ago',
      unread: 2,
      messages: [
        {
          id: 'm5',
          sender: 'player',
          text: 'Hi Coach, feeling some soreness in my hamstrings after yesterday.',
          timestamp: '2 hours ago'
        },
        {
          id: 'm6',
          sender: 'player',
          text: 'Should I do the recovery session today?',
          timestamp: '1 hour ago'
        }
      ]
    },
    {
      id: 3,
      playerName: 'David Chen',
      lastMessage: 'Looking forward to the next session!',
      timestamp: '3 hours ago',
      unread: 0,
      messages: []
    }
  ];

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    // Add message logic here
    setMessageText('');
  };

  if (selectedThread) {
    const thread = threads.find(t => t.id === selectedThread);
    
    return (
      <div className="space-y-6">
        <button
          onClick={() => setSelectedThread(null)}
          className="text-white/70 hover:text-white transition"
        >
          ← Back to Messages
        </button>

        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden">
          {/* Chat Header */}
          <div className="p-6 border-b border-white/10 bg-white/5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-full flex items-center justify-center font-bold">
                {thread.playerName.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h3 className="font-bold text-lg">{thread.playerName}</h3>
                <p className="text-sm text-white/60">Active now</p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="p-6 space-y-4 h-[500px] overflow-y-auto">
            {thread.messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.sender === 'coach' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div className={`max-w-[70%] ${
                  message.sender === 'coach'
                    ? 'bg-gradient-to-r from-[#4DFF91] to-[#007BFF] text-[#0C1A2A]'
                    : 'bg-white/10 text-white'
                } rounded-2xl p-4`}>
                  <p className="text-sm mb-1">{message.text}</p>
                  <p className={`text-xs ${
                    message.sender === 'coach' ? 'text-[#0C1A2A]/60' : 'text-white/60'
                  }`}>
                    {message.timestamp}
                  </p>
                </div>
              </div>
            ))}

            {/* AI Assistant Suggestion */}
            <div className="bg-gradient-to-r from-[#007BFF]/20 to-[#4DFF91]/20 border border-[#4DFF91]/30 rounded-2xl p-4">
              <div className="flex items-start gap-3">
                <Bot className="w-5 h-5 text-[#4DFF91] mt-0.5" />
                <div>
                  <div className="text-xs text-[#4DFF91] font-medium mb-1">AI Assistant</div>
                  <p className="text-sm text-white/90">
                    Suggested response: "Yes, do a light recovery session with foam rolling and 20 minutes of easy jogging. Monitor your soreness level."
                  </p>
                  <button className="text-xs text-[#4DFF91] hover:text-[#4DFF91]/80 mt-2">
                    Use this response
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-white/10 bg-white/5">
            <form onSubmit={handleSendMessage} className="flex gap-3">
              <button
                type="button"
                className="p-3 bg-white/10 hover:bg-white/20 rounded-xl transition"
                title="Voice Message"
              >
                <Mic className="w-5 h-5" />
              </button>
              <button
                type="button"
                className="p-3 bg-white/10 hover:bg-white/20 rounded-xl transition"
                title="Attach File"
              >
                <Paperclip className="w-5 h-5" />
              </button>
              <input
                type="text"
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
              />
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-medium text-[#0C1A2A] hover:shadow-lg hover:shadow-[#4DFF91]/30 transition flex items-center gap-2"
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
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Messages</h2>
        <p className="text-white/60 mt-1">Communicate with your players</p>
      </div>

      {/* Thread List */}
      <div className="space-y-3">
        {threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => setSelectedThread(thread.id)}
            className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:scale-[1.02] transition cursor-pointer"
          >
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-full flex items-center justify-center font-bold">
                {thread.playerName.split(' ').map(n => n[0]).join('')}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold">{thread.playerName}</h3>
                  <span className="text-xs text-white/60">{thread.timestamp}</span>
                </div>
                <p className="text-sm text-white/70 line-clamp-1">{thread.lastMessage}</p>
              </div>
              {thread.unread > 0 && (
                <div className="w-6 h-6 bg-[#4DFF91] rounded-full flex items-center justify-center text-xs font-bold text-[#0C1A2A]">
                  {thread.unread}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CoachMessages;