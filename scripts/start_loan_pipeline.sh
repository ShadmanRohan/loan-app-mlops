#!/bin/bash

COMPOSE_FILE="infrastructure/docker-compose/docker-compose.services.yml"
API_URL="http://localhost:8000"
MLFLOW_URL="http://localhost:5000"
MONITORING_URL="http://localhost:8501"
GRAFANA_URL="http://localhost:3001"
PROMETHEUS_URL="http://localhost:9090"

log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_warning() {
    echo "[WARNING] $1"
}

log_error() {
    echo "[ERROR] $1"
}

start_services() {
    local enable_dummy_requests=$1
    
    log_info "Stopping any existing services..."
    docker-compose -f "$COMPOSE_FILE" down > /dev/null 2>&1 || true
    
    log_info "Starting MLflow, API, Monitoring, and Grafana services..."
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    if [ $? -eq 0 ]; then
        log_success "Services started successfully"
    else
        log_error "Failed to start services"
        exit 1
    fi
    
    # Start dummy request generator if requested
    if [ "$enable_dummy_requests" = "true" ]; then
        log_info "Starting dummy request generator..."
        start_dummy_requests
    fi
}

start_dummy_requests() {
    # Create a simple dummy request generator container
    docker run -d \
        --name loan-dummy-requests \
        --network docker-compose_default \
        python:3.11-slim \
        bash -c "
            pip install requests > /dev/null 2>&1 && 
            python -c \"
import requests
import json
import random
import time
from datetime import datetime

scenarios = [
    {
        'name': 'Young Professional',
        'data': {
            'age': 28, 'annual_income': 65000, 'credit_score': 720,
            'employment_status': 'Employed', 'education_level': 'Bachelor',
            'experience': 3, 'loan_amount': 180000, 'loan_duration': 30,
            'marital_status': 'Single', 'number_of_dependents': 0,
            'home_ownership_status': 'Rent', 'monthly_debt_payments': 600,
            'credit_card_utilization_rate': 0.25, 'number_of_open_credit_lines': 2,
            'number_of_credit_inquiries': 1, 'debt_to_income_ratio': 0.22,
            'bankruptcy_history': 0, 'loan_purpose': 'Home',
            'previous_loan_defaults': 0, 'payment_history': 0.95,
            'length_of_credit_history': 6, 'savings_account_balance': 15000,
            'checking_account_balance': 3000, 'total_assets': 50000,
            'total_liabilities': 25000, 'monthly_income': 5417,
            'job_tenure': 2, 'net_worth': 25000
        }
    },
    {
        'name': 'Established Family',
        'data': {
            'age': 42, 'annual_income': 95000, 'credit_score': 780,
            'employment_status': 'Employed', 'education_level': 'Master',
            'experience': 15, 'loan_amount': 350000, 'loan_duration': 25,
            'marital_status': 'Married', 'number_of_dependents': 2,
            'home_ownership_status': 'Own', 'monthly_debt_payments': 1200,
            'credit_card_utilization_rate': 0.15, 'number_of_open_credit_lines': 4,
            'number_of_credit_inquiries': 0, 'debt_to_income_ratio': 0.18,
            'bankruptcy_history': 0, 'loan_purpose': 'Home',
            'previous_loan_defaults': 0, 'payment_history': 0.98,
            'length_of_credit_history': 20, 'savings_account_balance': 75000,
            'checking_account_balance': 15000, 'total_assets': 300000,
            'total_liabilities': 100000, 'monthly_income': 7917,
            'job_tenure': 8, 'net_worth': 200000
        }
    },
    {
        'name': 'Risky Applicant',
        'data': {
            'age': 35, 'annual_income': 45000, 'credit_score': 580,
            'employment_status': 'Employed', 'education_level': 'High School',
            'experience': 8, 'loan_amount': 200000, 'loan_duration': 30,
            'marital_status': 'Divorced', 'number_of_dependents': 1,
            'home_ownership_status': 'Rent', 'monthly_debt_payments': 1500,
            'credit_card_utilization_rate': 0.75, 'number_of_open_credit_lines': 6,
            'number_of_credit_inquiries': 3, 'debt_to_income_ratio': 0.45,
            'bankruptcy_history': 1, 'loan_purpose': 'Home',
            'previous_loan_defaults': 1, 'payment_history': 0.70,
            'length_of_credit_history': 10, 'savings_account_balance': 2000,
            'checking_account_balance': 500, 'total_assets': 15000,
            'total_liabilities': 80000, 'monthly_income': 3750,
            'job_tenure': 1, 'net_worth': -65000
        }
    }
]

request_count = 0
while True:
    try:
        scenario = random.choice(scenarios)
        data = scenario['data'].copy()
        
        # Add random variations
        data['age'] = max(18, min(70, data['age'] + random.randint(-5, 5)))
        data['annual_income'] = max(20000, data['annual_income'] + random.randint(-10000, 10000))
        data['credit_score'] = max(300, min(850, data['credit_score'] + random.randint(-50, 50)))
        data['loan_amount'] = max(50000, data['loan_amount'] + random.randint(-50000, 50000))
        
        response = requests.post('http://prediction-api:8000/predict', json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            request_count += 1
            print(f'Request #{request_count} - {scenario[\"name\"]}: Approved={result.get(\"approved\", False)}, Risk={result.get(\"risk_score\", 0):.1f}')
        else:
            print(f'Request failed: {response.status_code}')
    except Exception as e:
        print(f'Error: {e}')
    
    time.sleep(random.uniform(2, 4))  # Random interval between 2-4 seconds
\""
        
        log_success "Dummy request generator started (every 2-4 seconds)"
        log_info "View logs: docker logs loan-dummy-requests"
}

stop_services() {
    log_info "Stopping Loan Approval Pipeline..."
    
    # Stop dummy request generator if running
    if docker ps -q -f name=loan-dummy-requests > /dev/null 2>&1; then
        log_info "Stopping dummy request generator..."
        docker stop loan-dummy-requests > /dev/null 2>&1
        docker rm loan-dummy-requests > /dev/null 2>&1
    fi
    
    docker-compose -f "$COMPOSE_FILE" down
    if [ $? -eq 0 ]; then
        log_success "Services stopped"
    else
        log_error "Failed to stop services"
        exit 1
    fi
}

check_health() {
    local service_name=$1
    local url=$2
    local max_attempts=30
    local attempt=0
    local status=1

    log_info "Waiting for $service_name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null; then
            log_success "$service_name is ready"
            status=0
            break
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt+1))
    done

    if [ $status -ne 0 ]; then
        log_warning "$service_name is not responding on port $(echo "$url" | cut -d':' -f3)"
        return 1
    fi
    return 0
}

test_api() {
    log_info "Testing API..."
    if curl -s "$API_URL/health" | grep -q "healthy"; then
        echo "✅ API is running"
    else
        echo "❌ API is not running"
        return 1
    fi

    log_info "Testing loan prediction..."
    PREDICTION_DATA='{
        "age": 35,
        "annual_income": 75000,
        "credit_score": 720,
        "employment_status": "Employed",
        "education_level": "Bachelor",
        "experience": 8,
        "loan_amount": 250000,
        "loan_duration": 15,
        "marital_status": "Married",
        "number_of_dependents": 2,
        "home_ownership_status": "Rent",
        "monthly_debt_payments": 1200,
        "credit_card_utilization_rate": 0.3,
        "number_of_open_credit_lines": 3,
        "number_of_credit_inquiries": 1,
        "debt_to_income_ratio": 0.25,
        "bankruptcy_history": 0,
        "loan_purpose": "Home",
        "previous_loan_defaults": 0,
        "payment_history": 0.95,
        "length_of_credit_history": 12,
        "savings_account_balance": 50000,
        "checking_account_balance": 10000,
        "total_assets": 200000,
        "total_liabilities": 150000,
        "monthly_income": 6250,
        "job_tenure": 5,
        "net_worth": 50000
    }'
    PREDICTION_RESULT=$(curl -s -X POST -H "Content-Type: application/json" -d "$PREDICTION_DATA" "$API_URL/predict")
    if echo "$PREDICTION_RESULT" | grep -q "approved"; then
        echo "✅ Loan prediction working"
        echo "Sample result: $PREDICTION_RESULT"
    else
        echo "❌ Loan prediction failed"
        echo "Error: $PREDICTION_RESULT"
        return 1
    fi

    log_info "Current metrics:"
    curl -s "$API_URL/metrics"
    echo ""
    return 0
}

show_status() {
    echo "Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    echo "API Health:"
    curl -s "$API_URL/health" || echo "API not responding"
    echo ""
    echo "Metrics:"
    curl -s "$API_URL/metrics" || echo "Metrics not available"
    echo ""
    
    if docker ps -q -f name=loan-dummy-requests > /dev/null 2>&1; then
        echo "Dummy Request Generator:"
        echo "✅ Running (view logs: docker logs loan-dummy-requests)"
    else
        echo "Dummy Request Generator: ❌ Not running"
    fi
    echo ""
}

show_help() {
    echo "🚀 Loan Approval Pipeline"
    echo "========================"
    echo ""
    echo "Usage:"
    echo "  ./start_loan_pipeline.sh [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [--dummy]    Start services (optionally with dummy requests)"
    echo "  stop               Stop all services"
    echo "  status             Show service status"
    echo "  help               Show this help"
    echo ""
    echo "Options:"
    echo "  --dummy            Start with dummy request generator (every 2-4 seconds)"
    echo ""
    echo "Examples:"
    echo "  ./start_loan_pipeline.sh start              # Start without dummy requests"
    echo "  ./start_loan_pipeline.sh start --dummy     # Start with dummy requests"
    echo "  ./start_loan_pipeline.sh stop              # Stop all services"
    echo "  ./start_loan_pipeline.sh status             # Check status"
    echo ""
    echo "Service Endpoints:"
    echo "  • API: $API_URL"
    echo "  • Health: $API_URL/health"
    echo "  • Metrics: $API_URL/metrics"
    echo "  • Docs: $API_URL/docs"
    echo "  • MLflow: $MLFLOW_URL"
    echo "  • Streamlit Dashboard: $MONITORING_URL"
    echo "  • Grafana Dashboard: $GRAFANA_URL (admin/admin)
• Prometheus: $PROMETHEUS_URL"
    echo ""
    echo "Dashboard Comparison:"
    echo "  📊 Streamlit: Simple, real-time, auto-refresh"
    echo "  🚀 Grafana: Professional, advanced features, alerting"
}

main() {
    echo "🚀 Starting Loan Approval Pipeline"
    echo "=================================="

    case "$1" in
        "start")
            if [ "$2" = "--dummy" ]; then
                log_info "Starting with dummy request generator..."
                start_services "true"
            else
                start_services "false"
            fi
            
            log_info "Waiting for services to initialize..."
            sleep 5
            check_health "MLflow" "$MLFLOW_URL" || true
            check_health "Prediction API" "$API_URL/health"
            check_health "Streamlit Dashboard" "$MONITORING_URL" || true
            check_health "Grafana Dashboard" "$GRAFANA_URL" || true
            test_api
            
            echo "🎉 Loan Approval Pipeline is ready!"
            echo ""
            echo "Service Endpoints:"
            echo "• API: $API_URL"
            echo "• Health: $API_URL/health"
            echo "• Metrics: $API_URL/metrics"
            echo "• Docs: $API_URL/docs"
            echo "• MLflow: $MLFLOW_URL"
            echo "• Streamlit Dashboard: $MONITORING_URL"
            echo "• Grafana Dashboard: $GRAFANA_URL (admin/admin)
• Prometheus: $PROMETHEUS_URL"
            echo ""
            
            if [ "$2" = "--dummy" ]; then
                echo "🤖 Dummy Request Generator:"
                echo "• Generating requests every 2-4 seconds"
                echo "• View logs: docker logs loan-dummy-requests"
                echo "• Stop generator: docker stop loan-dummy-requests"
            fi
            
            echo ""
            echo "Dashboard Options:"
            echo "📊 Streamlit: Simple, real-time, auto-refresh"
            echo "🚀 Grafana: Professional, advanced features, alerting"
            echo ""
            echo "Usage:"
            echo "• Test API: curl $API_URL/health"
            echo "• Get Metrics: curl $API_URL/metrics"
            echo "• Stop Services: ./start_loan_pipeline.sh stop"
            ;;
        "stop")
            stop_services
            ;;
        "status")
            show_status
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            if [ "$1" = "--dummy" ]; then
                log_info "Starting with dummy request generator..."
                start_services "true"
            else
                start_services "false"
            fi
            
            log_info "Waiting for services to initialize..."
            sleep 5
            check_health "MLflow" "$MLFLOW_URL" || true
            check_health "Prediction API" "$API_URL/health"
            check_health "Streamlit Dashboard" "$MONITORING_URL" || true
            check_health "Grafana Dashboard" "$GRAFANA_URL" || true
            test_api
            
            echo "🎉 Loan Approval Pipeline is ready!"
            echo ""
            echo "Service Endpoints:"
            echo "• API: $API_URL"
            echo "• Health: $API_URL/health"
            echo "• Metrics: $API_URL/metrics"
            echo "• Docs: $API_URL/docs"
            echo "• MLflow: $MLFLOW_URL"
            echo "• Streamlit Dashboard: $MONITORING_URL"
            echo "• Grafana Dashboard: $GRAFANA_URL (admin/admin)
• Prometheus: $PROMETHEUS_URL"
            echo ""
            echo "Dashboard Options:"
            echo "📊 Streamlit: Simple, real-time, auto-refresh"
            echo "🚀 Grafana: Professional, advanced features, alerting"
            echo ""
            echo "Usage:"
            echo "• Test API: curl $API_URL/health"
            echo "• Get Metrics: curl $API_URL/metrics"
            echo "• Stop Services: ./start_loan_pipeline.sh stop"
            ;;
    esac
}

main "$@"
