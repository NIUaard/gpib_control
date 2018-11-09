import argparse
from util import * 

parser = argparse.ArgumentParser(description='records I-V curse')

# Required positional argument
parser.add_argument('Vmin', type=float,
                    help='minimum voltage (Volt)')
parser.add_argument('Vmax', type=float,
                    help='maximum voltage (Volt)')
# Optional positional argument
parser.add_argument('--Nstep', type=int, nargs='?',default=21, 
                    help='number of voltage setpoints (default=21)')
parser.add_argument('--Nsamp', type=int, nargs='?', default=5, 
                    help='number of samples at each voltage setpoints (default=5)')
# Switch
parser.add_argument('--cycle', action='store_true',
                    help='do the cycle Vmin->Vmax->0')
parser.add_argument('--display', action='store_true',
                    help='display data during the scan')

args = parser.parse_args()

print("Argument values:")
print (args)
print(args.Vmin)
print(args.Vmax)
print(args.Nstep)
print(args.Nsamp)
print(args.cycle)

record('test.log', args)
