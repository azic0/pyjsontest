import unittest
import json
import sys
import importlib
import argparse

import numpy as np



def contains_only_floats(lst):
    for item in lst:
        if isinstance(item, list):
            if not contains_only_floats(item):
                return False
        elif not isinstance(item, float):
            return False
    return True


def assert_close_or_equal(test_case, expected, result, float_tolerance):
    if isinstance(expected, float):
        np.testing.assert_allclose(expected, result, rtol=float_tolerance)
    elif contains_only_floats(expected):
        np.testing.assert_allclose(expected, result, rtol=float_tolerance)
    else:
        test_case.assertEqual(expected, result)


def generate_test(func, params, expected_results, float_tolerance):
    def test(self):
        results = func(**params)
        if not isinstance(results, tuple):
            results = [results]
        for e, r in zip(expected_results, results):
            assert_close_or_equal(self, e, r, float_tolerance)
    return test


def generate_tests(func, test_specs, float_tolerance):
    tests = {}
    for i, test_spec in enumerate(test_specs):
        tests[f'test_{i}'] = generate_test(func, test_spec['params'], test_spec['results'], float_tolerance)
    return tests


def generate_test_class(func, test_specs, float_tolerance):
    tests = generate_tests(func, test_specs, float_tolerance)
    return type(f'Test_{func.__name__}', (unittest.TestCase,), tests)


def generate_test_suite(test_suite_specs, module_name=None, float_tolerance=1.e-7):
    if not module_name:
        module = sys.modules['__main__']
    else:
        module = importlib.import_module(module_name)

    suite = unittest.TestSuite()
    for func_name, test_specs in test_suite_specs.items():
        func = getattr(module, func_name)
        TestClass = generate_test_class(func, test_specs, float_tolerance)
        test_class_suite = unittest.TestLoader().loadTestsFromTestCase(TestClass)
        suite.addTest(test_class_suite)
    return suite


def generate_test_suite_from_json_file(json_file, module_name, float_tolerance=1.e-7):
    with open(json_file, 'r') as f:
        test_suite_specs = json.load(f)
    return generate_test_suite(test_suite_specs, module_name, float_tolerance)


def run_json_tests(json_file, module_name, float_tolerance=1.e-7, verbosity=0):
    test_suite = generate_test_suite_from_json_file(json_file, module_name, float_tolerance)
    unittest.TextTestRunner(verbosity=verbosity).run(test_suite)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run tests based on a JSON file and optional module name.")
    
    parser.add_argument("json_file", type=str, help="Path to the JSON file.")
    parser.add_argument("--module", type=str, default="", help="Optional module name.")
    parser.add_argument("--verbosity", type=int, choices=[0, 1, 2], default=0, help="Set verbosity level.")
    parser.add_argument("--ftol", type=float, default=1.e-7, help="Float tolerance for numerical comparisons.")
    
    args = parser.parse_args()

    run_json_tests(args.json_file, args.module, args.ftol, args.verbosity)

