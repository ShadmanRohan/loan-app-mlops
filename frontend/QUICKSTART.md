# Quick Start Guide - Loan Approval with SHAP

Get the AI-powered loan approval interface running in 5 minutes!

## Prerequisites
- ✅ ML API running at http://localhost:8000
- ✅ Node.js 16+ installed
- ✅ Loan.csv data file (or use auto-generated sample data)

## Step 1: Verify ML API is Running

```bash
# From project root
./start_loan_pipeline.sh start

# Verify API health
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "shap_available": true
}
```

## Step 2: Test SHAP Endpoint

```bash
curl -X POST http://localhost:8000/predict/explain \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "annual_income": 75000,
    "credit_score": 720,
    "experience": 10,
    "loan_amount": 200000,
    "loan_duration": 360,
    "number_of_dependents": 2,
    "monthly_debt_payments": 1500,
    "credit_card_utilization_rate": 0.3,
    "number_of_open_credit_lines": 5,
    "number_of_credit_inquiries": 1,
    "debt_to_income_ratio": 0.35,
    "bankruptcy_history": 0,
    "previous_loan_defaults": 0,
    "payment_history": 0.98,
    "length_of_credit_history": 120,
    "savings_account_balance": 30000,
    "checking_account_balance": 10000,
    "total_assets": 350000,
    "total_liabilities": 150000,
    "monthly_income": 6250,
    "job_tenure": 48,
    "net_worth": 200000,
    "employment_status": "Employed",
    "education_level": "Bachelor",
    "marital_status": "Married",
    "home_ownership_status": "Own",
    "loan_purpose": "Home"
  }'
```

If successful, you'll see SHAP explanations! 🎉

## Step 3: Setup React App

### Option A: Using Create React App (Recommended)

```bash
# Create new React app
npx create-react-app loan-approval-app
cd loan-approval-app

# Install dependencies
npm install lucide-react papaparse
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind
npx tailwindcss init -p

# Copy the component
cp ../ml-orchestration/frontend/LoanApprovalWithSHAP.jsx src/App.jsx

# Update src/index.css
cat > src/index.css << 'TAILWIND'
@tailwind base;
@tailwind components;
@tailwind utilities;
TAILWIND

# Update tailwind.config.js
cat > tailwind.config.js << 'TAILWINDCONFIG'
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
TAILWINDCONFIG

# Start the app
npm start
```

### Option B: Using Vite (Faster)

```bash
# Create Vite app
npm create vite@latest loan-approval-app -- --template react
cd loan-approval-app

# Install dependencies
npm install
npm install lucide-react papaparse
npm install -D tailwindcss postcss autoprefixer

# Initialize Tailwind
npx tailwindcss init -p

# Copy component
cp ../ml-orchestration/frontend/LoanApprovalWithSHAP.jsx src/App.jsx

# Update src/index.css (same as above)
# Update tailwind.config.js (same as above)

# Start
npm run dev
```

## Step 4: Place Your CSV Data

Option 1: Use your own CSV
```bash
# Copy your Loan.csv to public folder
cp /path/to/Loan.csv loan-approval-app/public/
```

Option 2: Let the app generate sample data (automatic fallback)

## Step 5: Open the App

Navigate to http://localhost:3000 (Create React App) or http://localhost:5173 (Vite)

You should see:
- 📋 List of loan applications in the sidebar
- 🤖 AI analysis for pending applications
- 📊 SHAP visualizations with feature impacts
- ✅❌ Approve/Reject buttons with AI recommendations

## What You'll See

### 1. Application List (Left Sidebar)
- All loan applications from CSV
- Status badges (Pending/Approved/Rejected)
- Quick info: Amount, Credit Score, Risk

### 2. AI Analysis Panel (Top of main area)
Shows automatically for pending applications:
- 🎯 **Decision**: AI's recommendation
- 📊 **Confidence**: How confident the model is
- ⚠️ **Risk Score**: Calculated risk level
- 🟢 **Positive Features**: What helps approval
- 🔴 **Negative Features**: What hurts approval
- 📈 **Decision Path**: Step-by-step waterfall

### 3. Action Buttons
- Highlighted button shows AI recommendation
- Can override AI decision if needed
- Refresh button to re-run analysis

## Testing the SHAP Visualization

1. **Select a pending application** from the sidebar
2. **Wait 1-2 seconds** for AI analysis to load
3. **Scroll to top** to see SHAP explanations
4. **Look for green bars**: Features supporting approval
5. **Look for red bars**: Features against approval
6. **Review the waterfall**: See how probability changed
7. **Click recommended button** to approve/reject

## Troubleshooting

### ❌ "Failed to fetch" error
**Problem**: Can't connect to API

**Solution**:
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart the pipeline
./start_loan_pipeline.sh restart
```

### ❌ SHAP not showing
**Problem**: `/predict/explain` endpoint issues

**Solution**:
```bash
# Check API logs
docker compose -f infrastructure/docker-compose.yml logs prediction-api

# Test endpoint directly (see Step 2)
```

### ❌ CORS errors
**Problem**: Browser blocking requests

**Solution**: Add to `services/prediction-api/src/api/app.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then rebuild:
```bash
./start_loan_pipeline.sh restart
```

### ❌ CSV not loading
**Problem**: File path issues

**Solution**: The app auto-generates sample data if CSV not found. To use your CSV:
```bash
# For Create React App
cp Loan.csv loan-approval-app/public/

# For Vite
cp Loan.csv loan-approval-app/public/

# Update component if needed:
// Change in useEffect:
const fileContent = await fetch('/Loan.csv').then(r => r.text());
```

## Next Steps

✅ Everything working? Great! Now you can:

1. **Review loan applications** with AI assistance
2. **Understand AI decisions** through SHAP explanations
3. **Make informed decisions** based on feature impacts
4. **Track your decisions** (approved/rejected status updates)

## Advanced Usage

### Custom API URL
Edit `LoanApprovalWithSHAP.jsx`:
```jsx
const [apiUrl] = useState('http://your-server:8000');
```

### Export Decisions
Add export functionality (see README.md for future enhancements)

### Batch Processing
Process multiple applications at once (future feature)

## Support

- 📖 Full docs: See `frontend/README.md`
- 🐛 Issues: Check API logs and browser console
- 💡 Features: The component is fully customizable

Enjoy your AI-powered loan approval system! 🚀
