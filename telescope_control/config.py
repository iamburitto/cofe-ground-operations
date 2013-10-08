from collections import OrderedDict
import re

class Config(OrderedDict):
    """The Config class provides a dictionary-like object which simplifies
    the acts of using 'key pair' configuration files. An example of such a
    file:

    #This is a comment
    junk 0
    mo_junk 0.1 #this is more junk
    fluff bananas #lol

    Suppose this file was saved as 'config.txt'. Then one could simply
    >>> config = Config('config.txt')
    >>> print config
    Config({'junk':0, 'mo_junk':0.1, 'fluff':'bananas'})
    >>> config['junk']
    0
    >>> config['junk'] = 27
    >>> #etc

    Changing the values of a key in an instance of the Config class will
    also change the contents of the configuration file. After the example
    shown above, the contents would be:
    
    #This is a comment
    junk 27
    mo_junk 0.1 #this is more comment
    fluff bananas #lol

    Keys are always strings in use, but data is automatically converted into
    numerical types. For instance, if you had a line like "0 1234", you would
    do "config['0']" to access the value. The value, on the other hand, would
    b the int 1234. If it is more convenient to denote a value in some other
    common base, either 2, 8, or 16, then you may write things like
    "key b10100111" or "key xFF0088" or "key o70312" (the last one is octal.)
    You may also write a floating point decimal like "key 1234.5678". This must
    be in base 10!
    """
    def __init__(self, fname):
        """fname is the filename for the configuration file"""
        self.fname = fname
        OrderedDict.__init__(self, self.__get_current_state())

    def __get_current_state(self):
        #This returns a list of tuples, one for each "key val" pair in
        #the config file.
        current_state = [] #accumulator variable
        with open(self.fname) as f:
            for index, line in enumerate(f):
                #Each line is stripped of leading and trailing whitespace.
                line = line.strip()
                #If the resultant line is empty, skip it!
                #(You can't have a key which is whitespace
                #with a value that is whitespace.)
                if line == '':
                    continue
                #If the line starts with a '#' then it is a comment.
                #comments are there own key, with an empty string as
                #the associated value
                if line.startswith('#'):
                    current_state.append((line, ['']))
                    continue
                #If this line isn't a comment, then split it into at most
                #three parts, the third part being reserved for comments.
                line = line.split(' ', 2)
                if len(line) < 2: #If there is only one piece after the split
                    #then something is wrong!
                    raise TypeError("Bad line :~ line #{}:{}".format(index, line[0]))
                #convert the input values to the correct type
                line[1] = self.__type_check(line[1])
                #add the (key, [val, comment]) pair to the accumulator
                current_state.append((line[0], line[1:]))
        return current_state

    def __type_check(self, val):
        #Type checks the val and converts to the correct value
        checks = [(re.compile("[0-9]+"), int), #decimal
                  (re.compile("x[0-9A-Fa-f]+"), lambda x: int(x[1:], 16)), #hex
                  (re.compile("o[0-7]+"), lambda x: int(x[1:], 8)), #octal
                  (re.compile("b[01]+"), lambda x: int(x[1:], 2)), #binary
                  (re.compile("[0-9]+.[0-9]+"), float), #decimal float
                  (re.compile("True|False"), eval),  #python and scheme-style bool
                  (re.compile("#t|#f"), lambda x: True if x=="#t" else False)]
        for pattern, func in checks:
            match = re.search(pattern, val)
            #match will be None if re.search can't find a match.
            #Thankfully, 'and' returns imediately with the first non-True value
            if match and match.group(0)==val:
                val = func(val)
                return val
        #if the val doesn't match any pattern, then leave it as a string
        return val

    def __getitem__(self, key):
        #the value associated with key is the
        #first value in the associated list.
        return OrderedDict.__getitem__(self, key)[0]

    def __getitem(self, key):
        #returns the list associated with a key
        return OrderedDict.__getitem__(self, key)

    def __setitem(self, key, val):
        return OrderedDict.__setitem__(self, key, val)

    def __setitem__(self, key, val):
        #updates the contents of the file and the
        #dictionary at the same time.
        #currently, if you try to set a value equal to a list,
        #the actual list value associated with the key is replaced
        #not just the value the user is allowed to see. This is
        #because I have not added "list" typechecking logic yet.
        if isinstance(val, list):
            self.__setitem(key, val)
        else:
            #also, I did not add logic for when you try to
            #create a new key, TODO!
            if key in self:
                vals = self.__getitem(key) #get the val, comment list
                vals[0] = val #change the val
                self.__setitem(key, vals) #add the change
            with open(self.fname, 'w') as f:
                #rewrite every key val #comment to file
                for k in self:
                    print >>f, ' '.join([k]+map(str, self.__getitem(k)))
        return

    def __repr__(self):
        #Make the repr pretty. not functional
        #(i.e. calling eval(config_object) won't work)
        string = OrderedDict.__repr__(self).strip('Config([])')
        string = string.replace("', ", ":").translate(None, '()')
        return "Config({"+string+"})"

    def __str__(self):
        return self.__repr__()
