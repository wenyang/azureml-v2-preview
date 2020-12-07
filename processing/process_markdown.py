import argparse, glob, os

def readlines(filename):
   with open(filename, encoding='utf-8') as fh:
      lines = fh.readlines()
   if not lines[-1].endswith('\r') and not lines[-1].endswith('\n'):
      lines[-1] = lines[-1]+'\n'
   return lines

def process(filename):
   lines = readlines(filename)
   errors = []
   path = os.path.dirname(filename)
   with open(filename, encoding='utf-8', mode='w') as fh:
      i = 0
      while i < len(lines)-2: # pattern requires 3 lines
         if lines[i].lstrip().startswith('```yml') and lines[i+1].lstrip().startswith('#source '):
            indent = lines[i+1].index('#source ')
            fh.writelines([lines[i]])
            i = i + 1
            fh.writelines([lines[i]])
            include_file = os.path.join(path, lines[i][(indent + len('#source ')):].strip())
            print("processing include of " + include_file)
            try:
               def line_with_indent(line):
                  return '{}{}'.format((indent * ' ') if len(line.strip()) else '', line)
               fh.writelines(line_with_indent(line) for line in readlines(include_file))
            except Exception as ex:
               fh.writelines([str(ex)+'\n'])
               errors.append(ex)

            while i < len(lines)-2 and not lines[i].strip() == '```':
               # skip forward to end of include
               i = i + 1
         else:
            fh.writelines([lines[i]])
            i = i + 1
      fh.writelines(lines[-2:])

      if len(errors) > 0:
         raise errors[0]
   return

parser = argparse.ArgumentParser()
parser.add_argument("--md_glob", help="the md files", action='append', required=False)
args = parser.parse_args()

files = []
for one_glob in args.md_glob:
   for filename in glob.iglob(one_glob, recursive=True):
      files.append(filename)

for file in files:
   print('processing file:', file)
   process(file)

