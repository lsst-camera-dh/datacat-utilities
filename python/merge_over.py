# Two command-line arguments:  Name of a file containing a list of the single-
# sensor FITS images and the name of the output file

# Merge a set of single CCD images into a (large) FITS file
# assumed to be in S00, SO1, ... order.  This version modifies
# the header keywords to have overscan regions INCLUDED
# as part of the image
# The resulting image can be assembled in ds9 with
# ds9 -mosaicimage wcsq filename.fits
# And in ds9, View -> Multiple WCS -> WCS q
# will display a continuous pixel coordinate system
# Please note that only the WCS q coordinate system has been modified to
# include the overscan regions

import astropy.io.fits as fits
import numpy as np
import sys

# Read the list of files
io = open(sys.argv[1], "r")
infiles = []
for line in io:
    infiles.append(line.rstrip())
io.close()

hdulist = fits.HDUList()

# Take primary header from the first file in the list
hdu = fits.open(infiles[0])
# Extract the CCD_MANU keyword
ccdtype = hdu[0].header['CCD_MANU']
hdulist.append(hdu[0])
preh, overh = 0, 0  # notation of LCA-13501 - no pre- or over-scan
overv = 0

count = 0
for infile in infiles:
    hdu = fits.open(infile)

    # Notation below is from LCA-13501
    Cp = np.divide(count, 3)
    Cs = count - 3 * Cp  # modulo
    count += 1

    for i in range(1, 17):
        hdutemp = hdu[i]
        # Extract NAXIS1, NAXIS2, and the EXTNAME to redefine DATASEC and DETSEC
        # to select the entire segment, and still have it assembled with the
        # correct orientation and relative placement in ds9
        naxis1 = hdutemp.header['NAXIS1']
        naxis2 = hdutemp.header['NAXIS2']
        extname = hdutemp.header['EXTNAME']
        # Extract Sx, Sy (Segment 'x' and 'y' addresses) from EXTNAME
        Sx, Sy = int(extname[7]), int(extname[8])
        Sp, Ss = Sx, Sy  # for convenience of notation
        dimh, dimv = naxis1, naxis2
        ccdax, ccday = dimv * 2, dimh * 8
        # Equations below are from LCA-13501
        if ccdtype == 'E2V':
            dsx1 = (Sy * dimh + 1) * (1 - Sx) + (Sy + 1) * dimh * Sx
            dsx2 = (Sy + 1) * dimh * (1 - Sx) + (Sy * dimh + 1) * Sx
            dsy1 = 2 * dimv * (1 - Sx) + Sx
            dsy2 = (dimv + 1) * (1 - Sx) + dimv * Sx
            ccdpx, ccdpy = ccdax + 193, ccday + 104
            gap_inx, gap_iny = 28, 25
            gap_outx, gap_outy = 26.5, 25
            crval1q = gap_outy + (ccdpy - ccday) / 2 + Cs * (8 * dimh + gap_iny + ccdpy - ccday) + Sp * (
                    dimh + 1) + Ss * dimh + (2 * Sp - 1) * preh  # noqa
            crval2q = Sp * (2 * dimv + 1) + gap_outx + (ccdpx - ccdax) / 2 + Cp * (
                    2 * dimv + gap_inx + ccdpx - ccdax)  # noqa
        else:
            dsx1 = (Sy + 1) * dimh
            dsx2 = Sy * dimh + 1
            dsy1 = 2 * dimv * (1 - Sx) + Sx
            dsy2 = (dimv + 1) * (1 - Sx) + dimv * Sx
            ccdpx, ccdpy = ccdax + 198, ccday + 126
            gap_inx, gap_iny = 27, 27
            gap_outx, gap_outy = 26, 26
            crval1q = gap_outy + (ccdpy - ccday) / 2 + Cs * (8 * dimh + gap_iny + ccdpy - ccday) \
                + (Ss + 1) * dimh + 1 - preh
            crval2q = Sp * (2 * dimv + 1) + gap_outx + (ccdpx - ccdax) / 2 + Cp * \
                (2 * dimv + gap_inx + ccdpx - ccdax)

        datasec = '[1:' + str(naxis1) + ',1:' + str(naxis2) + ']'
        detsec = '[' + str(dsx1) + ':' + str(dsx2) + ',' + \
                 str(dsy1) + ':' + str(dsy2) + ']'
        detsize = '[1:' + str(naxis1 * 8) + ',1:' + str(naxis2 * 2) + ']'
        hdutemp.header['DATASEC'] = datasec
        hdutemp.header['DETSEC'] = detsec
        hdutemp.header['DETSIZE'] = detsize
        hdutemp.header['CRVAL1Q'] = crval1q
        hdutemp.header['CRVAL2Q'] = crval2q
        hdulist.append(hdutemp)

hdulist.writeto(sys.argv[2])
