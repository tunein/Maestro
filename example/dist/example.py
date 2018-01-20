import json

def main(event, context):
	print("Value = " + event['key1'])
	print("Value = " + event['key2'])
	print("Value = " + event['key3'])
	string = "Finishing weighted alias"
	return string
