import sys
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

filepath = str(sys.argv[1])

labels = open(filepath).readlines()
labels = [l.strip() for l in labels]
labels = [l.split(",") for l in labels]

if "-afterSC" in sys.argv :
  classes = Counter([l[1] for l in labels])
  
  classes["not informative / \n not involved"] = classes.pop('0')
  classes["informative"] = classes.pop('1')
  classes["involved"] = classes.pop('2')

else :
  pairs = Counter(["%s%s" % (l[1],l[2]) for l in labels])
  info = Counter(["%s" % l[1] for l in labels])
  invo = Counter(["%s" % l[2] for l in labels])

  # change the keys
  pairs["informative / \n not involved"] = pairs.pop("10")
  pairs["informative / \n involved"] = pairs.pop("11")
  pairs["not informative / \n not involved"] = pairs.pop("00")
  pairs["not informative / \n involved"] = pairs.pop("01")

  info["informative"] = info.pop("1")
  info["not informative"] = info.pop("0")

  invo["involved"] = invo.pop("1")
  invo["not involved"] = invo.pop("0")

  print(pairs)
  print(info)
  print(invo)

colors = ["lightcoral","steelblue","darkseagreen","wheat"]

def plotpie(data,output) :
	plt.clf()
	plt.figure(figsize=[7,7])
	plt.pie([float(v) for v in data.values()], labels=[str(k) for k in data.keys()], autopct='%.2f', colors = colors)
	plt.savefig(output,dpi = 200)

if "-afterSC" in sys.argv :
  plotpie(classes,"pie_classesAfterSC.png")
else :
  plotpie(pairs,"pie_pairs.png")
  plotpie(info,"pie_info.png")
  plotpie(invo,"pie_invo.png")
