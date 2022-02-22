
__all__ = (
	"FizzBuzzSeqGenerator",
)

class FizzBuzzSeqGenerator:
	"""
	FizzBuzz Sequence generator.

	Use as following:
		fizzbuzz = FizzBuzz(3, 5, 100, "fizz", "buzz")
		seq = fizzbuzz.sequence()
	"""
	
	def __init__(self, int1, int2, limit, str1, str2, maxLimit=1000000, maxStrLen=100):
		self.maxLimit = maxLimit
		self.maxStrLen = maxStrLen
		self.int1 = int1
		self.int2 = int2
		self.limit = limit
		self.str1 = str1
		self.str2 = str2
		self._validate()

	def _validate(self):
		try:
			self.int1 = int(self.int1)
			self.int2 = int(self.int2)
			self.limit = int(self.limit)
		except ValueError:
			raise ValueError("int1, int2 and limit must be integers")

		if not self.int1 or not self.int2:
			raise ValueError(f"int1 and int2 cannot be null")
		if self.limit <= 1:
			raise ValueError(f"the provided limit ({self.limit}) "
                             "cannot be lower or equal to 1")
		if self.limit > self.maxLimit:
			raise ValueError(f"limit {self.limit} cannot be bigger that {self.maxLimit}")
		if self.int1 > self.limit or self.int2 > self.limit:
			raise ValueError(f"int1 ({self.int1}) and int2 ({self.int2}) "
                             f"cannot be bigger than the limit ({self.limit})")
		if not isinstance(self.str1, str) or not isinstance(self.str2, str):
			raise ValueError(f"str1 and str2 must be of type string")
		if len(self.str1) > self.maxStrLen or len(self.str2) > self.maxStrLen:
			raise ValueError(f"max len of str1 and str2 is {self.maxStrLen}")
		forbidden = [",", "_"]
		for car in forbidden:
			if car in self.str1 or car in self.str2:
				raise ValueError(f"characters {forbidden} are forbidden")

	def sequence(self):
		res = ""
		for pos in range(1, self.limit + 1):
			replaced = False
			if not (pos % self.int1):
				res += self.str1
				replaced = True
			if not (pos % self.int2):
				res += self.str2
				replaced = True
			if not replaced:
				res += f"{pos}"

			res += ","

		# remove the trailing ","
		return res[:-1]
			
