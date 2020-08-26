with open("ID_LIST.txt","r") as F:
    F = F.readlines()
F = [line[:-1] for line in F]
newF = []
for i in range(len(F)):
    if i%2 == 0:
        newF.append(F[i])
with open("ID_LIST.txt","w") as F:
    for line in newF:
        F.write(line+"\n")

