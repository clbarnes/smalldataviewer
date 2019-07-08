OFFSET = (10, 10, 10)
SHAPE = (20, 20, 20)
PADDED_SHAPE = tuple(s + o*2 for s, o in zip(SHAPE, OFFSET))
PAD_VALUE = 1
INTERNAL_PATH = 'volume'