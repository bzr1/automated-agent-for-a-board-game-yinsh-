import pickle
import sys
sys.path.append('agents/')
result_dic = dict()

def Calh(player_id, composition):
    if composition.count("0") ==5:       # if there are 5 “0” (empty) in the string, then h=5 as the true value could be 6. 
        return 5
    if player_id == 0:
        if composition.count("3") >0:  #If the opponent ring exists, we consider h to be big, as it is hard to remove opponent's ring. 
            return 51
        if composition.count("2") ==5:    #if 5 “2” (teal counter) in a roll, then h = 0.
            return 0
        if composition.count("4") == 0:         #If there is no opponents counter, then we use empty space + teal’s ring as the h value
            return composition.count("0") + composition.count("1")

        #For other mixed situations, we first treated consecutive same game piece as one to reduce the complexity. 
        
        distinctcomp=composition[0]
        for i in range(1,5):
            if(composition[i] == composition[i-1] and (composition[i]=="2" or composition[i]=="4")):
                pass
            else:
                distinctcomp+=composition[i]
        
        h=0
        for i in range(len(distinctcomp)):
            if(distinctcomp[i]=="2"):
                pass
            
            elif(distinctcomp[i]=="0" or distinctcomp[i]=="1"):     #Also, for every empty and teal ring, we add 1 to the heuristic as well
                h+=1
            
            elif(distinctcomp[i]=="4" and (distinctcomp[i-1]!="1" or distinctcomp[i-1]!="0")):  ##then if there is opponents counter exists and if either the opponent’s counter is at the first place of the string or it doesn't have empty or teal’s ring next to it, then we add 1 to the heuristic.
                if(i == 0  or distinctcomp[i-1]=="2"):
                    h+=1
                    
            
                   
        return h
    # And vice versa for the magenta agent.
    if player_id == 1:
        if composition.count("4") ==5:
            return 0
        if composition.count("1") >0:
            return 51
        if composition.count("2") == 0:
            return composition.count("0") + composition.count("3")
        distinctcomp=composition[0]
        for i in range(1,5):
            if(composition[i] == composition[i-1] and (composition[i]=="2" or composition[i]=="4")):
                pass
            else:
                distinctcomp+=composition[i]
        h=0
        
        for i in range(len(distinctcomp)):
            if(distinctcomp[i]=="4"):
              pass
            elif(distinctcomp[i]=="0" or distinctcomp[i]=="3"):
                h+=1
            
            elif(distinctcomp[i]=="4" and (distinctcomp[i-1]!="3" or distinctcomp[i-1]!="0")):
                if(i == 0  or distinctcomp[i-1]=="4"):
                    h+=1
                    
                   
        return h
    
#calculate h value for all cases
for c1 in range(5):
    for c2 in range(5):
        for c3 in range(5):
            for c4 in range(5):
                for c5 in range(5):
                    clist = (c1,c2,c3,c4,c5)
                    composition =""
                    for i in clist:
                        composition+=str(i)
                    result_dic["0"+composition]=Calh(0,composition)
                    result_dic["1"+composition]=Calh(1,composition)

a_file = open("Ah.pkl", "wb")
pickle.dump(result_dic, a_file)
a_file.close()

# a_file = open("Ah.pkl", "rb")
# output = pickle.load(a_file)
# print(output)
# OUTPUT
# {'a': 1, 'b': 2}
# a_file.close()