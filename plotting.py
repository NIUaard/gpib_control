import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import sys 

fig = plt.figure()
ax1 = fig.add_subplot(111)



dir_path = '/usr/local/home/labuser/Documents/'
rootname = 'iv_monitoring'
newdir = time.strftime("%y-%B-%d")
path = dir_path+str('/')+str(newdir)
dir_path = path

#filename  = dir_path+str('/')+str(filename)

filename = '/usr/local/home/labuser/Documents/18-September-12/iv_monitoring_D20180912T151342'

def refreshGraphData(i):
    print "refreshing data"
    graphData = open(str(filename), 'r').read()
    lines = graphData.split('\n')
    xvalues = []
    yvalues = []
    for line in lines:
        if len(line) >1:
           trlist = line.strip().split(',')
           xvalues.append(trlist[1])
           yvalues.append(trlist[2])
    print trlist[1],trlist[2]
    ax1.clear()
    ax1.plot(yvalues,xvalues,'.')

ani = animation.FuncAnimation(fig,refreshGraphData,interval = 2000)
plt.show()


