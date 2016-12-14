import multiprocessing as mp
import logging, sys, os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from util_selenium import *

def initLogger(path):
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

# Init pool and divide tasks between processes
#
# test_list -> [(meth, pass_message, fail_message, URL, [args]), (...), ...]
def run_parallel_selenium(test_list, log_path, num_processes=0):

	#Init logger
	global logger
	logger = initLogger(log_path)

	# Init test queue
	tests = mp.JoinableQueue()

	# Init results queue
	results = mp.Queue()

	# Queue up all tests in the list
	for t in test_list:
		tests.put(t)

	# If invalid number of processes entered then default to max
	if num_processes <= 0:
		num_browsers = mp.cpu_count()
	# Otherwise go with user's number
	else:
		num_browsers = num_processes

	# Add stop flags to end of test queue for each process
	for p in xrange(num_browsers):
		tests.put(None)

	# Init browser processes
	browserProcesses = [browserProcess(tests, results)
						for i in xrange(num_browsers)]

	# Start browser processes
	for p in browserProcesses:
		p.start()

	# Wait for all tests to finish
	tests.close()
	tests.join()

	# Close browsers and terminate processes
	for p in browserProcesses:
		p.driver.quit()
		p.terminate()

	# Print results queue as summary in simple log
	logger.debug('--- TEST RESULTS SUMMARY---')
	num_tests = len(test_list)
	for t in xrange(num_tests):
		result = results.get()
		logger.debug(result)

	#Quit program
	sys.exit()


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

			# If stop flag encountered break the loop
			if next_test is None:
				self.test_queue.task_done()
				break

			# Otherwise PERFORM THE TEST (i.e. invoke __call__ on the popped object) and store the result in a queue
			result = next_test(self.driver)
			self.result_queue.put(result)

			self.test_queue.task_done()

# Each Test is a single test
# Pass a list of these into a run_[multiple|single]_selenium def
class Test(object):

	def __init__(self, function, function_args, processing_message, assert_type, to_compare, url):
		self.function = function
		self.args = function_args
		self.processing_message = processing_message
		self.assert_type = assert_type
		self.to_compare = to_compare
		self.url = url

	def __call__(self, driver):
		# Get the query result from Selenium
		queryResult = self.function(driver, self.url, *self.args)

		# Check for existence in returned list
		if self.assert_type == 'exists':
			if to_compare in queryResult:
				testResult = '{:<50}: - PASS - {} exists in queried {}'.format(self.processing_message, self.to_compare, queryResult)
			else:
				testResult = '{:<50}: - FAIL - {} does NOT exist in queried {}'.format(self.processing_message, self.to_compare, queryResult)

		# Exact match required (if match_type is 'equals' or anything else)
		elif self.assert_type == 'equals':
			if queryResult == self.to_compare:
				testResult = '{:<50}: - PASS - queried {} is equal to {}'.format(self.processing_message, queryResult, self.to_compare)
			else:
				testResult = '{}: - FAIL - queried {} is NOT equal to {}'.format(self.processing_message, queryResult, self.to_compare)

		# Otherwise invalid assert_type entered
		else:
			testResult = '- ASSERT ERROR - {} assertion not valid; {} not queried and {} not tested'.format(self.assert_type, queryResult)

		# Log the result
		logger.debug(testResult)

		return testResult

# UNIT TESTS e.g.
if __name__ == '__main__':

	l = [i for i in xrange(10)]

	tests = [Test(
				function=getElementTextByClass,
				function_args=['headline-container'],
				processing_message='Querying bikepoint {}'.format(j),
				assert_type='equals',
				to_compare='SANTANDER CYCLES',
				url='https://lilac.online.tfl.gov.uk/maps/cycle-hire?bikepoint=' + str(j))
			for j in l]

	run_parallel_selenium(tests, 'testResults.txt')
