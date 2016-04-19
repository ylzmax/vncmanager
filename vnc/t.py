from vnc.models  import *
import paramiko

def test():
	print "start "
	s=server.objects.all()
	print s
	for i in s:
		print i.servername
#test()
def updateserver():
	ser=server.objects.all()
	for i in ser:
		vncnum,se=runcmd2(i.serverusername,i.serverpassword,i.servername,"ps -ef | grep Xvnc |grep -v grep |wc| awk '{print $1}'")
		load,se2=runcmd2(i.serverusername,i.serverpassword,i.servername,"uptime | awk '{print $10}'")
		#so=2
		if vncnum and load:
			i.totalnum=int(vncnum)	
			loadunm=int(float(load.split(",")[0])*100)
			i.load=loadunm
			if int(vncnum) > 80 or loadunm >1000:
				i.status="disable"
			else: 
				i.status="enable"
		else:
			i.status="disable"
		i.save()


def runcmd2(un,pa,hn,cmd):
	s=paramiko.SSHClient()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		s.connect(str(hn),22,str(un),str(pa))
		si,so,se=s.exec_command(cmd)
		output=so.read()
		error=se.read()
		s.close()
		return output,error
	except:
		return ("","")

def p(msg):
	print msg
	
