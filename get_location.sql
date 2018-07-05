SELECT
	xy.MAP_X as x,
	xy.MAP_Y as y,
    ll.LLPG_LatLng_Lat AS lat,
    ll.LLPG_LatLng_Lng AS lng,
    xy.ADDRESS_STR AS addr
FROM
    WaSSCollections.dbo.LLPG_ADDRESS_CURRENT_SPATIAL xy
INNER JOIN
    WaSSCollections.dbo.LLPG_LatLng AS ll
ON xy.UPRN = ll.LLPG_LatLng_UPRN
WHERE ll.LLPG_LatLng_UPRN = (?)