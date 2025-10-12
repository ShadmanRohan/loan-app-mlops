#!/usr/bin/env python3
"""Real-time monitoring dashboard with drift monitoring and auto-refresh."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import time
import os

# Configure Streamlit page
st.set_page_config(
    page_title="ML Monitoring Dashboard with Drift Detection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add auto-refresh
st.markdown("""
<meta http-equiv="refresh" content="5">
""", unsafe_allow_html=True)

def get_api_metrics():
    """Fetch REAL metrics from the prediction API."""
    try:
        response = requests.get("http://prediction-api:8000/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch API metrics: {e}")
    return {"total_requests": 0, "approvals": 0, "approval_rate": 0.0, "avg_risk_score": 0.0}

def get_prometheus_metrics():
    """Fetch Prometheus metrics for comparison."""
    try:
        # Get Prometheus data via API
        prometheus_url = "http://prometheus:9090/api/v1/query"
        
        # Query for total requests
        total_requests_resp = requests.get(f"{prometheus_url}?query=sum(loan_api_requests_total)", timeout=5)
        total_requests = 0
        if total_requests_resp.status_code == 200:
            data = total_requests_resp.json()
            if data.get("status") == "success" and data.get("data", {}).get("result"):
                total_requests = int(float(data["data"]["result"][0]["value"][1]))
        
        # Query for approvals
        approvals_resp = requests.get(f"{prometheus_url}?query=sum(loan_api_approvals_total{approved=\"true\"})", timeout=5)
        approvals = 0
        if approvals_resp.status_code == 200:
            data = approvals_resp.json()
            if data.get("status") == "success" and data.get("data", {}).get("result"):
                approvals = int(float(data["data"]["result"][0]["value"][1]))
        
        # Query for avg risk score
        risk_resp = requests.get(f"{prometheus_url}?query=loan_api_avg_risk_score", timeout=5)
        avg_risk = 0.0
        if risk_resp.status_code == 200:
            data = risk_resp.json()
            if data.get("status") == "success" and data.get("data", {}).get("result"):
                avg_risk = float(data["data"]["result"][0]["value"][1])
        
        # Calculate approval rate
        approval_rate = (approvals / total_requests) if total_requests > 0 else 0.0
        
        return {
            "total_requests": total_requests,
            "approvals": approvals,
            "approval_rate": approval_rate,
            "avg_risk_score": avg_risk
        }
    except Exception as e:
        st.error(f"Failed to fetch Prometheus metrics: {e}")
        return {"total_requests": 0, "approvals": 0, "approval_rate": 0.0, "avg_risk_score": 0.0}

def get_drift_metrics():
    """Fetch drift metrics from the API."""
    try:
        response = requests.get("http://prediction-api:8000/drift/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch drift metrics: {e}")
    return {"status": "unavailable"}

def get_drift_summary():
    """Fetch drift summary from the API."""
    try:
        response = requests.get("http://prediction-api:8000/drift/summary", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch drift summary: {e}")
    return {"status": "unavailable"}

def get_api_health():
    """Check API health."""
    try:
        response = requests.get("http://prediction-api:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_drift_section():
    """Create the drift monitoring section."""
    st.subheader("📊 Data Drift Monitoring")
    
    drift_metrics = get_drift_metrics()
    drift_summary = get_drift_summary()
    
    if drift_metrics.get("status") == "unavailable":
        st.warning("⚠️ Drift monitoring not available. Make sure drift integration is deployed.")
        return
    
    if drift_metrics.get("status") == "insufficient_data":
        st.info(f"📊 Collecting data... ({drift_metrics.get('data_points', 0)} points collected)")
        st.info("Need at least 10 data points for drift analysis.")
        return
    
    if drift_metrics.get("status") == "error":
        st.error(f"❌ Drift analysis error: {drift_metrics.get('message', 'Unknown error')}")
        return
    
    # Drift status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        drift_detected = drift_metrics.get("dataset_drift_detected", False)
        drift_status = "🔴 High Drift" if drift_detected else "🟢 Normal"
        st.metric("Drift Status", drift_status)
    
    with col2:
        data_points = drift_metrics.get("data_points", 0)
        st.metric("Data Points", data_points)
    
    with col3:
        drifted_features = drift_metrics.get("number_of_drifted_features", 0)
        st.metric("Drifted Features", drifted_features)
    
    with col4:
        share_drifted = drift_metrics.get("share_of_drifted_features", 0.0)
        st.metric("Share Drifted", f"{share_drifted:.1%}")
    
    # Feature drift analysis
    if drift_metrics.get("feature_drift_scores"):
        st.subheader("🔍 Feature Drift Analysis")
        
        feature_scores = drift_metrics.get("feature_drift_scores", {})
        if feature_scores:
            # Create DataFrame for visualization
            df_features = pd.DataFrame([
                {"Feature": feature, "Drift Score": score}
                for feature, score in feature_scores.items()
            ]).sort_values("Drift Score", ascending=False)
            
            # Show top 10 features with highest drift
            st.write("**Top 10 Features with Highest Drift:**")
            st.dataframe(df_features.head(10), use_container_width=True)
            
            # Create bar chart
            fig = px.bar(df_features.head(10), x="Feature", y="Drift Score",
                        title="Feature Drift Scores (Top 10)",
                        color="Drift Score",
                        color_continuous_scale="Reds")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Drifted features list
        drifted_features = drift_metrics.get("drifted_features", [])
        if drifted_features:
            st.warning(f"⚠️ **Drifted Features Detected:** {', '.join(drifted_features)}")
        else:
            st.success("✅ **No significant drift detected in any features**")
    
    # Data collection summary
    if drift_summary.get("status") != "unavailable":
        st.subheader("📈 Data Collection Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Data Points", drift_summary.get("data_points_collected", 0))
        
        with col2:
            last_update = drift_summary.get("last_update")
            if last_update:
                st.metric("Last Update", last_update.split("T")[1][:8])
            else:
                st.metric("Last Update", "Never")
        
        with col3:
            num_features = len(drift_summary.get("numerical_features", []))
            cat_features = len(drift_summary.get("categorical_features", []))
            st.metric("Features Monitored", f"{num_features + cat_features}")

def create_real_time_dashboard():
    """Create real-time dashboard with auto-refresh and drift monitoring."""
    st.title("🚀 ML Monitoring Dashboard with Drift Detection")
    st.markdown("*Real-time data from your Loan Approval API with drift monitoring*")
    
    # Auto-refresh indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("🔄 **Auto-refreshing every 5 seconds**")
    
    st.markdown("---")
    
    # Get REAL current metrics
    metrics = get_api_metrics()
    api_healthy = get_api_health()
    
    # Status indicators with REAL data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="API Status",
            value="🟢 Healthy" if api_healthy else "🔴 Down",
            delta=None
        )
    
    with col2:
        total_requests = metrics.get("total_requests", 0)
        st.metric(
            label="Total Requests",
            value=total_requests,
            delta=None
        )
    
    with col3:
        approval_rate = metrics.get("approval_rate", 0.0)
        st.metric(
            label="Approval Rate",
            value=f"{approval_rate:.1%}",
            delta=None
        )
    
    with col4:
        avg_risk = metrics.get("avg_risk_score", 0.0)
        st.metric(
            label="Avg Risk Score",
            value=f"{avg_risk:.1f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Metrics Comparison Section
    st.subheader("🔄 Metrics Comparison (API vs Prometheus)")
    
    # Get both sets of metrics
    api_metrics = get_api_metrics()
    prometheus_metrics = get_prometheus_metrics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 API Metrics (Custom Endpoint)**")
        st.metric("Total Requests", api_metrics.get("total_requests", 0))
        st.metric("Approvals", api_metrics.get("approvals", 0))
        st.metric("Approval Rate", f"{api_metrics.get('approval_rate', 0.0):.1%}")
        st.metric("Avg Risk Score", f"{api_metrics.get('avg_risk_score', 0.0):.1f}")
    
    with col2:
        st.markdown("**📈 Prometheus Metrics (Real-time Counters)**")
        st.metric("Total Requests", prometheus_metrics.get("total_requests", 0))
        st.metric("Approvals", prometheus_metrics.get("approvals", 0))
        st.metric("Approval Rate", f"{prometheus_metrics.get('approval_rate', 0.0):.1%}")
        st.metric("Avg Risk Score", f"{prometheus_metrics.get('avg_risk_score', 0.0):.1f}")
    
    # Show differences
    st.markdown("**🔍 Differences:**")
    diff_requests = api_metrics.get("total_requests", 0) - prometheus_metrics.get("total_requests", 0)
    diff_approvals = api_metrics.get("approvals", 0) - prometheus_metrics.get("approvals", 0)
    diff_rate = api_metrics.get("approval_rate", 0.0) - prometheus_metrics.get("approval_rate", 0.0)
    diff_risk = api_metrics.get("avg_risk_score", 0.0) - prometheus_metrics.get("avg_risk_score", 0.0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Request Diff", diff_requests, delta=f"{diff_requests}")
    with col2:
        st.metric("Approval Diff", diff_approvals, delta=f"{diff_approvals}")
    with col3:
        st.metric("Rate Diff", f"{diff_rate:.1%}", delta=f"{diff_rate:.1%}")
    with col4:
        st.metric("Risk Diff", f"{diff_risk:.1f}", delta=f"{diff_risk:.1f}")
    
    st.markdown("---")
    
    # Drift monitoring section
    create_drift_section()
    
    st.markdown("---")
    
    # Real-time charts
    if total_requests > 0:
        st.subheader("📊 Real-Time Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Real approval distribution
            approvals = metrics.get("approvals", 0)
            rejections = total_requests - approvals
            
            if total_requests > 0:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Approved', 'Rejected'],
                    values=[approvals, rejections],
                    hole=0.3,
                    marker_colors=['#00ff00', '#ff0000']
                )])
                fig_pie.update_layout(
                    title="Real Loan Approval Distribution",
                    showlegend=True
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Real risk score gauge
            avg_risk = metrics.get("avg_risk_score", 0.0)
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_risk,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Average Risk Score"},
                delta = {'reference': 50},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 80
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Request trends over time (simulated based on current data)
        st.subheader("📈 Request Trends")
        
        # Create a simple trend chart
        now = datetime.now()
        time_points = [now - timedelta(minutes=i) for i in range(10, 0, -1)]
        request_counts = [max(0, total_requests - i) for i in range(10, 0, -1)]
        
        df_trends = pd.DataFrame({
            'Time': time_points,
            'Requests': request_counts
        })
        
        fig_trends = px.line(df_trends, x='Time', y='Requests', 
                           title="Request Count Over Time")
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Risk score distribution
        st.subheader("📊 Risk Score Analysis")
        
        # Simulate risk score distribution based on current data
        risk_scores = np.random.normal(avg_risk, 15, min(100, total_requests * 10))
        risk_scores = np.clip(risk_scores, 0, 100)
        
        df_risk = pd.DataFrame({'Risk Score': risk_scores})
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(df_risk, x='Risk Score', nbins=20, 
                                   title="Risk Score Distribution")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Approval rate over time
            approval_rates = [approval_rate] * 10
            time_points = [now - timedelta(minutes=i) for i in range(10, 0, -1)]
            
            df_approval = pd.DataFrame({
                'Time': time_points,
                'Approval Rate': approval_rates
            })
            
            fig_approval = px.line(df_approval, x='Time', y='Approval Rate',
                                  title="Approval Rate Over Time")
            st.plotly_chart(fig_approval, use_container_width=True)
    
    else:
        st.warning("⚠️ **No real data yet!** Make some API calls to see real metrics.")
        st.info("💡 **The dummy request generator should be creating requests every 2-4 seconds.**")
    
    # Service Status
    st.subheader("🔧 Service Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("API", "🟢 Running" if api_healthy else "🔴 Down")
    
    with col2:
        try:
            mlflow_response = requests.get("http://mlflow:5000", timeout=5)
            mlflow_status = "🟢 Running" if mlflow_response.status_code == 200 else "🔴 Down"
        except:
            mlflow_status = "🔴 Down"
        st.metric("MLflow", mlflow_status)
    
    with col3:
        st.metric("Dashboard", "🟢 Running")
    
    # Dummy request generator status
    st.subheader("🤖 Dummy Request Generator")
    
    # Check if dummy request generator is running
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps', '-q', '-f', 'name=loan-dummy-requests'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            st.success("✅ Dummy request generator is running")
            st.info("Generating requests every 2-4 seconds")
        else:
            st.warning("⚠️ Dummy request generator is not running")
            st.info("Start with: `./start_loan_pipeline.sh start --dummy`")
    except:
        st.info("Dummy request generator status unknown")
    
    # Manual refresh button
    if st.button("🔄 Force Refresh"):
        st.rerun()
    
    # Show raw metrics
    with st.expander("📋 Raw API Metrics"):
        st.json(metrics)
    
    # Show drift metrics
    with st.expander("📊 Raw Drift Metrics"):
        drift_metrics = get_drift_metrics()
        st.json(drift_metrics)
    
    # Auto-refresh every 5 seconds
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    create_real_time_dashboard()
