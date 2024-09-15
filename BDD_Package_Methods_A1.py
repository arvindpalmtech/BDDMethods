# Author - Arvind Kumar
# Address - Wagatsuma Laboratory, Kyushu Institute of Technology
 
import graphviz
import sys
import numpy as np

g = graphviz.Digraph('G', filename='plot.gv')

totlevel = 1
markvaluecount=0
value_set ={0,1,'X'}
count=0
res1 = []
Node_in_Reduced_BDD =[]

class Node:
    __one  = None  # singleton object for terminal node True
    __zero = None  # singleton object for terminal node False

    __nextid = 1

    def __init__(self, index, low, high, value,mark=False):
        self._index = index
        self._low   = low
        self._high  = high
        self._value = value
        self._id    = Node.__nextid
        self.mark = mark       #To mark vertex is visited while traversing
        Node.__nextid += 1



    @classmethod
    def createVariable(cls,index,low,high,value,mark=False):
        return Node(index, low, high, value,mark)

    
    def createEdges(self):

        if self._low != None and self._high != None:
            if self.mark == False:
                g.edge(str(self._id),str(self._low._id),'0')
                g.edge(str(self._id),str(self._high._id),'1')
                self.mark = True
                self._low.createEdges()
                self._high.createEdges()
        elif self._low == None and self._high != None:
            if self.mark == False:
                g.edge(str(self._id),str(self._high._id),'1')
                self.mark = True
                self._high.createEdges()
        elif self._low != None and self._high == None:
            if self.mark == False:
                g.edge(str(self._id),str(self._low._id),'0')
                self.mark = True
                self._low.createEdges()    


    def createNodes(self):
        if(self._index == -1):
            g.attr('node', shape='box', style='',color='')
            g.node(str(self._id),label=str(self._value))
        else:
            g.attr('node', shape='ellipse', style='',color='')
            g.node(str(self._id),label=str('x'+str(self._index)))
            self._low.createNodes()
            self._high.createNodes()



    def traverse(self):
        global markvaluecount
        #print("Index={} and Value={}".format(self._index,self._value))
        self.mark = not self.mark
        if self._index != -1:
            if  self.mark != self._low.mark:
                self._low.traverse()
            if self.mark != self._high.mark:
                self._high.traverse()
        markvaluecount = markvaluecount + 1

    def traverseNodeInTree(self):
        #print("Index={} and Value={}".format(self._index,self._value))
        self.mark = not self.mark
        Node_in_Reduced_BDD.append(self)
        if self._index != -1:
            if  self.mark != self._low.mark:
                self._low.traverse()
            if self.mark != self._high.mark:
                self._high.traverse()

    def makeListOfNodes(self,nodelist):
        global markvaluecount
        nodelist.append(self)
        self.mark = not self.mark
        if self._index != -1:
            if  self._low != None and self.mark != self._low.mark:
                self._low.makeListOfNodes(nodelist)
            if self._high != None and  self.mark != self._high.mark:
                self._high.makeListOfNodes(nodelist)
        markvaluecount = markvaluecount + 1

        return nodelist

        


    def reduce(self):
        subgraph={}
        vlist ={}
        nodelist =[]
        nodelist = self.makeListOfNodes(nodelist)
        for vertex in nodelist:
            index = vertex._index
            vlist[index] = vlist.get(index, [])
            vlist[index].append(vertex)
        nextid = 0
        index_vlist = [-1] + sorted(list(vlist), reverse=True)[:-1]
        for i in index_vlist:
            Q = []
            for u in vlist[i]:
                if u._index == -1:
                    Q.append((u._value,u))
                elif u._low._id == u._high._id:
                    u._id = u._low._id
                else:
                    Q.append(((u._low._id,u._high._id),u))
            Q = sorted(Q, key=lambda x: x[0])
            #print(Q)
            oldkey = (-1,-1)
            for key,u in Q:
                if key == oldkey:
                    u._id = nextid
                else:
                    nextid = nextid + 1
                    u._id = nextid
                    subgraph[nextid] = u
                    if u._low != None: 
                        u._low = subgraph[u._low._id]
                    if u._high != None:
                        u._high = subgraph[u._high._id]
                    oldkey = key
        return subgraph[nextid]


    @classmethod
    def apply(cls, v1, v2, op):
        T = {}
        return cls.__apply_step(v1, v2, op, T).reduce()

    @classmethod
    def __apply_step(cls, v1, v2, op, T):

        if v1 == None or v2 == None:
            return
        #print
        #print("v1 id ={} v2 id ={}".format(v1._id,v2._id))
        u = T.get((v1._id, v2._id))
        if u is not None:
            return u

        u = cls.createVariable(-100,None,None,-100,mark = False)
        
        T[(v1._id, v2._id)] = u
        #print("Before and, v1_value={}, v2_value={}".format(v1._value,v2._value))
        u._value = op(v1._value,v2._value)
        #print("u._value={}".format(u._value))
        if u._value != ('X' or 'Y'):
            u._index = -1
            u._low = None
            u._high = None
            #print("uindex={}".format(u._index))
        else:
            v1index = v2index = sys.maxsize
            if not v1._index == -1 :
                v1index = v1._index
            if not v2._index == -1:
                v2index = v2._index
            u._index = min(v1index,v2index)
            #print("v1index = {}, v2index ={} uindex={}".format(v1index,v2index,u._index))
            #print("Index of u should be 3={}".format(u._index))
            if v1._index == u._index:
                vlow1 = v1._low
                vhigh1 = v1._high
            else:
                vlow1 = v1
                vhigh1 = v1
            if v2._index == u._index:
                vlow2 =  v2._low
                vhigh2 = v2._high
            else:
                vlow2 = v2 
                vhigh2 =v2 

            u._low = cls.__apply_step(vlow1,vlow2,op,T)
            u._high = cls.__apply_step(vhigh1,vhigh2,op,T)
        
        return u 

    @classmethod
    def __or__(cls,item1,item2):
        if item1 == str(1) or item2 == str(1):
            return str(1)
        elif item1 == str(0) and item2 == str(0):
            return str(0)
        else:
            return 'X'

    @classmethod
    def __and__(cls,item1,item2):
        if item1 == str(0) or item2 == str(0):
            return str(0) 
        elif item1 == str(1) and item2 == str(1):
            return str(1)
        else:
            return 'X'

    @classmethod
    def neg(cls,val):
        if val == str(0):       # Notice everywhere 0,1 and X we have taken as string
            return str(1)       # Therefore accordingly we have declared a function
        elif val == str(1):
            return str(0)
        elif val == 'X':
            return val
        else:
            print("Wrong input to the neg method")

    @classmethod
    def __xor__(cls,item1,item2):
        if item1 == 'X' or item2 == 'X':
            return 'X'
        elif item1 == str(1) and item2 == str(1):
            return str(0)
        elif item1 == str(1) and item2 == str(0):
            return str(1)
        elif item1 == str(0) and item2 == str(1):
            return str(1)
        elif item1 == str(0) and item2 == str(0):
            return str(0)

    @classmethod
    def __invert__(cls,item1,zero,one):
        #print("Index={} and Value={}".format(self._index,self._value))
        #print("Inside invert")
        item1.mark = not item1.mark

        if item1 != None:
            #print("Inside Check")
            #print("item1 low index ={} low value type={}".format(item1._low._index, type(item1._low._value)))
            if item1._low._index == -1 and  item1._low._value == str(0):
                item1._low = one
                #print("updated x{} low zero to one".format(item1._index))
            if item1._low._index == -1 and item1._low._value == str(1):
                item1._low = one
                #print("updated x{} low one to zero".format(item1._index))

            if item1._high._index == -1 and item1._high._value == str(0):
                item1._high = one
                #print("updated x{} low zero to one".format(item1._index))
            if item1._high._index == -1 and item1._high._value == str(1):
                item1._high = zero
                #print("updated x{} low one to zero".format(item1._index))

        if item1._low._index != -1:
            if  item1.mark != item1._low.mark:
                cls.__invert__(item1._low,zero,one)
        if item1._high._index != -1:
            if item1.mark != item1._high.mark:
                cls.__invert__(item1._high,zero,one)
        
        return item1




    @classmethod
    def compose(cls,v1, v2, vari):
        T ={}
        if v1 != None:
            return cls.compose_Step(v1._low, v2._high, v2, vari, T).reduce()
        else:
            print("First argument is None")
            return

    @classmethod
    def compose_Step(cls, v1low, v1high, v2, vari, T):
        if v1low._index == vari:
            v1low = v1low._low
        if v1high._index == vari:
            v1high = v1high._high

        u = T.get((v1low._id, v1high._id, v2._id))
        if u is not None:
            return u
        u = cls.createVariable(-100,None,None,-100,mark = False)
        T[(v1low._id, v1high._id, v2._id)] = u
        u._value = Node.__or__(Node.__and__((Node.neg(v2._value),v1low._value)),(Node.__and__(v2._value,v1high._value)))
        
        if u._value != 'X':
            u._index = -1
            u._low = None
            u._high = None
        else:
            u._index = min(v1low._index, v1high._index, v2._index)
            if v1low._index == u._index:
                vll1 = v1low._low
                vlh1 = v1low._high
            else:
                vll1 = v1low
                vlh1 = v1low
            if v1high._index == u._index:
                vhl1 = v1high._low
                vhh1 = v1high._high
            else:
                vhl1 =v1high
                vhh1 = v1high
        if v2._index == u._index:
            v2low = v2._low
            v2high = v2._high
        else:
            v2low = v2 
            v2high = v2

        u._low = compose_Step(vll1,vhl1,v2low,vari, T)
        u._high = compose_Step(vlh1, vhh1, v2high, vari, T)
    
        return u 

    @classmethod
    def restrict(cls,v,var_index,var_value):
        # valuaton contains restricted varaible values in tuple form
        #print("In restrict")
        if v != None:
            return cls.restrictStep(v,var_index,var_value).reduce()
    
    @classmethod
    def restrictStep(cls, v, var_index, var_value):
        #print("In restrict step")
        v.mark = not v.mark
        #print("v_index= {} var_index ={}, var_value={}".format(v._index,var_index, var_value))
        if v._index == var_index:           #var_index gives the index of variable we want to restrict
            if var_value == str(0):         #var_value gives the restriction value in string form
                v._high = v._low
            elif var_value == str(1):
                v._low = v._high
        
        if v._index != -1:

            if  v._low != None and v.mark != v._low.mark:
                cls.restrictStep(v._low, var_index, var_value)
            if v._high != None and v.mark != v._high.mark:
                cls.restrictStep(v._high, var_index, var_value)
        return v

    @classmethod
    def satisfyOne(cls, v, x_array):
        if v != None and v._value == str(0):
            #Print("Failure")
            return False
        if v != None and v._value == str(1):
            #print("Success")
            return True, x_array

        if v._low != None:
            x_array.append(str(0))
            #print("x_array append ={} and v_index={}".format(x_array, v._index))
            if cls.satisfyOne(v._low, x_array):
                return True
        if v._high != None:
            x_array.append(str(1))
            return cls.satisfyOne(v._high, x_array)




    @classmethod
    def satisfyAll(cls,i,v,x_array,result):
        if v != None and v._value == str(0):
            x_array.pop()
            return
        if v!= None and v._index == -1 and v._value == str(1):  
            temp = []
            for j in x_array:
                temp.append(j)
            result.append(temp)
            return
        if v!= None and v._index != i :
            x_array.append(0)
            Node.satisfyAll(i+1, v, x_array,result)
            x_array.pop()
            x_array.append(1)
            Node.satisfyAll(i+1, v, x_array,result)
        else:
            x_array.append(0)
            Node.satisfyAll(i+1, v._low, x_array,result)
            x_array.pop()
            x_array.append(1)
            Node.satisfyAll(i+1, v._high, x_array,result)


    def plot(self):
        self.createNodes()
        if self._index != -1:
            if self.mark == True:
                self.traverse()
            self.createEdges()


                        




if __name__ == '__main__':

### YOUR CODE HERE ######