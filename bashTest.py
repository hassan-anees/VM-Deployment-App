import subprocess

bashCommand = 'chmod 400 key55.pem'
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()