import qnexus as qnx
qnx.login_with_credentials()
qnx.devices.get_all().df()