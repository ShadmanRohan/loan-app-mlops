# Loan Approval AI Assistant - Frontend

This is a modern React application for reviewing loan applications with **AI-powered decision support and SHAP explanations**.

## Features

### 🎯 Core Features
- **Loan Application Management**: Browse and review loan applications from CSV data
- **AI-Powered Recommendations**: Get intelligent approval/rejection recommendations from the ML API
- **SHAP Explanations**: Understand exactly why the AI made its recommendation
- **Real-time Analysis**: Automatic AI analysis for pending applications
- **Beautiful UI**: Modern, responsive design with Tailwind CSS

### 🤖 AI Decision Support
- **Approval Confidence**: See the model's confidence level (0-100%)
- **Risk Score**: View calculated risk assessment
- **Feature Impact**: Understand which features are pushing toward approval or rejection
- **Decision Path**: Follow the waterfall visualization to see how the model arrived at its decision

### 📊 SHAP Visualization Components

#### 1. Decision Summary
Shows the AI's recommendation, confidence level, and risk score at a glance.

#### 2. Top Positive Features
Green bars showing features that **support approval**:
- Feature name and value
- SHAP impact percentage
- Visual bar showing relative importance

#### 3. Top Negative Features
Red bars showing features that **work against approval**:
- Feature name and value
- SHAP impact percentage
- Visual bar showing relative importance

#### 4. Decision Path Waterfall
Step-by-step breakdown showing:
- Base approval rate (starting point)
- How each feature adjusted the probability
- Final approval probability

## Installation

### Prerequisites
- Node.js 16+ and npm/yarn
- The ML API running at `http://localhost:8000`

### Setup

```bash
cd frontend
npm install
```

### Required Dependencies

```bash
npm install react react-dom
npm install lucide-react      # Icons
npm install papaparse         # CSV parsing
npm install tailwindcss postcss autoprefixer  # Styling
```

### Tailwind CSS Configuration

Initialize Tailwind:
```bash
npx tailwindcss init -p
```

Update `tailwind.config.js`:
```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Add to your CSS file:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Usage

### 1. Start the ML Pipeline
First, ensure the ML API is running:
```bash
cd ..
./start_loan_pipeline.sh start
```

### 2. Start the React App
```bash
npm start
```

### 3. Using the Application

#### Browse Applications
- Applications are listed in the left sidebar
- Click any application to view details
- Pending applications are marked in yellow

#### AI Analysis
- When you select a pending application, AI analysis runs automatically
- The analysis appears at the top with:
  - AI recommendation (Approve/Reject)
  - Confidence level
  - Risk score
  - SHAP explanations

#### Understanding SHAP Visualizations

**Green Bars (Positive Features)**: 
- These features increase the approval probability
- Example: "High Credit Score: 780" → +12.5%

**Red Bars (Negative Features)**:
- These features decrease the approval probability
- Example: "High Debt-to-Income Ratio: 45%" → -8.3%

**Decision Path Waterfall**:
- Shows the step-by-step journey from base rate to final decision
- Each row shows a feature's contribution
- Final row shows the resulting probability

#### Making Decisions
- Review the AI recommendation and SHAP explanations
- Click "✨ AI Recommends: Approve" to approve (highlighted if AI suggests approval)
- Click "✨ AI Recommends: Reject" to reject (highlighted if AI suggests rejection)
- You can override the AI by clicking the opposite button

## API Integration

The component calls two endpoints:

### 1. Health Check (Optional)
```
GET http://localhost:8000/health
```

### 2. Prediction with Explanation
```
POST http://localhost:8000/predict/explain
Content-Type: application/json

{
  "age": 30,
  "annual_income": 75000,
  "credit_score": 720,
  ...
}
```

**Response**:
```json
{
  "prediction": {
    "approved": true,
    "probability": 0.847,
    "risk_score": 23.5,
    "confidence": "High"
  },
  "shap_explanation": {
    "available": true,
    "base_value": 0.65,
    "top_positive_features": [
      {
        "feature": "credit_score",
        "display_name": "Credit Score",
        "value": 720,
        "display_value": "720",
        "shap_value": 0.125,
        "abs_impact": 0.125
      }
    ],
    "top_negative_features": [...],
    "waterfall_data": [...]
  }
}
```

## Data Format

The app expects CSV data with these columns:
- `Age`, `AnnualIncome`, `CreditScore`
- `EmploymentStatus`, `EducationLevel`, `MaritalStatus`
- `LoanAmount`, `LoanDuration`, `LoanPurpose`
- `DebtToIncomeRatio`, `CreditCardUtilizationRate`
- `NumberOfDependents`, `NumberOfOpenCreditLines`
- `PreviousLoanDefaults`, `BankruptcyHistory`
- And more...

Place your `Loan.csv` file in the accessible directory or let the app generate sample data.

## Customization

### Change API URL
Update the `apiUrl` state in the component:
```jsx
const [apiUrl] = useState('http://your-api-url:8000');
```

### Adjust SHAP Feature Count
The API returns top 5 positive and negative features by default. To change this, modify the backend endpoint.

### Styling
All styling is done with Tailwind CSS classes. Modify the JSX classes to customize appearance.

## Troubleshooting

### SHAP Explanations Not Showing
- Ensure the ML API endpoint `/predict/explain` is working
- Check browser console for API errors
- Verify the model supports SHAP (currently uses RandomForest/LogisticRegression)

### CSV Loading Issues
- Check file path and permissions
- Ensure CSV headers match expected format
- Look for console errors related to Papa Parse

### API Connection Errors
- Verify ML API is running: `curl http://localhost:8000/health`
- Check for CORS issues (may need to enable CORS in FastAPI)
- Confirm network connectivity

## Architecture

```
LoanApprovalUI (Main Component)
├── State Management
│   ├── customerList (all applications)
│   ├── selectedCustomer (current selection)
│   ├── shapExplanation (AI analysis)
│   └── loading states
├── Data Loading
│   ├── CSV parsing (Papa Parse)
│   └── Sample data generation
├── API Integration
│   └── getPredictionWithExplanation()
├── UI Sections
│   ├── Sidebar (Application List)
│   ├── Header (Current Application)
│   ├── SHAP Card (AI Analysis)
│   ├── Personal Info
│   ├── Employment & Income
│   ├── Loan Details
│   ├── Credit Profile
│   ├── Financial Overview
│   └── Action Buttons
└── SHAPExplanationCard (Sub-component)
    ├── Decision Summary
    ├── Positive Features
    ├── Negative Features
    └── Waterfall Visualization
```

## Future Enhancements

- [ ] Export decisions to CSV
- [ ] Batch processing mode
- [ ] Historical decision tracking
- [ ] User authentication
- [ ] Audit log
- [ ] Advanced filtering and search
- [ ] Custom SHAP feature selection
- [ ] Comparison between applications
- [ ] Mobile-responsive improvements

## License

This project is part of the ML Orchestration Platform.
