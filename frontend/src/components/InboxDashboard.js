import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Inbox, Send, Mail, MailOpen, Trash2, Reply, Users, Search, X } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const InboxDashboard = () => {
  const [view, setView] = useState('inbox'); // 'inbox', 'sent', 'compose', 'read'
  const [messages, setMessages] = useState([]);
  const [sentMessages, setSentMessages] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  
  // Compose form state
  const [recipients, setRecipients] = useState([]);
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [replyTo, setReplyTo] = useState(null);
  
  const { user, isAuthenticated } = useAuth();
  
  useEffect(() => {
    if (isAuthenticated) {
      fetchInbox();
      fetchContacts();
    }
  }, [isAuthenticated]);
  
  const fetchInbox = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/messages/inbox`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.messages || []);
      setUnreadCount(response.data.unread || 0);
    } catch (error) {
      console.error('Error fetching inbox:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchSentMessages = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/messages/sent`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSentMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error fetching sent messages:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchContacts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/messages/contacts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContacts(response.data.contacts || []);
    } catch (error) {
      console.error('Error fetching contacts:', error);
    }
  };
  
  const handleSendMessage = async () => {
    if (recipients.length === 0 || !subject || !message) {
      alert('Please fill in all fields');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      
      // Determine recipient type
      let recipientType = 'individual';
      const selectedContact = contacts.find(c => c.username === recipients[0]);
      if (selectedContact?.type) {
        recipientType = selectedContact.type;
      }
      
      // For group messages, get all member usernames
      let recipientUsernames = recipients;
      if (selectedContact?.members) {
        recipientUsernames = selectedContact.members;
      }
      
      await axios.post(`${API}/messages/send`, {
        recipient_usernames: recipientUsernames,
        recipient_type: recipientType,
        subject: subject,
        message: message,
        replied_to: replyTo?.id || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      alert('Message sent successfully!');
      setRecipients([]);
      setSubject('');
      setMessage('');
      setReplyTo(null);
      setView('inbox');
      fetchInbox();
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  const handleReadMessage = async (msg) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/messages/message/${msg.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSelectedMessage(response.data);
      setView('read');
      fetchInbox(); // Refresh to update read status
    } catch (error) {
      console.error('Error reading message:', error);
    }
  };
  
  const handleDeleteMessage = async (messageId) => {
    if (!window.confirm('Are you sure you want to delete this message?')) return;
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/messages/message/${messageId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('Message deleted');
      setView('inbox');
      setSelectedMessage(null);
      fetchInbox();
    } catch (error) {
      console.error('Error deleting message:', error);
      alert('Failed to delete message');
    }
  };
  
  const handleReply = (msg) => {
    setReplyTo(msg);
    setRecipients([msg.sender_username]);
    setSubject(`Re: ${msg.subject}`);
    setMessage(`\n\n--- Original Message ---\nFrom: ${msg.sender_name}\nDate: ${new Date(msg.timestamp).toLocaleString()}\n\n${msg.message}`);
    setView('compose');
  };
  
  const filteredContacts = contacts.filter(contact =>
    contact.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    contact.username.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Inbox</h1>
        <Button onClick={() => { setView('compose'); setReplyTo(null); setRecipients([]); setSubject(''); setMessage(''); }}>
          <Send className="w-4 h-4 mr-2" />
          Compose
        </Button>
      </div>
      
      {/* Navigation Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => { setView('inbox'); fetchInbox(); }}
          className={`px-4 py-2 font-medium ${view === 'inbox' || view === 'read' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'}`}
        >
          <Inbox className="w-4 h-4 inline mr-2" />
          Inbox {unreadCount > 0 && <Badge className="ml-2">{unreadCount}</Badge>}
        </button>
        <button
          onClick={() => { setView('sent'); fetchSentMessages(); }}
          className={`px-4 py-2 font-medium ${view === 'sent' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'}`}
        >
          <Send className="w-4 h-4 inline mr-2" />
          Sent
        </button>
      </div>
      
      {/* Inbox View */}
      {view === 'inbox' && (
        <Card>
          <CardHeader>
            <CardTitle>Messages</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : messages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No messages yet</div>
            ) : (
              <div className="space-y-2">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    onClick={() => handleReadMessage(msg)}
                    className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${!msg.is_read ? 'bg-blue-50 border-blue-200' : ''}`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {!msg.is_read ? <Mail className="w-4 h-4 text-blue-600" /> : <MailOpen className="w-4 h-4 text-gray-400" />}
                          <span className="font-semibold">{msg.sender_name}</span>
                          {msg.recipient_type !== 'individual' && <Badge variant="secondary">{msg.recipient_type}</Badge>}
                        </div>
                        <div className="font-medium mt-1">{msg.subject}</div>
                        <div className="text-sm text-gray-600 mt-1 truncate">{msg.message.substring(0, 100)}...</div>
                      </div>
                      <div className="text-sm text-gray-500">{new Date(msg.timestamp).toLocaleDateString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Sent View */}
      {view === 'sent' && (
        <Card>
          <CardHeader>
            <CardTitle>Sent Messages</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : sentMessages.length === 0 ? (
              <div className="text-center py-8 text-gray-500">No sent messages</div>
            ) : (
              <div className="space-y-2">
                {sentMessages.map((msg) => (
                  <div key={msg.id} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Send className="w-4 h-4 text-gray-400" />
                          <span className="font-medium">To: {msg.recipient_usernames.join(', ')}</span>
                          {msg.recipient_type !== 'individual' && <Badge>{msg.recipient_type}</Badge>}
                        </div>
                        <div className="font-medium mt-1">{msg.subject}</div>
                        <div className="text-sm text-gray-600 mt-1 truncate">{msg.message.substring(0, 100)}...</div>
                        <div className="text-xs text-gray-500 mt-2">
                          Read by {msg.read_count} of {msg.recipient_count}
                        </div>
                      </div>
                      <div className="text-sm text-gray-500">{new Date(msg.timestamp).toLocaleDateString()}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Read Message View */}
      {view === 'read' && selectedMessage && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>{selectedMessage.subject}</CardTitle>
                <div className="text-sm text-gray-600 mt-2">
                  From: <strong>{selectedMessage.sender_name}</strong> ({selectedMessage.sender_role})
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {new Date(selectedMessage.timestamp).toLocaleString()}
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => handleReply(selectedMessage)}>
                  <Reply className="w-4 h-4 mr-1" />
                  Reply
                </Button>
                <Button variant="outline" size="sm" onClick={() => handleDeleteMessage(selectedMessage.id)}>
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </Button>
                <Button variant="outline" size="sm" onClick={() => setView('inbox')}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">{selectedMessage.message}</div>
          </CardContent>
        </Card>
      )}
      
      {/* Compose View */}
      {view === 'compose' && (
        <Card>
          <CardHeader>
            <CardTitle>{replyTo ? 'Reply to Message' : 'Compose New Message'}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>To:</Label>
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Search contacts..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <div className="mt-2 space-y-1 max-h-40 overflow-y-auto">
                {filteredContacts.map((contact) => (
                  <div
                    key={contact.username}
                    onClick={() => {
                      if (!recipients.includes(contact.username)) {
                        setRecipients([contact.username]);
                        setSearchQuery('');
                      }
                    }}
                    className={`p-2 border rounded cursor-pointer hover:bg-gray-50 ${recipients.includes(contact.username) ? 'bg-blue-100 border-blue-500' : ''}`}
                  >
                    <div className="flex items-center gap-2">
                      {contact.type === 'team' || contact.type === 'parent_group' ? <Users className="w-4 h-4" /> : null}
                      <span className="font-medium">{contact.full_name}</span>
                      <Badge variant="secondary" className="text-xs">{contact.role}</Badge>
                    </div>
                  </div>
                ))}
              </div>
              {recipients.length > 0 && (
                <div className="mt-2 flex gap-2 flex-wrap">
                  {recipients.map((r) => {
                    const contact = contacts.find(c => c.username === r);
                    return (
                      <Badge key={r} className="flex items-center gap-1">
                        {contact?.full_name || r}
                        <X className="w-3 h-3 cursor-pointer" onClick={() => setRecipients(recipients.filter(x => x !== r))} />
                      </Badge>
                    );
                  })}
                </div>
              )}
            </div>
            
            <div>
              <Label>Subject:</Label>
              <Input
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Message subject"
              />
            </div>
            
            <div>
              <Label>Message:</Label>
              <Textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message here..."
                rows={8}
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleSendMessage}>
                <Send className="w-4 h-4 mr-2" />
                Send Message
              </Button>
              <Button variant="outline" onClick={() => setView('inbox')}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default InboxDashboard;
