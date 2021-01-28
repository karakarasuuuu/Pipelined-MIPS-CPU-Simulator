# Pipelined MIPS CPU Simulator

This is my final project during the computer organization class.  
It supports five instructions, including `add`, `sub`, `beq`, `lw`, and `sw`.  

Note that It is not 100% completed. Here is the to-do list:
- Reordering codes
- Fixing bugs
- Sorting files

## Detail

### `stall.py`

Once a hazard takes place, all the program does is stall, causing a bubble to wait.  

### `forward.py`

Similar to `stall.py` but forwarding is used when available.  

### `example.txt` and `forward.txt`

Examples to execute this program.  
`example.txt` is for stall, and `forward.txt` is for forwarding.  

### `memory.txt`

The input of the program.  
The result will be written into a file called `result.txt`.  
