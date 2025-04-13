import json
import os
import datetime
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader


class TestReporting:
    def __init__(self, reports_dir: str = "framework/reports"):
        self.reports_dir = reports_dir
        self.results_dir = os.path.join(reports_dir, "results")
        self.trends_dir = os.path.join(reports_dir, "trends")
        self.templates_dir = os.path.join("framework", "templates")
        
        # Create necessary directories
        for dir_path in [self.results_dir, self.trends_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def generate_trend_report(self):
        """Generate trend report from historical test runs"""
        trend_data = self._collect_historical_data()
        if not trend_data:
            return
        
        # Create trend graphs
        self._create_pass_fail_trend(trend_data)
        self._create_duration_trend(trend_data)
        self._create_flaky_tests_trend(trend_data)
        
        # Generate HTML report
        self._generate_trend_html(trend_data)
    
    def generate_run_report(self, run_info: Dict):
        """Generate detailed HTML report for current test run"""
        # Load performance data
        perf_data = self._load_performance_data()
        
        # Generate test execution timeline
        timeline_data = self._generate_timeline(perf_data)
        
        # Generate performance graphs
        perf_graphs = self._generate_performance_graphs(perf_data)
        
        # Create HTML report
        self._generate_run_html(run_info, timeline_data, perf_graphs)
    
    def _collect_historical_data(self) -> List[Dict]:
        """Collect data from previous test runs"""
        trend_data = []
        for filename in os.listdir(self.results_dir):
            if filename.startswith("run_info_") and filename.endswith(".json"):
                with open(os.path.join(self.results_dir, filename)) as f:
                    run_data = json.load(f)
                    trend_data.append(run_data)
        return sorted(trend_data, key=lambda x: x["start_time"])
    
    def _create_pass_fail_trend(self, trend_data: List[Dict]):
        """Create pass/fail trend graph"""
        dates = [run["start_time"][:10] for run in trend_data]
        passed = [run.get("passed", 0) for run in trend_data]
        failed = [run.get("failed", 0) for run in trend_data]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=passed, name="Passed", line=dict(color="green")))
        fig.add_trace(go.Scatter(x=dates, y=failed, name="Failed", line=dict(color="red")))
        
        fig.update_layout(title="Test Results Trend", xaxis_title="Date", yaxis_title="Number of Tests")
        fig.write_html(os.path.join(self.trends_dir, "pass_fail_trend.html"))
    
    def _create_duration_trend(self, trend_data: List[Dict]):
        """Create test duration trend graph"""
        dates = [run["start_time"][:10] for run in trend_data]
        durations = []
        
        for run in trend_data:
            start = datetime.datetime.fromisoformat(run["start_time"])
            end = datetime.datetime.fromisoformat(run["end_time"])
            duration = (end - start).total_seconds() / 60  # Convert to minutes
            durations.append(duration)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=durations, name="Duration"))
        
        fig.update_layout(title="Test Duration Trend", xaxis_title="Date", yaxis_title="Duration (minutes)")
        fig.write_html(os.path.join(self.trends_dir, "duration_trend.html"))
    
    def _create_flaky_tests_trend(self, trend_data: List[Dict]):
        """Create flaky tests trend graph"""
        dates = [run["start_time"][:10] for run in trend_data]
        flaky_tests = [run.get("retry_stats", {}).get("flaky_tests", 0) for run in trend_data]
        retried_tests = [run.get("retry_stats", {}).get("retried_tests", 0) for run in trend_data]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=flaky_tests, name="Flaky Tests"))
        fig.add_trace(go.Scatter(x=dates, y=retried_tests, name="Retried Tests"))
        
        fig.update_layout(title="Test Flakiness Trend", xaxis_title="Date", yaxis_title="Number of Tests")
        fig.write_html(os.path.join(self.trends_dir, "flaky_tests_trend.html"))
    
    def _load_performance_data(self) -> Dict:
        """Load performance data from current run"""
        perf_file = os.path.join(self.results_dir, "performance_report.json")
        if os.path.exists(perf_file):
            with open(perf_file) as f:
                return json.load(f)
        return {}
    
    def _generate_timeline(self, perf_data: Dict) -> Dict:
        """Generate test execution timeline"""
        timeline = []
        for test_id, test_data in perf_data.get("tests", {}).items():
            timeline.append({
                "test_id": test_id,
                "start_time": test_data["timestamp"],
                "duration": test_data["duration"],
                "outcome": test_data["outcome"]
            })
        return sorted(timeline, key=lambda x: x["start_time"])
    
    def _generate_performance_graphs(self, perf_data: Dict) -> Dict:
        """Generate performance-related graphs"""
        graphs = {}
        
        # Test duration distribution
        durations = [t["duration"] for t in perf_data.get("tests", {}).values()]
        if durations:
            fig = go.Figure(data=[go.Histogram(x=durations)])
            fig.update_layout(title="Test Duration Distribution", xaxis_title="Duration (seconds)", yaxis_title="Count")
            graphs["duration_dist"] = fig.to_html()
        
        # Memory usage over time (if available)
        memory_data = []
        for test_data in perf_data.get("tests", {}).values():
            if "memory" in test_data:
                memory_data.append({
                    "timestamp": test_data["timestamp"],
                    "used_memory": test_data["memory"]["used_js_heap_size"] / (1024 * 1024)  # Convert to MB
                })
        
        if memory_data:
            df = pd.DataFrame(memory_data)
            fig = go.Figure(data=[go.Scatter(x=df["timestamp"], y=df["used_memory"])])
            fig.update_layout(title="Memory Usage Over Time", xaxis_title="Time", yaxis_title="Used Memory (MB)")
            graphs["memory_usage"] = fig.to_html()
        
        return graphs
    
    def _generate_trend_html(self, trend_data: List[Dict]):
        """Generate HTML trend report"""
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template("trend_report.html")
        
        html_content = template.render(
            trend_data=trend_data,
            generated_at=datetime.datetime.now().isoformat()
        )
        
        with open(os.path.join(self.trends_dir, "trend_report.html"), "w") as f:
            f.write(html_content)
    
    def _generate_run_html(self, run_info: Dict, timeline_data: List[Dict], perf_graphs: Dict):
        """Generate HTML report for current run"""
        env = Environment(loader=FileSystemLoader(self.templates_dir))
        template = env.get_template("run_report.html")
        
        html_content = template.render(
            run_info=run_info,
            timeline_data=timeline_data,
            perf_graphs=perf_graphs,
            generated_at=datetime.datetime.now().isoformat()
        )
        
        with open(os.path.join(self.results_dir, "run_report.html"), "w") as f:
            f.write(html_content) 