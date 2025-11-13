import React from 'react';
import { CreditCard, Download, AlertCircle, Check } from 'lucide-react';

const ParentBilling = () => {
  // Mock subscription data
  const subscription = {
    planName: 'Elite Plan',
    status: 'Active',
    pricePerMonth: 79.99,
    playersCovered: 1,
    nextBillingDate: '2024-04-01',
    startDate: '2024-01-01'
  };

  // Mock payment history
  const paymentHistory = [
    { id: '1', date: '2024-03-01', amount: 79.99, status: 'Paid', invoiceUrl: '#' },
    { id: '2', date: '2024-02-01', amount: 79.99, status: 'Paid', invoiceUrl: '#' },
    { id: '3', date: '2024-01-01', amount: 79.99, status: 'Paid', invoiceUrl: '#' },
    { id: '4', date: '2023-12-01', amount: 79.99, status: 'Paid', invoiceUrl: '#' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'bg-green-100 text-green-800';
      case 'Paused': return 'bg-yellow-100 text-yellow-800';
      case 'Canceled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Current Subscription</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-1">{subscription.planName}</h3>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${
                  getStatusColor(subscription.status)
                }`}>
                  {subscription.status}
                </span>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold text-blue-600">${subscription.pricePerMonth}</p>
                <p className="text-sm text-gray-600">/month</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Check className="w-4 h-4 text-green-600" />
                <span>{subscription.playersCovered} Player{subscription.playersCovered > 1 ? 's' : ''} Covered</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Check className="w-4 h-4 text-green-600" />
                <span>AI-powered training plans</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Check className="w-4 h-4 text-green-600" />
                <span>Video analysis & feedback</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Check className="w-4 h-4 text-green-600" />
                <span>Monthly assessments</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <Check className="w-4 h-4 text-green-600" />
                <span>Direct coach messaging</span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Member since</p>
              <p className="text-lg font-bold text-gray-800">{subscription.startDate}</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Next billing date</p>
              <p className="text-lg font-bold text-gray-800">{subscription.nextBillingDate}</p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition">
            Upgrade Plan
          </button>
          <button className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition">
            Pause Subscription
          </button>
          <button className="px-6 py-2 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition">
            Cancel Subscription
          </button>
        </div>
      </div>

      {/* Payment Method */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Payment Method</h3>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <CreditCard className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <p className="font-medium text-gray-800">Visa ending in 4242</p>
            <p className="text-sm text-gray-600">Expires 12/2025</p>
          </div>
          <button className="ml-auto px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition">
            Update
          </button>
        </div>
      </div>

      {/* Payment History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Payment History</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Date</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Amount</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-700">Invoice</th>
              </tr>
            </thead>
            <tbody>
              {paymentHistory.map((payment) => (
                <tr key={payment.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm text-gray-700">{payment.date}</td>
                  <td className="py-3 px-4 text-sm font-medium text-gray-900">${payment.amount}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                      {payment.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1 ml-auto">
                      <Download className="w-4 h-4" />
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Billing Info */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <p className="font-medium text-gray-800 mb-1">Billing Information</p>
            <p className="text-sm text-gray-700">
              Your subscription will automatically renew on {subscription.nextBillingDate}. You can cancel anytime before the renewal date.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentBilling;