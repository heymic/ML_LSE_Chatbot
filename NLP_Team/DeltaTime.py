"""
Library for SUTime integration

paper: https://nlp.stanford.edu/pubs/lrec2012-sutime.pdf
"""


import os
import json
from sutime import SUTime
from autocorrect import spell


class timeDelta:

	def __init__(self, path):
		# Initialize SUtime

		jar_files = os.path.join(os.path.dirname(path), 'jars')
		self.sutime = SUTime(jars=jar_files, 
			mark_time_ranges=False, include_range=True)

	def get_times(self, text):
		# get all time values found by SUtime

		parsed = self.sutime.parse(text)
		values = []

		for dic in parsed:
			values.append(dic['value'])

		return values
