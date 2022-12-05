from Common import *
import Reader

class OCCTransaction(Transaction):

    def __init__(self, transaction):
        super().__init__(transaction.id)
        self.writeSet = []
        self.readSet = []
        self.startTs = float('inf')
        self.finishTs = float('inf')

    def write(self, i, data):
        if (self.startTs == float('inf')):
            self.startTs = i
        if (data not in self.writeSet):
            self.writeSet.append(data)
        return True

    def read(self, i, data):
        if (self.startTs == float('inf')):
            self.startTs = i
        if (data not in self.readSet):
            self.readSet.append(data)
        return True
    
    def commit(self, i, arrTransaction):
        success = True
        for i in range(self.id-1):
            T = arrTransaction[i]
            if (T.id == self.id):
                continue
            if (not (T.finishTs < self.startTs)):
                success = False
            if ((not success) and set(T.writeSet).isdisjoint(self.readSet)):
                success = True
            
            if (not success):
                break
        
        self.finishTs = i

        return success

    def is_running(self):
        return (self.startTs != float('inf')) and (self.finishTs == float('inf'))
    
    def printInfo(self):
        running = '"running"' if self.is_running() else '"not running"'
        print(f"T{self.id} = ({running}, [", end="")
        for i, x in enumerate(self.readSet):
            if (i == len(self.readSet)-1):
                print(x, end="")
            else:
                print(x, end=",")
        print("], ", end="")
        print(f"[", end="")
        for i, x in enumerate(self.writeSet):
            if (i == len(self.writeSet)-1):
                print(x, end="")
            else:
                print(x, end=",")
        print("])")
            

class OCCProcess(Process):

    def __init__(self, process):
        super().__init__(process = process)
    
    def execute(self, i, arrTransaction):
        success = True
        if (self.action == 'R'):
            success = self.transaction.read(i, self.data)
        elif (self.action == 'W'):
            success = self.transaction.write(i, self.data)
        else:
            success = self.transaction.commit(i, arrTransaction)

        if (not(success)):
            print(f'Abort T{self.transaction.id}')
        
        return success


def execute_OCC(fileName):
    arrTransaction, arrProcess, raw_data = Reader.generalSetup(fileName)
    arrTransaction, arrProcess = Reader.OCC_Converter(arrTransaction, arrProcess, raw_data)
    txn_request = []

    for i, p in enumerate(arrProcess, start=1):
        if (p.transaction in txn_request):
            print(f'{p}: {p.transaction} is aborted\n')
        else:
            print(p)
            print("Transaksi dengan timestamp lebih kecil:\n[ ", end="")
            for i in range(p.transaction.id-1):
                print(arrTransaction[i], end=" ")
            print("]")

            success = p.execute(i, arrTransaction)
            for T in arrTransaction:
                T.printInfo()

            if (not success):
                txn_request.append(p.transaction)

            input()
