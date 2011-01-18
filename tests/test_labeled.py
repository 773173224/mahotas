import numpy as np
import mahotas.labeled
def test_border():
    labeled = np.zeros((32,32), np.uint8)
    labeled[8:11] = 1
    labeled[11:14] = 2
    labeled[14:17] = 3
    labeled[10,8:] = 0
    b12 = mahotas.labeled.border(labeled, 1, 2)
    YX = np.where(b12)
    YX = np.array(YX).T
    b13 = mahotas.labeled.border(labeled, 1, 3)

    assert not np.any(b13)
    assert np.any(b12)
    assert (11,0) in YX
    assert (11,1) in YX
    assert (12,1) in YX
    assert (12,9) not in YX

    b13 = mahotas.labeled.border(labeled, 1, 3, always_return=0)
    assert b13 is None

def _included(a,b):
    assert np.sum(a&b) == a.sum()

def test_borders():
    labeled = np.zeros((32,32), np.uint8)
    labeled[8:11] = 1
    labeled[11:14] = 2
    labeled[14:17] = 3
    labeled[10,8:] = 0
    borders = mahotas.labeled.borders(labeled)
    _included(mahotas.labeled.border(labeled,1,2), borders)
    _included(mahotas.labeled.border(labeled,1,23), borders)
    _included(mahotas.labeled.border(labeled,1,3), borders)
    _included(mahotas.labeled.border(labeled,2,3), borders)

    union = np.zeros_like(borders)
    for i in xrange(4):
        for j in xrange(4):
            if i != j:
                union |= mahotas.labeled.border(labeled, i, j)

    assert np.all(union == borders)

