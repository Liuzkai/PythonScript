import sys
import os
from HART import HART
from HART_Auto import HART_Auto
from HART_Auto.ttypes import *
from thrift.transport import TTransport, TSocket
from thrift.protocol.TBinaryProtocol import TBinaryProtocol


# Make socket
transport = TSocket.TSocket('localhost', 9090)

# Buffering is critical. Raw sockets are very slow
transport = TTransport.TBufferedTransport(transport)

# Wrap in a protocol
protocol = TBinaryProtocol(transport)

# Create a client to use the protocol encoder
client = HART.Client(protocol)

# Connect!
transport.open()


# Initialize Client
cook_options = CookOptions()
client.Initialize(cook_options, True, -1, "C:/Users/zhongkailiu.TENCENT/Documents/houdini18.5/houdini.env", "", "", "",
                  "")

# Load HIP
client.LoadHIPFile("D:/Hou/Test/Thrift.hip", True)
# Create HDA
node_ids = client.recv_GetHIPFileNodeIds()




client.Cleanup()



# Close!
transport.close()

