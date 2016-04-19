from django.db import models

# Create your models here.


privinfo=(
	("1",1),
	("2",2),
	("3",3),
	("4",4),
	("5",5),

)
	
enableinfo=(
	("enable","enable"),
	("disable","disable"),

)


class server(models.Model):
	servername=models.CharField(max_length=30,verbose_name="server name")
	serverip=models.CharField(max_length=30,verbose_name="IP")
	serverusername=models.CharField(max_length=30,verbose_name="username")
	serverpassword=models.CharField(max_length=30,verbose_name="password")
	privi=models.CharField(max_length=10,choices=privinfo,verbose_name="privalige",default="1")
	status=models.CharField(max_length=30,choices=enableinfo,verbose_name="enable",default="enable")
	totalnum=models.IntegerField(null=True,blank=True,default=0)
	load=models.CharField(max_length=5,null=True,blank=True,default="0")

	def __unicode__(self):
		return self.servername

class vncserver(models.Model):
	servername=models.CharField(max_length=30,verbose_name="server name")
	geometry=models.CharField(max_length=30)
	depth=models.CharField(max_length=30)
	ip=models.CharField(max_length=30)
	port=models.CharField(max_length=10)
	comments=models.CharField(max_length=20,null=True,blank=True)
	username=models.CharField(max_length=30,verbose_name="username",null=True)
	def __unicode__(self):
		return self.servername
