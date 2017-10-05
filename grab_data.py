#!/usr/bin/env python3.6
import urllib.request
from datetime import datetime,timedelta
import sys
import gzip
import io
import os


if not len(sys.argv) == 4:
	print ('usage: ./grab_data <base> start_time end_time')
	exit(1)


date_format = '%Y-%m-%dT%H:%M:%SZ'
real_url = 'ftp://www.ngs.noaa.gov/cors/rinex/2017/257/nybp/nybp2570.17o.gz'
url = 'ftp://www.ngs.noaa.gov/cors/rinex/<year>/<day_of_year>/<base>/<base><day><block>.<year_last_two_digit>o.gz'



#read inputs
base, start, end = sys.argv[1].strip(),sys.argv[2].strip(), sys.argv[3].strip()

start_date = datetime.strptime(start,date_format)
end_date = datetime.strptime(end,date_format)
start_year = start_date.year
end_year = end_date.year

start_day = start_date.timetuple().tm_yday
end_day = end_date.timetuple().tm_yday

output_file = base+'.obs'

current = datetime(start_date.year,start_date.month,start_date.day,start_date.hour)
last = datetime(end_date.year,end_date.month,end_date.day,end_date.hour)
file_pool = []


#download data
try:
	while(current <= last):
		year = str(current.year)
		day_of_year = str(current.timetuple().tm_yday)
		block = chr(ord('a') + int(current.hour))
		year_last_two_digit = year[2:]
		url = 'ftp://www.ngs.noaa.gov/cors/rinex/%s/%s/%s/%s%s%c.%so.gz' % (year,day_of_year,base,base,day_of_year,block,year_last_two_digit)
		file_name = '%s%s%c.%so' % (base, day_of_year,block,year_last_two_digit)
		
		source_file = urllib.request.urlopen(url, file_name)
		compressed_file = io.BytesIO(source_file.read())
		decompressed_file = gzip.GzipFile(fileobj = compressed_file)
		with open(file_name,'wb+') as outputfile:
			outputfile.write(decompressed_file.read())

		file_pool.append(file_name)

		print ('download'+url)
		current += timedelta(hours=1)
except:


	#Once hourly data is not found, download daily data
	print ('hour file is not found, program will download daily data')

	for file in file_pool:
		os.remove(file)


	current = datetime(start_date.year,start_date.month,start_date.day)
	last = datetime(end_date.year,end_date.month,end_date.day)
	while (current <= last):
		try:
			year = str(current.year)
			day_of_year = str(current.timetuple().tm_yday)
			block = chr(ord('a') + int(current.hour))
			year_last_two_digit = year[2:]
			url = 'ftp://www.ngs.noaa.gov/cors/rinex/%s/%s/%s/%s%s0.%so.gz' % (year,day_of_year,base,base,day_of_year,year_last_two_digit)
			file_name = '%s%s0.%so' % (base, day_of_year,year_last_two_digit)

			#unzip file


			source_file = urllib.request.urlopen(url, file_name)
			compressed_file = io.BytesIO(source_file.read())
			decompressed_file = gzip.GzipFile(fileobj = compressed_file)
			with open(file_name,'wb+') as outputfile:
				outputfile.write(decompressed_file.read())

			

			file_pool.append(file_name)

			print ('download',url)


			current += timedelta(days=1)


		except:
			print ('downloading is interruptted. file does not exist')

finally:

	#merge file

	print ('start to merge files')
	all_file = ''
	for file in file_pool:
		all_file += file + ' '

	command = './teqc ' + all_file + '> ' + output_file
	os.system(command)


	for file in file_pool:
		os.remove(file)


	print ('exucation finished!')













