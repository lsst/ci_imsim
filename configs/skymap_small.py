config.skyMap["discrete"].projection = "TAN"
# center of tract 3828 patch 3,3=24
config.skyMap["discrete"].raList = [56.64971166122064]
config.skyMap["discrete"].decList = [-36.4462532139527947602893]
# 28000 (pix as in DC2 skymap; 7x4000pix patches)/3600(deg/asec)*0.2(asec/pix)/2(diam-to-rad) = 7/9
# Then round down to 6.4/9, otherwise it seems to make 8x8 patches
config.skyMap["discrete"].radiusList = [6.4/9]
config.skyMap["discrete"].rotation = 0.0
config.skyMap["discrete"].patchBorder = 100
config.skyMap["discrete"].tractOverlap = 0.0
config.skyMap["discrete"].pixelScale = 0.2
config.skyMap["discrete"].patchInnerDimensions = [2000, 2000]
config.skyMap.name = "discrete"
config.name = 'discrete/ci_imsim/2k'
