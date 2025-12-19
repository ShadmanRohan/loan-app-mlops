import React, { useState, useEffect } from 'react';
import { DollarSign, Phone, Mail, Calendar, Briefcase, Home, CreditCard, CheckCircle, XCircle, Menu, X, TrendingUp, User, Building, PiggyBank, AlertCircle, BarChart3, Sparkles } from 'lucide-react';
import Papa from 'papaparse';

export default function LoanApprovalUI() {
  const [selectedCustomer, setSelectedCustomer] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [customerList, setCustomerList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [shapExplanation, setShapExplanation] = useState(null);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [apiUrl] = useState('http://191.101.81.150:9001');

  useEffect(() => {
    const loadData = async () => {
      try {
        const fileContent = await window.fs.readFile('Loan.csv', { encoding: 'utf8' });
        const parsed = Papa.parse(fileContent, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true,
          delimitersToGuess: [',', '\t', '|', ';']
        });

        const cleanedData = parsed.data.map(row => {
          const cleanRow = {};
          Object.keys(row).forEach(key => {
            cleanRow[key.trim()] = row[key];
          });
          return cleanRow;
        });

        setCustomerList(cleanedData);
        setLoading(false);
      } catch (error) {
        console.error('Error loading CSV:', error);
        const sampleData = generateSampleData();
        setCustomerList(sampleData);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Auto-load SHAP explanation when customer changes
  useEffect(() => {
    if (customerList.length > 0 && selectedCustomer >= 0) {
      const customer = customerList[selectedCustomer];
      if (customer.LoanApproved !== 0 && customer.LoanApproved !== 1) {
        // Auto-get prediction for pending applications
        getPredictionWithExplanation(customer);
      } else {
        // Clear SHAP for already decided applications
        setShapExplanation(null);
      }
    }
  }, [selectedCustomer, customerList.length]);

  const generateSampleData = () => {
    const loanPurposes = ['Home', 'Auto', 'Business', 'Personal', 'Education'];
    const employmentStatuses = ['Employed', 'Self-Employed', 'Contract'];
    const maritalStatuses = ['Single', 'Married', 'Divorced'];
    const educationLevels = ['High School', 'Bachelor', 'Master', 'PhD'];
    const homeOwnership = ['Own', 'Rent', 'Mortgage'];
    
    return Array.from({ length: 50 }, (_, i) => ({
      ApplicationDate: `2025-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
      Age: Math.floor(Math.random() * 40) + 25,
      AnnualIncome: Math.floor(Math.random() * 150000) + 30000,
      CreditScore: Math.floor(Math.random() * 300) + 500,
      EmploymentStatus: employmentStatuses[Math.floor(Math.random() * employmentStatuses.length)],
      EducationLevel: educationLevels[Math.floor(Math.random() * educationLevels.length)],
      Experience: Math.floor(Math.random() * 20) + 1,
      LoanAmount: Math.floor(Math.random() * 500000) + 10000,
      LoanDuration: [12, 24, 36, 48, 60, 84, 120, 180, 240, 360][Math.floor(Math.random() * 10)],
      MaritalStatus: maritalStatuses[Math.floor(Math.random() * maritalStatuses.length)],
      NumberOfDependents: Math.floor(Math.random() * 5),
      HomeOwnershipStatus: homeOwnership[Math.floor(Math.random() * homeOwnership.length)],
      MonthlyDebtPayments: Math.floor(Math.random() * 3000) + 200,
      CreditCardUtilizationRate: Math.random() * 0.8,
      NumberOfOpenCreditLines: Math.floor(Math.random() * 10) + 1,
      NumberOfCreditInquiries: Math.floor(Math.random() * 5),
      DebtToIncomeRatio: Math.random() * 0.5,
      BankruptcyHistory: Math.random() > 0.9 ? 1 : 0,
      LoanPurpose: loanPurposes[Math.floor(Math.random() * loanPurposes.length)],
      PreviousLoanDefaults: Math.floor(Math.random() * 3),
      PaymentHistory: Math.floor(Math.random() * 120) + 6,
      LengthOfCreditHistory: Math.floor(Math.random() * 240) + 12,
      SavingsAccountBalance: Math.floor(Math.random() * 50000),
      CheckingAccountBalance: Math.floor(Math.random() * 20000),
      TotalAssets: Math.floor(Math.random() * 500000) + 50000,
      TotalLiabilities: Math.floor(Math.random() * 200000),
      MonthlyIncome: Math.floor((Math.random() * 150000 + 30000) / 12),
      UtilityBillsPaymentHistory: Math.random() * 0.3 + 0.7,
      JobTenure: Math.floor(Math.random() * 120) + 6,
      NetWorth: Math.floor(Math.random() * 300000),
      BaseInterestRate: Math.random() * 3 + 3,
      InterestRate: Math.random() * 5 + 4,
      MonthlyLoanPayment: Math.floor(Math.random() * 5000) + 500,
      TotalDebtToIncomeRatio: Math.random() * 0.6,
      LoanApproved: Math.random() > 0.5 ? (Math.random() > 0.5 ? 1 : 0) : null,
      RiskScore: Math.random()
    }));
  };

  const getPredictionWithExplanation = async (customerData) => {
    setLoadingPrediction(true);
    setShapExplanation(null);
    
    try {
      // Map CSV column names to API field names
      const payload = {
        age: customerData.Age || 30,
        annual_income: customerData.AnnualIncome || 50000,
        credit_score: customerData.CreditScore || 650,
        experience: customerData.Experience || 5,
        loan_amount: customerData.LoanAmount || 100000,
        loan_duration: (customerData.LoanDuration || 36) / 12,
        number_of_dependents: customerData.NumberOfDependents || 0,
        monthly_debt_payments: customerData.MonthlyDebtPayments || 500,
        credit_card_utilization_rate: customerData.CreditCardUtilizationRate || 0.3,
        number_of_open_credit_lines: customerData.NumberOfOpenCreditLines || 3,
        number_of_credit_inquiries: customerData.NumberOfCreditInquiries || 1,
        debt_to_income_ratio: customerData.DebtToIncomeRatio || 0.3,
        bankruptcy_history: customerData.BankruptcyHistory || 0,
        previous_loan_defaults: customerData.PreviousLoanDefaults || 0,
        payment_history: (customerData.PaymentHistory || 95) / 100,
        length_of_credit_history: customerData.LengthOfCreditHistory || 12,
        savings_account_balance: customerData.SavingsAccountBalance || 10000,
        checking_account_balance: customerData.CheckingAccountBalance || 5000,
        total_assets: customerData.TotalAssets || 100000,
        total_liabilities: customerData.TotalLiabilities || 50000,
        monthly_income: customerData.MonthlyIncome || 4000,
        job_tenure: customerData.JobTenure || 24,
        net_worth: customerData.NetWorth || 50000,
        employment_status: customerData.EmploymentStatus || "Employed",
        education_level: customerData.EducationLevel || "Bachelor",
        marital_status: customerData.MaritalStatus || "Single",
        home_ownership_status: customerData.HomeOwnershipStatus || "Rent",
        loan_purpose: customerData.LoanPurpose || "Home"
      };
      
      const response = await fetch(`${apiUrl}/predict/explain`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }
      
      const result = await response.json();
      setShapExplanation(result);
      
      // Don't auto-update the loan status, let user decide
      
    } catch (error) {
      console.error('Error getting prediction:', error);
      setShapExplanation({
        error: true,
        message: error.message
      });
    } finally {
      setLoadingPrediction(false);
    }
  };

  const handleApproveWithAI = () => {
    if (shapExplanation && shapExplanation.prediction) {
      const updated = [...customerList];
      updated[selectedCustomer].LoanApproved = 1;
      updated[selectedCustomer].RiskScore = shapExplanation.prediction.risk_score / 100;
      setCustomerList(updated);
    }
  };

  const handleRejectWithAI = () => {
    if (shapExplanation && shapExplanation.prediction) {
      const updated = [...customerList];
      updated[selectedCustomer].LoanApproved = 0;
      updated[selectedCustomer].RiskScore = shapExplanation.prediction.risk_score / 100;
      setCustomerList(updated);
    }
  };

  const handleRefreshPrediction = () => {
    const customer = customerList[selectedCustomer];
    getPredictionWithExplanation(customer);
  };

  const getCreditScoreColor = (score) => {
    if (score >= 740) return "text-green-600";
    if (score >= 670) return "text-yellow-600";
    return "text-red-600";
  };

  const getRiskScoreColor = (score) => {
    if (score <= 0.3) return "text-green-600";
    if (score <= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getStatusBadge = (approved) => {
    if (approved === 1) {
      return <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">Approved</span>;
    }
    if (approved === 0) {
      return <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">Rejected</span>;
    }
    return <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">Pending Review</span>;
  };

  const getLoanPurposeIcon = (purpose) => {
    if (purpose?.toLowerCase().includes('home')) return <Home className="w-4 h-4" />;
    if (purpose?.toLowerCase().includes('auto')) return <CreditCard className="w-4 h-4" />;
    if (purpose?.toLowerCase().includes('business')) return <Building className="w-4 h-4" />;
    return <DollarSign className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading loan applications...</p>
        </div>
      </div>
    );
  }

  if (customerList.length === 0) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-center">
          <p className="text-gray-600">No loan applications found.</p>
        </div>
      </div>
    );
  }

  const customer = customerList[selectedCustomer];
  const pendingCount = customerList.filter(c => c.LoanApproved !== 0 && c.LoanApproved !== 1).length;

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className={`fixed left-0 top-0 h-full w-80 bg-gradient-to-b from-blue-50 to-purple-50 shadow-xl overflow-y-auto transition-transform duration-300 z-20 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="p-6 border-b border-blue-100">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Loan Applications</h1>
              <p className="text-sm text-gray-600 mt-1">{pendingCount} pending reviews</p>
            </div>
          </div>
        </div>
        
        <div className="p-4 space-y-3">
          {customerList.slice(0, 100).map((cust, index) => (
            <div
              key={index}
              onClick={() => setSelectedCustomer(index)}
              className={`p-4 rounded-lg cursor-pointer transition-all ${
                selectedCustomer === index
                  ? 'bg-white shadow-md border-2 border-blue-400'
                  : 'bg-white/60 border-2 border-transparent hover:bg-white hover:shadow-sm'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {cust.Age}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">Application #{index + 1}</h3>
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      {getLoanPurposeIcon(cust.LoanPurpose)}
                      {cust.LoanPurpose}
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-3 space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-semibold text-gray-800">${cust.LoanAmount?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Credit:</span>
                  <span className={`font-semibold ${getCreditScoreColor(cust.CreditScore)}`}>
                    {cust.CreditScore}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Risk:</span>
                  <span className={`font-semibold ${getRiskScoreColor(cust.RiskScore)}`}>
                    {cust.RiskScore?.toFixed(2)}
                  </span>
                </div>
                <div className="mt-2">
                  {getStatusBadge(cust.LoanApproved)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className={`flex-1 overflow-y-auto transition-all duration-300 ${sidebarOpen ? 'ml-80' : 'ml-0'}`}>
        {/* Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="fixed top-6 left-6 z-30 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-lg transition-all"
        >
          {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>

        <div className="p-8">
          <div className="max-w-5xl mx-auto">
            {/* Header */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-semibold">
                    {customer.Age}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800">Application #{selectedCustomer + 1}</h2>
                    <p className="text-gray-500">{customer.LoanPurpose} - {customer.EmploymentStatus}</p>
                  </div>
                </div>
                {getStatusBadge(customer.LoanApproved)}
              </div>
            </div>

            {/* AI Prediction & SHAP Explanation Section */}
            {loadingPrediction && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow-sm p-8 mb-6">
                <div className="flex items-center justify-center space-x-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="text-lg font-semibold text-gray-700">🤖 AI is analyzing the application...</p>
                </div>
              </div>
            )}

            {shapExplanation && !shapExplanation.error && shapExplanation.prediction && (
              <SHAPExplanationCard shapData={shapExplanation} />
            )}

            {shapExplanation && shapExplanation.error && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6 mb-6">
                <div className="flex items-center space-x-3">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                  <div>
                    <p className="font-semibold text-red-800">Error getting AI prediction</p>
                    <p className="text-sm text-red-600">{shapExplanation.message}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Personal Information */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Personal Information
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Age</p>
                  <p className="text-sm font-medium text-gray-800">{customer.Age} years</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Marital Status</p>
                  <p className="text-sm font-medium text-gray-800">{customer.MaritalStatus}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Dependents</p>
                  <p className="text-sm font-medium text-gray-800">{customer.NumberOfDependents}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Education Level</p>
                  <p className="text-sm font-medium text-gray-800">{customer.EducationLevel}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Home Ownership</p>
                  <p className="text-sm font-medium text-gray-800">{customer.HomeOwnershipStatus}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Application Date</p>
                  <p className="text-sm font-medium text-gray-800">{customer.ApplicationDate}</p>
                </div>
              </div>
            </div>

            {/* Employment & Income */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Employment & Income
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-xs text-gray-500">Employment Status</p>
                  <p className="text-sm font-medium text-gray-800">{customer.EmploymentStatus}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Experience</p>
                  <p className="text-sm font-medium text-gray-800">{customer.Experience} years</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Job Tenure</p>
                  <p className="text-sm font-medium text-gray-800">{customer.JobTenure} months</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Annual Income</p>
                  <p className="text-lg font-bold text-gray-800">${customer.AnnualIncome?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Monthly Income</p>
                  <p className="text-lg font-semibold text-gray-800">${customer.MonthlyIncome?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Monthly Debt Payments</p>
                  <p className="text-sm font-medium text-gray-800">${customer.MonthlyDebtPayments?.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Loan Details */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Loan Details
              </h3>
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <p className="text-xs text-gray-500">Loan Amount</p>
                  <p className="text-2xl font-bold text-gray-800">${customer.LoanAmount?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Loan Duration</p>
                  <p className="text-lg font-semibold text-gray-800">{customer.LoanDuration} months</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Loan Purpose</p>
                  <p className="text-sm font-medium text-gray-800">{customer.LoanPurpose}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Base Interest Rate</p>
                  <p className="text-lg font-semibold text-gray-800">{customer.BaseInterestRate?.toFixed(2)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Interest Rate</p>
                  <p className="text-lg font-semibold text-blue-600">{customer.InterestRate?.toFixed(2)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Monthly Payment</p>
                  <p className="text-lg font-bold text-gray-800">${customer.MonthlyLoanPayment?.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Credit Profile */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5" />
                Credit Profile
              </h3>
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <p className="text-xs text-gray-500">Credit Score</p>
                  <p className={`text-3xl font-bold ${getCreditScoreColor(customer.CreditScore)}`}>
                    {customer.CreditScore}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Risk Score</p>
                  <p className={`text-2xl font-bold ${getRiskScoreColor(customer.RiskScore)}`}>
                    {customer.RiskScore?.toFixed(3)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Credit History Length</p>
                  <p className="text-lg font-semibold text-gray-800">{customer.LengthOfCreditHistory} months</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Credit Card Utilization</p>
                  <p className="text-sm font-medium text-gray-800">{(customer.CreditCardUtilizationRate * 100)?.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Open Credit Lines</p>
                  <p className="text-sm font-medium text-gray-800">{customer.NumberOfOpenCreditLines}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Credit Inquiries</p>
                  <p className="text-sm font-medium text-gray-800">{customer.NumberOfCreditInquiries}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Payment History</p>
                  <p className="text-sm font-medium text-gray-800">{customer.PaymentHistory} months</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Previous Defaults</p>
                  <p className="text-sm font-medium text-gray-800">{customer.PreviousLoanDefaults}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Bankruptcy History</p>
                  <p className="text-sm font-medium text-gray-800">{customer.BankruptcyHistory === 1 ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>

            {/* Financial Overview */}
            <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <PiggyBank className="w-5 h-5" />
                Financial Overview
              </h3>
              <div className="grid grid-cols-3 gap-6">
                <div>
                  <p className="text-xs text-gray-500">Debt-to-Income Ratio</p>
                  <p className="text-lg font-semibold text-gray-800">{(customer.DebtToIncomeRatio * 100)?.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Debt-to-Income</p>
                  <p className="text-lg font-semibold text-gray-800">{(customer.TotalDebtToIncomeRatio * 100)?.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Utility Bills Payment History</p>
                  <p className="text-sm font-medium text-gray-800">{(customer.UtilityBillsPaymentHistory * 100)?.toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Savings Account</p>
                  <p className="text-lg font-semibold text-gray-800">${customer.SavingsAccountBalance?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Checking Account</p>
                  <p className="text-lg font-semibold text-gray-800">${customer.CheckingAccountBalance?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Net Worth</p>
                  <p className="text-lg font-bold text-gray-800">${customer.NetWorth?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Assets</p>
                  <p className="text-sm font-medium text-gray-800">${customer.TotalAssets?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Total Liabilities</p>
                  <p className="text-sm font-medium text-gray-800">${customer.TotalLiabilities?.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {customer.LoanApproved !== 0 && customer.LoanApproved !== 1 && (
              <div className="space-y-4">
                {/* Refresh AI Analysis Button */}
                {shapExplanation && (
                  <button
                    onClick={handleRefreshPrediction}
                    disabled={loadingPrediction}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>Refresh AI Analysis</span>
                  </button>
                )}
                
                {/* Decision Buttons */}
                {shapExplanation && shapExplanation.prediction && (
                  <div className="flex space-x-4">
                    <button
                      onClick={handleApproveWithAI}
                      className={`flex-1 font-semibold py-4 px-6 rounded-lg transition-all flex items-center justify-center space-x-2 ${
                        shapExplanation.prediction.approved
                          ? 'bg-green-600 hover:bg-green-700 text-white shadow-lg scale-105'
                          : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                      }`}
                    >
                      <CheckCircle className="w-5 h-5" />
                      <span>
                        {shapExplanation.prediction.approved ? '✨ AI Recommends: Approve' : 'Override: Approve'}
                      </span>
                    </button>
                    <button
                      onClick={handleRejectWithAI}
                      className={`flex-1 font-semibold py-4 px-6 rounded-lg transition-all flex items-center justify-center space-x-2 ${
                        !shapExplanation.prediction.approved
                          ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg scale-105'
                          : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                      }`}
                    >
                      <XCircle className="w-5 h-5" />
                      <span>
                        {!shapExplanation.prediction.approved ? '✨ AI Recommends: Reject' : 'Override: Reject'}
                      </span>
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// SHAP Explanation Card Component
function SHAPExplanationCard({ shapData }) {
  if (!shapData || !shapData.prediction) {
    return null;
  }

  const { prediction, shap_explanation } = shapData;
  
  // Handle case where SHAP is not available
  if (!shap_explanation || shap_explanation.error || !shap_explanation.available) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-8 mb-6 border-2 border-blue-200">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center justify-center gap-3">
            <Sparkles className="w-8 h-8 text-yellow-500" />
            🤖 AI Prediction Result
          </h3>
          
          <div className="bg-white rounded-lg p-6 mb-6 inline-block">
            <div className={`text-6xl font-bold mb-2 ${prediction.approved ? 'text-green-600' : 'text-red-600'}`}>
              {prediction.approved ? '✅ APPROVED' : '❌ REJECTED'}
            </div>
            <div className="text-3xl font-semibold text-blue-600 mb-2">
              {(prediction.probability * 100).toFixed(1)}% Confidence
            </div>
            <div className="text-lg text-gray-600">
              Risk Score: {prediction.risk_score.toFixed(1)}
            </div>
          </div>
          
          <p className="text-sm text-gray-500">
            {shap_explanation?.message || 'SHAP explanations temporarily unavailable'}
          </p>
        </div>
      </div>
    );
  }

  const { top_positive_features, top_negative_features, base_value, waterfall_data } = shap_explanation;

  return (
    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-8 mb-6 border-2 border-blue-200">
      <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
        <Sparkles className="w-8 h-8 text-yellow-500" />
        🤖 AI Decision Explanation (SHAP Analysis)
      </h3>

      {/* Decision Summary */}
      <div className="bg-white rounded-xl p-6 mb-6 shadow-md">
        <div className="grid grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">AI Decision</p>
            <p className={`text-4xl font-bold ${prediction.approved ? 'text-green-600' : 'text-red-600'}`}>
              {prediction.approved ? '✅ APPROVE' : '❌ REJECT'}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Confidence Level</p>
            <p className="text-4xl font-bold text-blue-600">
              {(prediction.probability * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">{prediction.confidence} Confidence</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Risk Score</p>
            <p className={`text-4xl font-bold ${getRiskScoreColor(prediction.risk_score / 100)}`}>
              {prediction.risk_score.toFixed(1)}
            </p>
          </div>
        </div>
      </div>

      {/* Top Positive Features */}
      {top_positive_features && top_positive_features.length > 0 && (
        <div className="bg-white rounded-xl p-6 mb-6 shadow-md">
          <h4 className="text-lg font-bold text-green-700 mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            🟢 Top Reasons Supporting Approval
          </h4>
          <div className="space-y-4">
            {top_positive_features.map((feat, idx) => (
              <div key={idx} className="border-l-4 border-green-500 pl-4 py-2 bg-green-50 rounded-r-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800 text-sm">
                    {idx + 1}. {feat.display_name}
                  </span>
                  <span className="text-lg font-bold text-green-600">
                    +{(feat.shap_value * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full bg-green-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-green-600 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${Math.min(feat.abs_impact * 1000, 100)}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm text-gray-600 font-medium w-32 text-right">
                    {feat.display_value}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top Negative Features */}
      {top_negative_features && top_negative_features.length > 0 && (
        <div className="bg-white rounded-xl p-6 mb-6 shadow-md">
          <h4 className="text-lg font-bold text-red-700 mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5" />
            🔴 Top Concerns Against Approval
          </h4>
          <div className="space-y-4">
            {top_negative_features.map((feat, idx) => (
              <div key={idx} className="border-l-4 border-red-500 pl-4 py-2 bg-red-50 rounded-r-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800 text-sm">
                    {idx + 1}. {feat.display_name}
                  </span>
                  <span className="text-lg font-bold text-red-600">
                    {(feat.shap_value * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1">
                    <div className="w-full bg-red-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-red-600 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${Math.min(feat.abs_impact * 1000, 100)}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm text-gray-600 font-medium w-32 text-right">
                    {feat.display_value}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decision Path Waterfall */}
      {waterfall_data && waterfall_data.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-md">
          <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            📊 Decision Path (How We Got Here)
          </h4>
          <div className="space-y-2">
            {waterfall_data.map((step, idx) => (
              <div key={idx} className={`flex items-center justify-between p-3 rounded-lg ${
                step.impact === 'neutral' ? 'bg-gray-100' :
                step.impact === 'positive' ? 'bg-green-50' :
                step.impact === 'negative' ? 'bg-red-50' :
                'bg-blue-100 font-bold'
              }`}>
                <span className={`text-sm ${
                  step.impact === 'final' ? 'font-bold text-gray-900' : 'text-gray-700'
                }`}>
                  {step.step}
                  {step.display_value && (
                    <span className="text-xs text-gray-500 ml-2">({step.display_value})</span>
                  )}
                </span>
                <div className="flex items-center gap-3">
                  {step.contribution !== 0 && (
                    <span className={`text-xs font-semibold ${
                      step.contribution > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {step.contribution > 0 ? '+' : ''}{(step.contribution * 100).toFixed(1)}%
                    </span>
                  )}
                  <span className={`text-base font-bold ${
                    step.impact === 'final' ? 'text-blue-700 text-xl' : 'text-gray-800'
                  }`}>
                    = {(step.value * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {/* Summary */}
          <div className="mt-6 pt-4 border-t-2 border-gray-200">
            <p className="text-center text-sm text-gray-600">
              Starting from base approval rate of <strong>{(base_value * 100).toFixed(1)}%</strong>, 
              the AI model adjusted the probability based on applicant's features to reach 
              <strong className={prediction.approved ? 'text-green-600' : 'text-red-600'}>
                {' '}{(prediction.probability * 100).toFixed(1)}%
              </strong>
            </p>
          </div>
        </div>
      )}

      {/* Explanation Footer */}
      <div className="mt-6 bg-blue-100 border-l-4 border-blue-600 rounded-lg p-4">
        <p className="text-sm text-blue-900">
          <strong>💡 How to read this:</strong> The AI model starts with a base approval rate and adjusts it based on the applicant's features. 
          Green bars show features that increase approval chances, while red bars show features that decrease them.
          The final probability determines the recommendation.
        </p>
      </div>
    </div>
  );
}

function getRiskScoreColor(score) {
  if (score <= 0.3) return "text-green-600";
  if (score <= 0.6) return "text-yellow-600";
  return "text-red-600";
}
