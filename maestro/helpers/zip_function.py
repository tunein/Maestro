#External libs
import zipfile
import sys
import os

#This is only here for printing pretty colors
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def zip_function(lambda_name):
  '''
  Zips up our function and all dependencies to be uploaded to the lambda specified in lambda name

  args:
    lambda_name: name of the lambda, retrieved from the config file
  '''
  output_path = os.getcwd() + '/%s.zip' % lambda_name
  folder_path = os.curdir + '/dist'
  grab_lambda = os.walk(folder_path)
  length = len(folder_path)

  try:
    zipped_lambda = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for root, folders, files in grab_lambda:
      for folder_name in folders:
        absolute_path = os.path.join(root, folder_name)
        shortened_path = os.path.join(root[length:], folder_name)
        print(color.CYAN + "Adding '%s' to package." % shortened_path + color.END)
        zipped_lambda.write(absolute_path, shortened_path)
      for file_name in files:
        absolute_path = os.path.join(root, file_name)
        shortened_path = os.path.join(root[length:], file_name)
        print(color.CYAN + "Adding '%s' to package." % shortened_path + color.END)
        zipped_lambda.write(absolute_path, shortened_path)
    print(color.CYAN + "'%s' lambda packaged successfully." % lambda_name + color.END)
    return True
  except IOError:
    print(message)
    sys.exit(1)
  except OSError:
    print(message)
    sys.exit(1)
  except zipfile.BadZipfile:
    print(message)
    sys.exit(1)
  finally:
    zipped_lambda.close()