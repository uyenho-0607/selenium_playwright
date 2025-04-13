from typing import Dict, List
import os
import json


class ParallelConfig:
    @staticmethod
    def get_parallel_config() -> Dict:
        """Get parallel execution configuration"""
        return {
            'web': {
                'chrome': ['--browser', 'chrome'],
                'firefox': ['--browser', 'firefox'],
                'playwright': ['--browser', 'playwright']
            },
            'mobile': {
                'android': ['--platform', 'android'],
                'ios': ['--platform', 'ios']
            }
        }

    @staticmethod
    def generate_execution_list(markers: List[str] = None, platforms: List[str] = None) -> List[List[str]]:
        """
        Generate execution list for parallel runs
        :param markers: List of test markers to run
        :param platforms: List of platforms to run on
        :return: List of pytest command arguments
        """
        execution_list = []
        base_args = ['-v', '--alluredir=framework/reports/allure-results']
        
        if markers:
            for marker in markers:
                base_args.extend(['-m', marker])
        
        config = ParallelConfig.get_parallel_config()
        
        if not platforms:
            platforms = list(config.keys())
        
        for platform in platforms:
            if platform == 'web':
                for browser, browser_args in config['web'].items():
                    args = base_args.copy()
                    args.extend(['--platform', 'web'])
                    args.extend(browser_args)
                    execution_list.append(args)
            elif platform == 'mobile':
                for device, device_args in config['mobile'].items():
                    args = base_args.copy()
                    args.extend(device_args)
                    execution_list.append(args)
        
        return execution_list

    @staticmethod
    def save_execution_plan(execution_list: List[List[str]], output_file: str = 'execution_plan.json'):
        """Save execution plan to file"""
        plan = {
            'total_combinations': len(execution_list),
            'execution_list': [' '.join(args) for args in execution_list]
        }
        
        with open(output_file, 'w') as f:
            json.dump(plan, f, indent=2)

    @staticmethod
    def get_worker_count() -> int:
        """Get optimal number of parallel workers"""
        cpu_count = os.cpu_count() or 1
        return max(1, cpu_count - 1)  # Leave one CPU for system 