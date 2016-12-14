# Class for accessing the relevant TfL page
import getTflBikePoints

# Run selenium using multiprocessing
from parallel_selenium import run_parallel_selenium, Test

if __name__ == '__main__':
	# Get list of data
	dataList = getTflBikePoints.bikePoints('https://api.tfl.gov.uk/BikePoint')

	# Individual test parameters: (function, processing_message, assert_type, to_compare, url, args)
	tests = [Test(
				function=util_selenium.getElementTextByClass,
				function_args=['nearby-list-heading'],
				processing_message='Querying {}'.format(i[0]),
				assert_type='equals',
				to_compare=i[1],
				url='https://lilac.online.tfl.gov.uk/maps/cycle-hire?bikepoint=' + i[0])
			for i in dataList]

	#Run it!
	run_parallel_selenium(tests, 'testResults.txt')
