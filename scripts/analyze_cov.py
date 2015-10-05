import codecs
import os
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import random


#prog = "xpdf_3.02-2"
#prog  = "gif2png"
#prog = "mp3gain"
#prog = "mp3blaster"
#prog = "jpegtran"
prog = "eog"

cov_folder = "C:/Users/rvlfl_000/Documents/Projects/Fuzzing/UbuFuzz_2013_32_" + prog + "_folder/pincoverage/results/"

bbl_dist_fig_path = "bbl_dist.pdf"

covs = []

seed_num = 80

# In each iteration, we randomly select this number of files, 
# and select the one that contributes most new bbls to the seeds. 
# Increasing this number will improve the results, at the cost of 
# more execution time.
cand_size = 100



# We go through the folder and get the path of all files
for root, subFolders, files in os.walk(cov_folder):
    for f in files:
        covs.append(os.path.join(root,f))

print("There are " + str(len(covs)) + " coverage files.")

addr_count = {}
addr_count_total = {}
addr_set  = {}

i = 0

for cov_file in covs:
    #print(cov_file)    
    
    addr_count[cov_file] = {}
    addr_set[cov_file] = set()
    
    for line in open(cov_file):
        
        if(line.strip() == ""):
            continue              
        
        #print(cov_file)
        
        try:
            addr = int(line.split(": ")[0].strip())
            count = int(line.split(": ")[1].strip())
        except:
            
            #print(cov_file)
            continue
        
        # Should have no duplicate
        #assert addr not in addr_count[cov_file]
        
        #addr_count[cov_file][addr] = count
        
        addr_set[cov_file].add(addr)
        
        if addr not in addr_count_total:
            addr_count_total[addr] = 0
        addr_count_total[addr] += 1
        
    i += 1
    if i % 100 == 0:
        print(i)
        
    #print(len(addr_count[cov_file]))

print("There are " + str(len(addr_count_total)) + " bbls.")

bbl_sorted = []
bbl_count_sorted = []

for pair in sorted(addr_count_total.items(), key=itemgetter(1), reverse=True):
    bbl_sorted.append(pair[0])
    bbl_count_sorted.append(pair[1])


# Dedup



#################################################################
# We draw the distribution of bbls
#################################################################

fontSize = 18
figWidth = 7
figHeight = 5

fig = plt.figure()

ax = fig.add_subplot(111)

ax.set_xlabel('bbls (ranked)', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)

isLogLog = False

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')

plt.plot(np.arange(len(bbl_count_sorted)), bbl_count_sorted)

fig.tight_layout()

fig.savefig(bbl_dist_fig_path) 
##############################################################



#assert False

# A greedy algoritm to choose a large coverage seed set

def get_new_element_size(seed_set, cand_set):
    union_set = seed_set | cand_set
    return len(union_set)  

def get_rand_items(cand_size, popu):
    assert len(popu) > cand_size
    result = set()
    while(len(result) < cand_size):
        choice = random.choice(popu)
        if choice not in result:
            result.add(choice)
    return result
        

seed_addr = set()

seed_list = codecs.open(prog + "seeds.txt", "w", 'utf-8')


for i in range(0, seed_num):
    max_union_num = 0
    max_file = ""
    j = 0
    
    # Using the whole set is too expensive in many cases,
    # so here we randomly sample a subset as the candidates.
    cands = get_rand_items(cand_size, covs)    
    
    for cov_file in cands:
        union_num = get_new_element_size(seed_addr, addr_set[cov_file])       
        if union_num > max_union_num:
            max_union_num = union_num
            max_file = cov_file
        j += 1
        
    for addr in addr_set[max_file]:
        if addr not in seed_addr:
            seed_addr.add(addr)
    
    fileName = max_file[max_file.rfind('\\') + 1:-4]
    fileName = fileName[:max_file.rfind('_')] + "." + fileName[max_file.rfind('_') + 1:]

    seed_list.write(fileName + "\n")
    
seed_list.close()

print("# bbl in the final seed:" + str(len(seed_addr)))
print("% bbl covered:" + str(len(seed_addr) / len(addr_count_total)))
