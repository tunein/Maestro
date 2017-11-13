import json

def main(event, context):
	print("Value = " + event['key1'])
	print("Value = " + event['key2'])
	print("Value = " + event['key3'])
	string = "this is a MONDAY morning update pt 3"
	return string
