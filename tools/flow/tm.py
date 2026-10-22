import math
a=6378137.0;f=1/298.257222101;k0=0.9996;lat0=math.radians(38);lon0=math.radians(127.5);FE=1000000;FN=2000000
e2=f*(2-f);ep2=e2/(1-e2)
def M(phi):
    return a*((1-e2/4-3*e2**2/64-5*e2**3/256)*phi-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*phi)+(15*e2**2/256+45*e2**3/1024)*math.sin(4*phi)-(35*e2**3/3072)*math.sin(6*phi))
def fwd(lat,lon):
    phi=math.radians(lat);lam=math.radians(lon)
    N=a/math.sqrt(1-e2*math.sin(phi)**2);T=math.tan(phi)**2;C=ep2*math.cos(phi)**2;A=(lam-lon0)*math.cos(phi)
    x=FE+k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T**2+72*C-58*ep2)*A**5/120)
    y=FN+k0*(M(phi)-M(lat0)+N*math.tan(phi)*(A**2/2+(5-T+9*C+4*C**2)*A**4/24+(61-58*T+T**2+600*C-330*ep2)*A**6/720))
    return x,y
def inv(x,y):
    M0=M(lat0);Mm=M0+(y-FN)/k0
    mu=Mm/(a*(1-e2/4-3*e2**2/64-5*e2**3/256))
    e1=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    phi1=mu+(3*e1/2-27*e1**3/32)*math.sin(2*mu)+(21*e1**2/16-55*e1**4/32)*math.sin(4*mu)+(151*e1**3/96)*math.sin(6*mu)+(1097*e1**4/512)*math.sin(8*mu)
    N1=a/math.sqrt(1-e2*math.sin(phi1)**2);T1=math.tan(phi1)**2;C1=ep2*math.cos(phi1)**2;R1=a*(1-e2)/(1-e2*math.sin(phi1)**2)**1.5;D=(x-FE)/(N1*k0)
    phi=phi1-(N1*math.tan(phi1)/R1)*(D**2/2-(5+3*T1+10*C1-4*C1**2-9*ep2)*D**4/24+(61+90*T1+298*C1+45*T1**2-252*ep2-3*C1**2)*D**6/720)
    lam=lon0+(D-(1+2*T1+C1)*D**3/6+(5-2*C1+28*T1-3*C1**2+8*ep2+24*T1**2)*D**5/120)/math.cos(phi1)
    return math.degrees(phi),math.degrees(lam)
def cellid(x,y):
    sx=int(x//250*250);sy=int(y//250*250)
    return '다사'+str(sx)[1:5]+str(sy)[2:6],sx,sy
if __name__=='__main__':
    x,y=fwd(37.5663,126.9779);print(x,y,cellid(x,y));print(inv(x,y))
