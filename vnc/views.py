from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.core import serializers
import json
import socket
import nis,crypt
import paramiko
from vnc.models import *
import os,re,stat
from multiprocessing import Pool,Queue
#from django.contrib import auth

# Create your views here.
q=Queue()
def logincheck(func):
	def usercheck(req,*args,**kwargs):
		try:
			if req.session["username"]:
				return func(req)
		except:
			#return render(req,"login.htm")	
			return HttpResponseRedirect('/login')
	
	return usercheck	

def nischeck(username,password):
	if username:
		try:
			un=nis.match(username,"passwd").split(":")[1]
			if un.__len__()> 16:
				if crypt.crypt(password,un[0:12])==un:
					return 1
				else:
					return 0
			else:
				if crypt.crypt(password,un)==un:
					return 1
				else:
					return 0
			
		except:
			return 0
def login(req):
	if req.method=="POST":
		username=req.POST.get("username")
		password=req.POST.get("password")
		if nischeck(username,password):
			#auth.login(req,str(username))
			req.session['username']=username
			req.session['password']=password
			req.session['searchlocalvnc']=1
			return HttpResponseRedirect('/index')
		else:

			return render(req,"login.htm",{'error':"Wrong username or password!"})
	return render(req,"login.htm")

@logincheck	
def index(req):
	username=req.session['username']
	vncinfo=vncserver.objects.filter(username=username)
	if req.session["searchlocalvnc"]:
		#getlocalvnc(req)
		getlocalvncinfo=True
	else:
	#	req.session['searchlocalvnc']=0
		getlocalvncinfo=False
	return render(req,"index.html",{"username":username,"vncinfo":vncinfo,"getlocalvncinfo":getlocalvncinfo})

def getvncpid(file):
	if file:
		f=open(file,"ro")
		res=f.readlines()
		f.close()
		return res
	else:
		return 0

def createnew(req):
	#serverinfo=server.objects.all()
	print req.method
	if req.method=="POST":
		geometry=str(req.POST["geometry"])
		depth=str(req.POST["depth"])
		username=req.session['username']
		chserver=server.objects.filter(status="enable").order_by("totalnum","load")[0]
		print chserver
		so,se=runcmd(req,chserver.serverip,"vncserver -geometry %s -depth %s"%(geometry,depth))
		if "Starting applications specified" in se:
			print se
			newport=re.search(":(\d\d|\d)",se).group()
			print newport
			vncdb=vncserver(servername=chserver.servername,ip=chserver.serverip,geometry=geometry,depth=depth,port=newport,username=username)
			vncdb.save()
			servercount=server.objects.get(servername=chserver.servername)
			chserver.totalnum=int(chserver.totalnum)+1
			chserver.save()
			res=chserver.servername+newport
			return HttpResponse(res)
		else:
			return HttpResponse("Vnc Create Error! %s"%se)

def createresult(req,res):
	return render(req,"createresult.htm",{"res":res})

def runcmd(req,hn,cmd):
	if cmd:
		s=paramiko.SSHClient()
		s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		user=req.session["username"]
		passw=req.session["password"]
		s.connect(str(hn),22,str(user),str(passw))
		try:
			si,so,se=s.exec_command(cmd)
			output=so.read()
			error=se.read()
			s.close()
			return output,error
		except:
			return 0
	else:
		return 0

def changevncpassword(req):
	s=paramiko.SSHClient()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	user=req.session["username"]
	passw=req.session["password"]
	vncpassword=str(req.POST["vncpassword"])
	chserver=server.objects.filter(status="enable").order_by("load")[0]
	s.connect(chserver.servername,22,str(user),str(passw))
	try:
		chan=s.invoke_shell()
		chan.send('vncpasswd\n')
		buff = ''
		while not buff.endswith("Password:"):
		    resp = chan.recv(9999)
		    buff +=resp
		chan.send("%s\n"%vncpassword)
		buff=""
		while not buff.endswith('Verify:'):
		    resp = chan.recv(9999)
		    buff +=resp
		chan.send("%s\n"%vncpassword)
		s.close()
		return HttpResponse("sucess")
	except:
		return HttpResponse("false")


def logout(req):
	#auth.logout(req)
	req.session.flush()
	return HttpResponseRedirect("/login")


def test(req):
	data=serializers.serialize("json",vncserver.objects.filter(username=req.session["username"]))
	print data
	
	return data


def kill(req):
	if req.method == "POST":
		servername=req.POST['servername']
		serverport=req.POST['serverport']
		print servername
		print serverport
		so,se=runcmd(req,servername,"vncserver -kill %s"%serverport)
		print se
		#so1,se1=runcmd(req,servername,"rm -f /home/%s/.vnc/*%s.pid"%(req.session["username"],serverport,serverport))
		#print so1
		if se:
			data=vncserver.objects.filter(servername=servername,port=serverport)
			data.delete()
			return HttpResponse(se)
		else:
			return HttpResponse("Error !")
		
		

def recreate(req):
	if req.method == "POST":
		servername=req.POST['servername']
		serverport=req.POST['serverport']
		servergeometry=req.POST['geometry']
		serverdepth=req.POST['depth']
		print servergeometry
		print serverdepth
		so,se=runcmd(req,servername,"vncserver -kill %s"%serverport)
		print se
		if "Killing Xvnc process ID" in se:
			so1,se1=runcmd(req,servername,"vncserver %s -geometry %s -depth %s"%(serverport,servergeometry,serverdepth))
			print se1
			return HttpResponse(se1)
		else:
			return 0


def getusername(req):
	print req.method
	if req.session['username']:
		return HttpResponse(req.session['username'])

def getlocalvncmethod(req):
	username=req.session['username']
	passwd=req.session['password']
	if not os.path.isdir("/home/%s/.vnc"%username):
		warn="Not found .vnc folder,Please init vnc env"
		return HttpResponse(warn)
	else:
		vncfile=os.listdir("/home/%s/.vnc/"%username)
		result=[]
		cl=[]
		for v in vncfile:
			if "pid" in v:
				print "OK"+v 
				pid=getvncpid("/home/%s/.vnc/%s"%(username,v))[0].strip()
				server=v.split(":")[0]
				cmd="ps -eo pid,cmd | grep %s| grep -v grep"%pid
				cl.append((username,passwd,server,cmd,v))
			else:
				print "false"+v

		if cl:
			pool=Pool(processes=cl.__len__())	
			#pool=Pool()	
			for c in cl:
				result.append(pool.apply_async(runcmdmulit,c))
		else:
			return 	False
		pool.close()
		pool.join()
		while not q.empty():
			(hn,so,filename)=q.get()
			if ".vnc/passwd" in so:
				port=re.search(":(\d\d|\d)",so).group()
				geo=re.search(" \d+x\d+ ",so).group().strip()
				depth=re.findall("-depth \d+",so)
				if depth:
					depth=depth[0].split()[1]
				else:
					depth=24
				server=hn
				try:
					ip=socket.gethostbyname(server)
				except:
					ip=""
				if vncserver.objects.filter(servername=server,port=port):
					#return HttpResponse("None")	
					pass
				else:	
					vncs=vncserver(servername=server,ip=ip,geometry=geo,depth=depth,port=port,username=username)
					vncs.save()
			else:
				badport=filename.split(".")[1]
				if vncserver.objects.filter(servername=hn,port=badport):
					vncserver.objects.filter(servername=hn,port=badport).delete()
				if not os.path.isdir("/home/%s/.vnc/remove"%username):
					os.mkdir("/home/%s/.vnc/remove"%username)
					os.chmod("/home/%s/.vnc/remove"%username,stat.S_IRWXO+stat.S_IRWXU+stat.S_IRWXG)
					
				os.rename("/home/%s/.vnc/%s"%(username,filename),"/home/%s/.vnc/remove/%s"%(username,filename))
		return True
def getlocalvnc(req):
	if req.method=="GET":
		if req.session["searchlocalvnc"]:
			data=getlocalvncmethod(req)
			if data:
				req.session["searchlocalvnc"]=0
			else:
				return 0
		#vncserverinfo=serializers.serialize("json",vncserver.objects.filter(username=req.session["username"]))
		return HttpResponse("success")
		#return HttpResponse(vncserverinfo)
		

def runcmdmulit(username,passwd,hn,cmd,filename):
	if cmd:
		s=paramiko.SSHClient()
		s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		user=username
		passw=passwd
		try:
			s.connect(str(hn),22,str(user),str(passw))
			si,so,se=s.exec_command(cmd)
			output=so.read()
			s.close()
			res=(str(hn),output,filename)
			q.put(res)
			return res
		except Exception as e:
			res=(str(hn),str(e),filename)
			q.put(res)
			return res
	else:
		return 0

def help(req):
	return render(req,"help.htm")

def comment(req):
	if req.method=="POST":
		if req.POST["ctext"]:
			updateserver=vncserver.objects.filter(servername=req.POST["server"],port=req.POST["port"])[0]
			updateserver.comments=req.POST["ctext"]
			updateserver.save()
	return HttpResponse("OK")
			
