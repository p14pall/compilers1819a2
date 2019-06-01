import plex

class ParseError(Exception):
	pass
	
class MyParser:
	def __init__(self):
		AND_OP = plex.Str('and')
		OR_OP = plex.Str('or')
		XOR_OP = plex.Str('xor')
		ASSIGN_OP = plex.Str('=')
		OPEN_PAR = plex.Str('(')
		CLOSE_PAR = plex.Str(')')
		PRINT_TOKEN = plex.Str('print')
		DIGIT = plex.Range('09')
		BINARY = plex.Range('01')
		LETTER = plex.Range('AZaz')
		B_NUM = plex.Rep1(BINARY)
		SPACE = plex.Any(' \n\t')
		ID_TOKEN = LETTER + plex.Rep(LETTER|DIGIT)
		
		self.LEXICON = plex.Lexicon([
			(AND_OP, 'and'),
			(OR_OP, 'or'),
			(XOR_OP, 'xor'),
			(SPACE, plex.IGNORE),
			(ASSIGN_OP, '='),
			(PRINT_TOKEN, 'print'),
			(OPEN_PAR, '('),
			(CLOSE_PAR, ')'),
			(ID_TOKEN, 'id'),
			(B_NUM, 'b_num')
			])
			
		self.ST = {}
			
	def create_scanner(self, fp):
		self.SCANNER = plex.Scanner(self.LEXICON, fp)
		self.LA, self.TEXT = self.next_token()
		
	def next_token(self):
		return self.SCANNER.read()
		
	def match(self, token):
		if self.LA == token:
			self.LA, self.TEXT = self.next_token()
		else:
			raise ParseError("{} instead of {}".format(self.LA, token))
	
	def parse(self, fp):
		self.create_scanner(fp)
		self.stmt_list()
		
	def stmt_list(self):
		if self.LA == 'id' or self.LA == 'print':
			self.stmt()
			self.stmt_list()
		elif self.LA == None:
			return
		else:
			raise ParseError("{} is not 'id' or 'print' token as expected".format(self.LA))
			
	def stmt(self):
		if self.LA == 'id':
			varname = self.TEXT
			self.match('id')
			self.match('=')
			self.ST[varname] = self.expr()
		elif self.LA == 'print':
			self.match('print')
			print('{:b}'.format(self.expr()))
		else:
			raise ParseError("{} is not 'id' or 'print' token as expected".format(self.LA))
			
	def expr(self):
		if self.LA == '(' or self.LA == 'id' or self.LA == 'b_num':
			t = self.term()
			while self.LA == 'xor':
				self.match('xor')
				t2 = self.term()
				t ^= t2
			if self.LA == 'id' or self.LA == 'print' or self.LA ==')' or self.LA is None:
				return t
			raise ParseError("{} is not 'id', 'print', ')' or 'None' token as expected".format(self.LA))
		else:
			raise ParseError("{} is not '(', 'id' or 'b_num' token as expected".format(self.LA))
			
	def term(self):
		if self.LA == '(' or self.LA == 'id' or self.LA == 'b_num':
			f = self.factor
			while self.LA == 'or':
				self.match('or')
				f2 = self.factor()
				f |= f2
			if self.LA == 'xor' or self.LA == 'id' or self.LA == 'print' or self.LA == ')' or self.LA is None:
				return f
			raise ParseError("{} is not 'xor', 'id', 'print', ')' or 'None' token as expected".format(self.LA))
		else:
			raise ParseError("{} is not '(', 'id' or 'b_num' as expected".format(self.LA))
				
	def factor(self):
		if self.LA == '(' or self.LA == 'id' or self.LA == 'b_num':
			a = self.atom()
			while self.LA == 'and':
				self.match('and')
				a2 = self.atom()
				a &= a2
			if self.LA == 'or' or self.LA == 'xor' or self.LA == 'id' or self.LA == 'print' or self.LA is None:
				return a
			raise ParseError("{} is not 'or' ,'xor', 'id', 'print', ')' or 'None' token as expected".format(self.LA))
		else:
			raise ParseError("{} is not '(', 'id' or 'b_num' as expected".format(self.LA))
			
	def atom(self):
		if self.LA == '(':
			self.match('(')
			e = self.expr()
			self.match(')')
			return e
		elif self.LA == 'id':
			varname = self.TEXT
			self.match('id')
			if varname in self.ST:
				return self.ST[varname]
			raise ParseError("{} is not in self.ST as expected".format(varname))
		elif self.LA == ('b_num'):
			b_val = int(self.TEXT, 2)
			self.match('b_num')
			return b_val
		else:
			raise ParseError("{} is not '(', 'id' or 'b_num' as expected".format(self.LA))
			
parser = MyParser
with open('test.txt', 'r') as fp:
	parser.parse(fp)
