import json

def main(event, context):
	print("Value = " + event['key1'])
	print("Value = " + event['key2'])
	print("Value = " + event['key3'])
	string = "This is a dev test at 8:25am 9/20/17 " + event['key3']
	return string
