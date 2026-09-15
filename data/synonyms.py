"""Definitions extracted verbatim from the frozen synonym scorer."""
W={0:"zero",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety"}

C={0:"零",1:"一",2:"二",3:"三",4:"四",5:"五",6:"六",7:"七",8:"八",9:"九",10:"十"}

OPS={"multiplication":["*","×","x","multiplication","multiply","multiplying","times","product","乘","乘法","乘以"],
     "addition":["+","addition","add","adding","plus","sum","加","加法","加上"],
     "subtraction":["-","−","–","subtraction","subtract","subtracting","minus","difference","减","减法","减去"],
     "division":["/","÷","division","divide","dividing","divided","quotient","除","除法","除以"]}

def forms(n):
    d={"digit":{str(n)}}
    if n in W: d["word"]={W[n]}
    elif n<100: t,o=divmod(n,10); d["word"]={W[t*10]+"-"+W[o],W[t*10]+W[o]}
    if n<=10: d["cjk"]={C[n]}
    elif n<20: d["cjk"]={"十"+C[n%10]}
    elif n<100: t,o=divmod(n,10); d["cjk"]={C[t]+"十"+(C[o] if o else "")}
    return d

def syn(key, cjk=True):
    if key.lstrip("-").isdigit():
        f=forms(int(key)); s=set(f["digit"])|set(f.get("word",()))|(set(f.get("cjk",())) if cjk else set())
    else: s=set(OPS.get(key,[key]))
    return {x.lower() for x in s}
