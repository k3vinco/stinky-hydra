import multiprocessing as mp
import logging, sys, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from util_selenium import *


class Mp_Selenium(object):
	def __init__(self, test_list, log_path, num_processes=0):
		self._logger = self._init_logger(log_path)
		self._tests = self._load_tests(test_list)
		self._results = mp.Queue()
		self._browsers = self._init_browsers(num_processes)

	def _init_browsers(self, num_processes)
		if num_processes <= 0:
			num_browsers = mp.cpu_count()
		else:
			num_browsers = num_processes
		
		return [browserProcess(self._tests, self._results)
						for i in xrange(num_browsers)]

	def _load_tests(self, test_list):
		q = mp.JoinableQueue()
		for test in test_list:
			q.put(test)
		return q

	def _init_logger(self, path):
		logger = logging.getLogger()
		logger.setLevel(logging.DEBUG)

		formatter = logging.Formatter('%(asctime)s - %(message)s')

		# Delete the existing file
		os.remove(path)

		fh = logging.FileHandler(path)
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(formatter)

		# Add file handler to logger
		logger.addHandler(fh)

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(formatter)

		# Add stream handler to logger
		logger.addHandler(ch)

		return logger

	def run(self):
		for process in self._browsers:
			process.start()

		# Block until all tests finish
		tests.close()
		tests.join()

		# Close browsers and terminate processes
		for p in browserProcesses:
			p.driver.quit()
			p.terminate()

		# Print results queue as summary in simple log
		logger.info('--- TEST RESULTS SUMMARY---')
		num_tests = len(test_list)
		for t in xrange(num_tests):
			result = results.get()
			logger.info(result)

class browserProcess(mp.Process):

	# Reference the test queue with local variable
	def __init__(self, test_queue, result_queue):
		super(browserProcess, self).__init__()
		self.test_queue = test_queue
		self.result_queue = result_queue
		self.driver = webdriver.Firefox()

	# Runs when start() is called
	def run(self):

		# Keep going through test queue and popping off tasks
		while True:
			# Get next test from queue
			next_test = self.test_queue.get()
			self.test_queue.task_done()

			# Perform the test and store the result in a queue
			result = next_test(self.driver)
			self.result_queue.put(result)

# Each Test is a single test
# Pass a list of these into a run_[multiple|single]_selenium def
class Test(object):

	def __init__(self, function, function_args, processing_message, assert_type, to_compare, url):
		self._function = function
		self._args = function_args
		self._processing_message = processing_message
		self._assert_type = assert_type
		self._to_compare = to_compare
		self._url = url

	def __call__(self, driver):
		# Get the query result from Selenium
		queryResult = self._function(driver, self._url, *self._args)

		# Check for existence in returned list
		if self._assert_type == 'exists':
			if to_compare in queryResult:
				testResult = '{:<50}: - PASS - {} exists in queried {}'.format(self._processing_message, self._to_compare, queryResult)
			else:
				testResult = '{:<50}: - FAIL - {} does NOT exist in queried {}'.format(self._processing_message, self._to_compare, queryResult)

		# Exact match required (if match_type is 'equals' or anything else)
		elif self._assert_type == 'equals':
			if queryResult == self._to_compare:
				testResult = '{:<50}: - PASS - queried {} is equal to {}'.format(self._processing_message, queryResult, self._to_compare)
			else:
				testResult = '{}: - FAIL - queried {} is NOT equal to {}'.format(self._processing_message, queryResult, self._to_compare)

		# Otherwise invalid assert_type entered
		else:
			testResult = '- ASSERT ERROR - {} assertion not valid; {} not queried and {} not tested'.format(self._assert_type, queryResult)

		# Log the result
		logger.debug(testResult)

		return testResult

# UNIT TESTS e.g.
if __name__ == '__main__':

	tests = [Test(
				function=getElementTextByClass,
				function_args=['headline-container'],
				processing_message='Querying bikepoint {}'.format(j),
				assert_type='equals',
				to_compare='SANTANDER CYCLES',
				url='https://lilac.online.tfl.gov.uk/maps/cycle-hire?bikepoint=' + str(j))
			for j in xrange(10)]

	run_parallel_selenium(tests, 'testResults.txt')
