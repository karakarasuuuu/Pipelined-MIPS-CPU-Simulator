
if __name__ == '__main__':

    # read instructions
    inst = list()
    with open('memory.txt', 'r') as f:
        for line in f:
            inst.append(line.split())

    f = open('result.txt', 'w')

    # variables
    reg = [1 if i != 0 else 0 for i in range(32)]
    mem = [1 for _ in range(32)]
    dreg = {}
    dmem = {}
    IF = ''
    ID = ''
    EX = ''
    MEM = ''
    WB = ''
    cycle = 0
    stall = False
    EXCtrl = ''
    MEMCtrl = ''
    WBCtrl = ''
    current = 0

    # process
    while True:
    
        stall = False

        # instructions after ID will not be affected
        WB = MEM
        MEM = EX
        EX = ''

        # check if stall is needed
        if ID:
            if ID[0] == 'add' or ID[0] == 'sub': 
                rd = ID[1].strip(',')
                rs = ID[2].strip(',')
                rt = ID[3].strip(',')

                # data hazard
                # if WB and WB[0] != 'beq' and WB[0] != 'sw':
                #     if rs == WB[1].strip(',') or rt == WB[1].strip(','):
                #         stall = True

                # if MEM and MEM[0] != 'beq' and MEM[0] != 'sw':
                #     if rs == MEM[1].strip(',') or rt == MEM[1].strip(','):
                #         stall = True

                if EX and EX[0] == 'lw':
                    if rs == EX[1].strip(',') or rt == EX[1].strip(','):
                        stall = True

            elif ID[0] == 'sw':
                rs = ID[1].strip(',')

                # data hazard
                # if WB and WB[0] != 'beq' and WB[0] != 'sw':
                #     if rs == WB[1].strip(','):
                #         stall = True

                # if MEM and MEM[0] != 'beq' and MEM[0] != 'sw':
                #     if rs == MEM[1].strip(','):
                #         stall = True

                if EX and EX[0] == 'lw':
                    if rs == EX[1].strip(','):
                        stall = True

            elif ID[0] == 'beq':
                rs = ID[1].strip(',')
                rt = ID[2].strip(',')

                # if the value is different from the initial stage, we store it
                for i in range(1, len(reg)): # since $0 is always zero
                    if reg[i] != 1:
                        dreg[i] = reg[i]

                for i in range(len(mem)):
                    if mem[i] != 1:
                        dmem[i] = mem[i]

                # data hazard
                # if WB and WB[0] != 'beq' and WB[0] != 'sw':
                #     if rs == WB[1].strip(',') or rt == WB[1].strip(','):
                #         stall = True

                # if MEM and MEM[0] != 'beq' and MEM[0] != 'sw':
                #     if rs == MEM[1].strip(',') or rt == MEM[1].strip(','):
                #         stall = True
                
                if EX and EX[0] == 'lw':
                    if rs == EX[1].strip(',') or rt == EX[1].strip(','):
                        stall = True

        # no stalls then move on
        if not stall:
            EX = ID
            ID = IF
            IF = inst[current] if len(inst) > current else ''
            current += 1

        # registers and memory process if no stall
        if EX:
            # store words from register to memory
            if EX[0] == 'sw':
                rs = int(EX[1].strip('$, '))
                
                offset = int(EX[2][:EX[2].find('(')]) // 4 # 24($0) -> [0, 2)
                base = int(EX[2][EX[2].find('$') + 1:EX[2].find(')')]) # 24($0) -> [3, 5)

                mem[base + offset] = reg[rs]
            # load words from memory to register
            elif EX[0] == 'lw':
                rs = int(EX[1].strip('$, '))
                
                offset = int(EX[2][:EX[2].find('(')]) // 4 # 24($0) -> [0, 2)
                base = int(EX[2][EX[2].find('$') + 1:EX[2].find(')')]) # 24($0) -> [3, 5)

                reg[rs] = mem[base + offset]
            # addition
            elif EX[0] == 'add':
                rd = int(EX[1].strip('$, '))
                rs = int(EX[2].strip('$, '))
                rt = int(EX[3].strip('$, '))

                reg[rd] = reg[rs] + reg[rt]
            # subtraction
            elif EX[0] == 'sub':
                rd = int(EX[1].strip('$, '))
                rs = int(EX[2].strip('$, '))
                rt = int(EX[3].strip('$, '))

                reg[rd] = reg[rs] - reg[rt]
            # condition
            elif EX[0] == 'beq':
                rs = int(EX[1].strip('$, '))
                rt = int(EX[2].strip('$ ,'))
                target = int(EX[3].strip('$, '))

                if reg[rs] == reg[rt]:
                    ID = ''
                    current = inst.index(EX) + target + 1
                    IF = inst[current] if len(inst) > current else ''
                    current += 1
                    # if taken, we have to restore the values when beq is fetched
                    for i in range(1, len(reg)): # since $0 is always zero
                        if i in dreg.keys(): reg[i] = dreg[i]
                        elif reg[i] != 1: reg[i] = 1
                    dreg.clear()

                    for i in range(len(mem)):
                        if i in dmem.keys(): mem[i] = dmem[i]
                        elif mem[i] != 1: mem[i] = 1
                    dmem.clear()
                    
        # control signals
        if EX:
            if EX[0] == 'lw': EXCtrl = '01 010 11'
            elif EX[0] == 'sw': EXCtrl = 'X1 001 0X'
            elif EX[0] == 'add' or EX[0] == 'sub': EXCtrl = '10 000 10'
            elif EX[0] == 'beq': EXCtrl = 'X0 100 0X'

        if MEM:
            if MEM[0] == 'lw': MEMCtrl = '010 11'
            elif MEM[0] == 'sw': MEMCtrl = '001 0X'
            elif MEM[0] == 'add' or MEM[0] == 'sub': MEMCtrl = '000 10'
            elif MEM[0] == 'beq': MEMCtrl = '100 0X'

        if WB:
            if WB[0] == 'lw': WBCtrl = '11'
            elif WB[0] == 'sw': WBCtrl = '0X'
            elif WB[0] == 'add' or WB[0] == 'sub': WBCtrl = '10'
            elif WB[0] == 'beq': WBCtrl = '0X'

        # done
        if not IF and not ID and not EX and not MEM and not WB: 
            f.write('\n')
            f.write(f'需要花{cycle}個cycles')
            f.write('\n')

            f.write('\n')

            # Since the example in the slide is too ugly, I chose to use a better form.
            for i in range(len(reg)):
                f.write(f'${i} {reg[i]}\n')

            f.write('\n')    
            
            for i in range(len(mem)):
                f.write(f'W{i} {mem[i]}\n')

            break
        
        # print results
        cycle += 1
        f.write(f"Cycle {cycle}\n")

        if WB: f.write(f'   {WB[0]}: WB {WBCtrl}\n')
        if MEM: f.write(f'   {MEM[0]}: MEM {MEMCtrl}\n')
        if EX: f.write(f'   {EX[0]}: EX {EXCtrl}\n')
        if ID: f.write(f'   {ID[0]}: ID\n')
        if IF: f.write(f'   {IF[0]}: IF\n')

    f.close()
