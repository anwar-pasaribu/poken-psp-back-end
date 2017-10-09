import csv

def open_data():
	with open('lokasi.csv', 'rb') as csvfile:
		# myreader = csv.reader(csvfile, delimiter=',', quotechar='|')
		# id,kelurahan,kecamatan,kabupaten,provinsi,kodepos
		fieldnames = ['id', 'kelurahan', 'kecamatan','kabupaten','provinsi', 'kodepos']
		myreader = csv.DictReader(csvfile, fieldnames=fieldnames)
		
		for row in myreader:
			# print ', '.join(row)
			# print '-' , row
			# print "Keys size %d" % len(row.keys())
			print (''.join('%s - ' % (row[s]) for s in fieldnames))

if __name__ == '__main__':
	open_data()