config.skyMap["discrete"].projection = "TAN"
# center of tract 3828 patch 3,3=24
config.skyMap["discrete"].raList = [56.64971166122064]
config.skyMap["discrete"].decList = [-36.4462532139527947602893]
# We want 13x13 patches so that the central patch is the central quarter
# of the central patch in the 4k x 4k skymap
# this does also mean that the tracts will be a little smaller, but that's ok
# A tract 26000 pix across (13x2000pix patches)
# 26000/3600(deg/asec)*0.2(asec/pix)/2(diam-to-rad) = 13/18 = 6.5/9
# Rounding down to 6.4/9 works just as it did for the 4kx4k skymap
config.skyMap["discrete"].radiusList = [6.4/9]
config.skyMap["discrete"].rotation = 0.0
config.skyMap["discrete"].patchBorder = 100
config.skyMap["discrete"].tractOverlap = 0.0
config.skyMap["discrete"].pixelScale = 0.2
config.skyMap["discrete"].patchInnerDimensions = [2000, 2000]
config.skyMap.name = "discrete"
config.name = 'discrete/ci_imsim/2k'
