from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

matrix = [  
  [0, 1, 1, 1],
  [0, 1, 0, 0],
  [1, 1, 0, 0],
  [0, 1, 0, 0]
]
grid = Grid(matrix=matrix)

start = (3, 0)
end = (0, 2)

#Given 2 sets of coordinates, returns path
def findpath(s,e):
    x1=s[0]
    y1=s[1]
    x2=e[0]
    y2=e[1]
    start = grid.node(x1,y1)
    end = grid.node(x2, y2)
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)
    print(path)
    return path

path=findpath(start,end)
print('path length:', len(path))
print(grid.grid_str(path=path, start=start, end=end))

#Converts nodes to commands for different Orientations
def Ncommand(list):
    command=[]
    for i in range(len(list)-1):
        a=list[i+1]
        b=list[i]
        c=(a[0]-b[0],a[1]-b[1])
        if c==(1,0):
            command.append("R")
        elif c==(-1,0):
            command.append("L")
        else:
            command.append("S")
    return command

def Scommand(list):
    command=[]
    for i in range(len(list)-1):
        a=list[i+1]
        b=list[i]
        c=(a[0]-b[0],a[1]-b[1])
        if c==(1,0):
            command.append("L")
        elif c==(-1,0):
            command.append("R")
        else:
            command.append("S")
    return(command)

def Wcommand(list):
    command=[]
    for i in range(len(list)-1):
        a=list[i+1]
        b=list[i]
        c=(a[0]-b[0],a[1]-b[1])
        if c==(0,1):
            command.append("L")
        elif c==(0,-1):
            command.append("R")
        else:
            command.append("S")
    return command

def Ecommand(list):
    command=[]
    for i in range(len(list)-1):
        a=list[i+1]
        b=list[i]
        c=(a[0]-b[0],a[1]-b[1])
        if c==(0,1):
            command.append("R")
        elif c==(0,-1):
            command.append("L")
        else:
            command.append("S")
    return command

#Returns new path after accounting for Orientation
def Ncommand_path(list1,list2,state):
    cmd=list1
    new_path=list2
    for i in range(len(cmd)):
        new_path.append(cmd[i])
        if cmd[i]=="L":
            print("delay 500 sec")
            state="W"
            temp=Wcommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
        elif cmd[i]=="R":
            print("delay 500 sec")
            state="E"
            temp=Ecommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            decide(cmd,state)
            continue
    return (new_path,state)

def Scommand_path(list1,list2,state):
    cmd=list1
    new_path=list2
    for i in range(len(cmd)):
        new_path.append(cmd[i])
        if cmd[i]=="L":
            print("delay 500 sec")
            state="E"
            temp=Ecommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
        elif cmd[i]=="R":
            print("delay 500 sec")
            state="W"
            temp=Wcommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
    return (new_path,state)

def Wcommand_path(list1,list2,state):
    cmd=list1
    new_path=list2
    for i in range(len(cmd)):
        new_path.append(cmd[i])
        if cmd[i]=="L":
            print("delay 500 sec")
            state="S"
            temp=Scommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
        elif cmd[i]=="R":
            print("delay 200 sec")
            state="N"
            temp=Ncommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
    return new_path,state

def Ecommand_path(list1,list2,state):
    cmd=list1
    new_path=list2
    for i in range(len(cmd)):
        new_path.append(cmd[i])
        if cmd[i]=="L":
            print("delay 500 sec")
            state="N"
            temp=Ncommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
        elif cmd[i]=="R":
            print("delay 200 sec")
            state="S"
            temp=Scommand(path)
            for x in range(i+1,len(cmd)):
                cmd[x]=temp[x]
            continue
    return new_path,state

def decide(list3,state):
    cmd=list3
    new_cmd=[]
    if state=="N":
        new_cmd,state = Ncommand_path(cmd,new_cmd,state)
        print(new_cmd)
        print(state)
    elif state=="S":
        new_cmd,state = Scommand_path(cmd,new_cmd,state)
        print(new_cmd)
        print(state)    
    elif state=="W":
        new_cmd,state = Wcommand_path(cmd,new_cmd,state)
        print(new_cmd)
        print(state)    
    elif state=="E":
        new_cmd,state = Ecommand_path(cmd,new_cmd,state)
        print(new_cmd)
        print(state)
    return(new_cmd,state)


def nodecheck(path,s,e):
    if s==(1,3):
        state="N"
        cmd=Ncommand(path)
        new_cmd,state = decide(cmd,state)
    elif start==(3,0):
        cmd=Wcommand(path)
        state="W"
        new_cmd,state = decide(cmd,state)
    elif start==(0,2):
        cmd=Ecommand(path)
        state="E"
        new_cmd,state = decide(cmd,state)

    print(new_cmd)

nodecheck(path,start,end)
