import pytest
from typing import Generator, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from playwright.sync_api import sync_playwright, Browser, Page
from appium import webdriver as appium_webdriver
from framework.config.config import Config
import allure
import json
import os
import datetime
import time
import socket
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from framework.core.browser_manager import BrowserManager
from framework.config.config import Config as TestConfig
from framework.config.parallel_config import ParallelConfig
from framework.utils.reporting import TestReporting


@pytest.fixture(scope="function")
def selenium_driver() -> Generator:
    """
    Fixture for Selenium WebDriver
    """
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.implicitly_wait(Config.IMPLICIT_WAIT)
    driver.maximize_window()
    yield driver
    allure.attach(
        driver.get_screenshot_as_png(),
        name="screenshot",
        attachment_type=allure.attachment_type.PNG
    )
    driver.quit()


@pytest.fixture(scope="function")
def playwright_page() -> Generator[Page, None, None]:
    """
    Fixture for Playwright Page
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(**Config.get_playwright_config())
        context = browser.new_context()
        page = context.new_page()
        yield page
        if page:
            allure.attach(
                page.screenshot(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG
            )
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def android_driver() -> Generator:
    """
    Fixture for Android Appium WebDriver
    """
    driver = appium_webdriver.Remote(
        command_executor=Config.APPIUM_HUB,
        desired_capabilities=Config.get_android_capabilities()
    )
    yield driver
    if driver:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG
        )
        driver.quit()


@pytest.fixture(scope="function")
def ios_driver() -> Generator:
    """
    Fixture for iOS Appium WebDriver
    """
    driver = appium_webdriver.Remote(
        command_executor=Config.APPIUM_HUB,
        desired_capabilities=Config.get_ios_capabilities()
    )
    yield driver
    if driver:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG
        )
        driver.quit()


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--platform",
        action="store",
        default="web",
        help="Platform to run tests on: web, android, or ios"
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser to use for web tests"
    )
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        help="Environment to run tests against"
    )
    parser.addoption(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.addoption(
        "--workers",
        action="store",
        default=None,
        help="Number of parallel workers"
    )
    parser.addoption(
        "--video",
        action="store_true",
        help="Record video of test execution"
    )
    parser.addoption(
        "--performance",
        action="store_true",
        help="Collect performance metrics"
    )
    parser.addoption(
        "--distributed",
        action="store_true",
        help="Enable distributed test execution"
    )
    parser.addoption(
        "--node-id",
        action="store",
        default=socket.gethostname(),
        help="Node identifier for distributed execution"
    )
    parser.addoption(
        "--master",
        action="store",
        help="Master node address for distributed execution"
    )
    parser.addoption(
        "--retries",
        action="store",
        type=int,
        default=0,
        help="Number of times to retry failed tests"
    )
    parser.addoption(
        "--flaky-tests-only",
        action="store_true",
        help="Only retry tests marked as flaky"
    )


@pytest.fixture(scope="session")
def browser_manager():
    """Fixture for browser manager instance"""
    return BrowserManager()


@pytest.fixture(scope="function")
def driver(request, browser_manager):
    """Dynamic driver fixture based on platform"""
    platform = request.config.getoption("--platform")
    browser = request.config.getoption("--browser")
    
    driver = browser_manager.get_driver(platform, browser)
    yield driver
    browser_manager.quit_driver(driver)


@pytest.fixture(scope="session", autouse=True)
def performance_data():
    """Fixture to collect performance data"""
    data = {
        "tests": {},
        "summary": {
            "total_duration": 0,
            "average_duration": 0,
            "slowest_tests": [],
            "fastest_tests": []
        }
    }
    yield data
    
    # Calculate summary statistics
    if data["tests"]:
        durations = [t["duration"] for t in data["tests"].values()]
        data["summary"]["total_duration"] = sum(durations)
        data["summary"]["average_duration"] = sum(durations) / len(durations)
        
        # Sort tests by duration
        sorted_tests = sorted(data["tests"].items(), key=lambda x: x[1]["duration"])
        data["summary"]["fastest_tests"] = sorted_tests[:5]
        data["summary"]["slowest_tests"] = sorted_tests[-5:]
        
        # Save performance report
        with open("framework/reports/results/performance_report.json", "w") as f:
            json.dump(data, f, indent=2)


@pytest.fixture(scope="session")
def test_reporting():
    """Fixture for test reporting instance"""
    return TestReporting()


def pytest_configure(config: Config):
    """Enhanced test configuration with retry, distributed, and reporting support"""
    # Set up custom markers
    config.addinivalue_line("markers", "web: mark test as web test")
    config.addinivalue_line("markers", "mobile: mark test as mobile test")
    config.addinivalue_line("markers", "android: mark test as android test")
    config.addinivalue_line("markers", "ios: mark test as ios test")
    
    if config.getoption("--parallel"):
        workers = config.getoption("--workers") or ParallelConfig.get_worker_count()
        config.option.numprocesses = int(workers)
    
    # Create results directories
    for dir_name in ["results", "videos", "screenshots", "logs", "trends"]:
        os.makedirs(os.path.join("framework", "reports", dir_name), exist_ok=True)
    
    # Enhanced run info
    run_info = {
        "start_time": datetime.datetime.now().isoformat(),
        "platform": config.getoption("--platform"),
        "browser": config.getoption("--browser"),
        "environment": config.getoption("--env"),
        "parallel": config.getoption("--parallel"),
        "workers": config.option.numprocesses if config.getoption("--parallel") else 1,
        "video_recording": config.getoption("--video"),
        "performance_monitoring": config.getoption("--performance"),
        "distributed": config.getoption("--distributed"),
        "node_id": config.getoption("--node-id") if config.getoption("--distributed") else None,
        "master": config.getoption("--master") if config.getoption("--distributed") else None
    }
    
    # Save run info with timestamp in filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_info_file = f"run_info_{timestamp}.json"
    with open(os.path.join("framework", "reports", "results", run_info_file), "w") as f:
        json.dump(run_info, f, indent=2)
    
    # Register flaky marker
    config.addinivalue_line(
        "markers",
        "flaky(reruns=int): mark test as flaky and set retry count"
    )
    
    # Configure test retries
    if config.getoption("--retries"):
        config.option.reruns = config.getoption("--retries")
        if config.getoption("--flaky-tests-only"):
            config.option.reruns_only_flaky = True
    
    # Configure distributed testing
    if config.getoption("--distributed"):
        try:
            from xdist.scheduler import LoadScheduling
            
            class CustomScheduling(LoadScheduling):
                def _split_scope(self, nodeid):
                    """Custom logic to split tests across nodes"""
                    platform = nodeid.split("::")[-2] if "::" in nodeid else "web"
                    return platform
            
            config.option.dist = "load"
            config.option.tx = [f"socket={config.getoption('--master')}"] if config.getoption("--master") else []
            config.option.scheduling = CustomScheduling
        except ImportError:
            print("pytest-xdist not installed. Distributed testing disabled.")


def pytest_sessionstart(session):
    """Called after the Session object has been created and before running tests"""
    # Set up test environment based on command line options
    TestConfig.ENVIRONMENT = session.config.getoption("--env")
    
    # Log session start
    allure.attach(
        f"Starting test session with platform: {session.config.getoption('--platform')}",
        "Session Start",
        allure.attachment_type.TEXT
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    """Enhanced session finish with reporting"""
    outcome = yield
    
    # Get test reporting fixture
    test_reporting = None
    if hasattr(session, "test_reporting"):
        test_reporting = session.test_reporting
    else:
        test_reporting = TestReporting()
    
    # Get latest run info file
    results_dir = os.path.join("framework", "reports", "results")
    run_info_files = [f for f in os.listdir(results_dir) if f.startswith("run_info_")]
    if run_info_files:
        latest_run_info = max(run_info_files)
        with open(os.path.join(results_dir, latest_run_info)) as f:
            run_info = json.load(f)
        
        # Add test statistics
        run_info.update({
            "end_time": datetime.datetime.now().isoformat(),
            "exit_status": exitstatus,
            "total_tests": session.testscollected,
            "passed": len([item for item in session.items if item.session.testsfailed == 0]),
            "failed": session.testsfailed,
            "retry_stats": {
                "total_retries": sum(getattr(item, "execution_count", 0) for item in session.items),
                "retried_tests": len([item for item in session.items if getattr(item, "execution_count", 0) > 0]),
                "flaky_tests": len([item for item in session.items if item.get_closest_marker("flaky")])
            }
        })
        
        # Save updated run info
        with open(os.path.join(results_dir, latest_run_info), "w") as f:
            json.dump(run_info, f, indent=2)
        
        # Generate reports
        test_reporting.generate_run_report(run_info)
        test_reporting.generate_trend_report()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item: Item, nextitem):
    """Enhanced test protocol with retry support"""
    # Initialize execution count
    item.execution_count = getattr(item, "execution_count", 0)
    
    # Start timing
    start_time = time.time()
    
    # Get performance data fixture
    perf_data = item.session.performance_data if hasattr(item.session, "performance_data") else None
    
    outcome = yield
    
    # Record performance data if enabled
    if perf_data and item.config.getoption("--performance"):
        duration = time.time() - start_time
        perf_data["tests"][item.nodeid] = {
            "duration": duration,
            "outcome": "passed" if outcome.get_result().passed else "failed",
            "timestamp": datetime.datetime.now().isoformat()
        }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo):
    """Enhanced test reporting with video, performance metrics, and retry information"""
    outcome = yield
    report = outcome.get_result()
    
    # Add retry information to the report
    if hasattr(item, "execution_count"):
        report.rerun = item.execution_count
    
    # Handle test retries
    if report.when == "call" and report.failed:
        flaky_marker = item.get_closest_marker("flaky")
        retries = item.config.getoption("--retries")
        
        if flaky_marker or (retries and not item.config.getoption("--flaky-tests-only")):
            max_reruns = flaky_marker.kwargs.get("reruns", retries) if flaky_marker else retries
            if getattr(item, "execution_count", 0) < max_reruns:
                item.execution_count = getattr(item, "execution_count", 0) + 1
                report.failed = False
                report.outcome = "rerun"
    
    if report.when == "call":
        driver = _get_driver_from_item(item)
        if driver:
            # Handle video recording
            if item.config.getoption("--video") and hasattr(driver, "stop_recording_screen"):
                try:
                    video_path = f"framework/reports/videos/{item.nodeid}.mp4"
                    os.makedirs(os.path.dirname(video_path), exist_ok=True)
                    driver.stop_recording_screen()
                    allure.attach.file(
                        video_path,
                        name="Test Video",
                        attachment_type=allure.attachment_type.MP4
                    )
                except Exception as e:
                    allure.attach(
                        str(e),
                        "Video Recording Error",
                        allure.attachment_type.TEXT
                    )
            
            # Collect performance metrics for web tests
            if item.config.getoption("--performance") and item.config.getoption("--platform") == "web":
                try:
                    metrics = _collect_performance_metrics(driver)
                    allure.attach(
                        json.dumps(metrics, indent=2),
                        "Performance Metrics",
                        allure.attachment_type.JSON
                    )
                except Exception as e:
                    allure.attach(
                        str(e),
                        "Performance Metrics Error",
                        allure.attachment_type.TEXT
                    )


def _get_driver_from_item(item: Item) -> Optional[Any]:
    """Helper to get driver instance from test item"""
    try:
        for fixturedef in item._fixtureinfo.name2fixturedef.values():
            if fixturedef.argname == "driver":
                return item._request.getfixturevalue("driver")
    except:
        pass
    return None


def _collect_performance_metrics(driver: Any) -> Dict:
    """Collect performance metrics from browser"""
    metrics = {}
    
    try:
        if hasattr(driver, "execute_script"):
            # Navigation Timing API metrics
            timing = driver.execute_script("return window.performance.timing.toJSON()")
            metrics["navigation_timing"] = timing
            
            # Memory usage
            memory = driver.execute_script("return window.performance.memory")
            if memory:
                metrics["memory"] = {
                    "used_js_heap_size": memory.usedJSHeapSize,
                    "total_js_heap_size": memory.totalJSHeapSize,
                    "js_heap_size_limit": memory.jsHeapSizeLimit
                }
            
            # Resource timing
            resources = driver.execute_script("""
                var resources = window.performance.getEntriesByType('resource');
                return resources.map(function(resource) {
                    return {
                        name: resource.name,
                        duration: resource.duration,
                        transferSize: resource.transferSize
                    };
                });
            """)
            metrics["resources"] = resources
    except:
        pass
    
    return metrics


class TestReport:
    """Custom test report class"""
    def __init__(self, item: Item, when: str, outcome: str, exc_info=None):
        self.nodeid = item.nodeid
        self.when = when
        self.outcome = outcome
        self.exc_info = exc_info
        self.passed = outcome == "passed"
        self.failed = outcome == "failed"
        self.skipped = outcome == "skipped"
        self.duration = 0  # Can be updated with actual duration if needed 