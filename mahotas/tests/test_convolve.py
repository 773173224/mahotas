import numpy as np
import mahotas
import mahotas.convolve
from mahotas.convolve import convolve1d, gaussian_filter
import mahotas._filters
from os import path
from nose.tools import raises

def test_compare_w_ndimage():
    from scipy import ndimage
    A = np.arange(34*340).reshape((34,340))%3
    B = np.ones((3,3), A.dtype)
    for mode in mahotas._filters.modes:
        assert np.all(mahotas.convolve(A, B, mode=mode) == ndimage.convolve(A, B, mode=mode))

def test_22():
    A = np.arange(1024).reshape((32,32))
    B = np.array([
        [0,1],
        [2,3],
        ])
    C = np.array([
        [0,1,0],
        [2,3,0],
        [0,0,0],
        ])
    AB = mahotas.convolve(A,B)
    AC = mahotas.convolve(A,C)
    assert AB.shape == AC.shape
    assert np.all(AB == AC)


@raises(ValueError)
def test_mismatched_dims():
    f = np.arange(128*128, dtype=float).reshape((128,128))
    filter = np.arange(17,dtype=float)-8
    filter **= 2
    filter /= -16
    np.exp(filter,filter)
    mahotas.convolve(f,filter)

def test_convolve1d():
    f = np.arange(64*4).reshape((16,-1))
    n = [.5,1.,.5]
    for axis in (0,1):
        g = convolve1d(f, n, axis)
        assert g.shape == f.shape

@raises(ValueError)
def test_convolve1d_2d():
    f = np.arange(64*4).reshape((16,-1))
    n = np.array([[.5,1.,.5],[0.,2.,0.]])
    convolve1d(f, n, 0)

luispedro_jpg = lambda: mahotas.imread(path.join(
    path.abspath(path.dirname(__file__)),
                '..',
                'demos',
                'data',
                'luispedro.jpg'), 1)


def test_gaussian_filter():
    from scipy import ndimage
    f = luispedro_jpg()
    for s in (4.,8.,12.):
        g = gaussian_filter(f, s)
        n = ndimage.gaussian_filter(f, s)
        assert np.max(np.abs(n - g)) < 1.e-5

def test_gaussian_order():
    im = np.arange(64*64).reshape((64,64))
    for order in (1,2,3):
        g_mat = mahotas.gaussian_filter(im, 2., order=order)

def test_gaussian_order_high():
    im = np.arange(64*64).reshape((64,64))
    @raises(ValueError)
    def gaussian_order(order):
        mahotas.gaussian_filter(im, 2., order=order)
    yield gaussian_order, 4
    yield gaussian_order, 5
    yield gaussian_order, -3
    yield gaussian_order, -1
    yield gaussian_order, 1.5

def test_haar():
    image = luispedro_jpg()
    image = image[:256,:256]
    wav = mahotas.haar(image)

    assert wav.shape == image.shape
    assert np.allclose((image[0].reshape((-1,2)).mean(1)+image[1].reshape((-1,2)).mean(1))/2, wav[0,:128]/2.)
    assert np.abs(np.mean(image**2) - np.mean(wav**2)) < 1.

    image = luispedro_jpg()
    wav =  mahotas.haar(image, preserve_energy=False)
    assert np.abs(np.mean(image**2) - np.mean(wav**2)) > 16.
    wav =  mahotas.haar(image, inline=True)
    assert id(image) == id(wav)

def test_ihaar():
    image = luispedro_jpg()
    image = image[:256,:256]
    wav = mahotas.haar(image)
    iwav = mahotas.ihaar(wav)
    assert np.allclose(image, iwav)
    iwav = mahotas.ihaar(wav, preserve_energy=False)
    assert not np.allclose(wav, iwav)
    iwav =  mahotas.ihaar(wav, inline=True)
    assert id(iwav) == id(wav)


def test_daubechies():
    image = luispedro_jpg()
    image = image[:256,:256]
    wav = mahotas.haar(image, preserve_energy=False)
    dau = mahotas.daubechies(image, 'D2')

    assert wav.shape == dau.shape
    assert np.allclose(dau, wav)

def test_3d_wavelets_error():
    @raises(ValueError)
    def call_f(f):
        f(np.arange(4*4*4).reshape((4,4,4)))

    yield call_f, mahotas.haar
    yield call_f, mahotas.ihaar
    yield call_f, lambda im: mahotas.daubechies(im, 'D4')

def test_wavelets_inline():
    def inline(f):
        im = np.arange(16, dtype=float).reshape((4,4))
        t = f(im, inline=True)
        assert id(im) == id(t)

    yield inline, mahotas.haar
    yield inline, lambda im,inline: mahotas.daubechies(im, 'D4', inline=inline)

