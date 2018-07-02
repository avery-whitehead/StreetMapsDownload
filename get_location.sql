SELECT
    ll.LLPG_LatLng_Lat AS lat,
    ll.LLPG_LatLng_Lng AS lng,
    addr.ADDRESS_STR AS address
FROM
    WaSSCollections.dbo.LLPG_LatLng AS ll
INNER JOIN
    WaSSCollections.dbo.LLPG_ADDRESSES_SEARCH_CURRENT AS addr
ON ll.LLPG_LatLng_UPRN = addr.UPRN
WHERE ll.LLPG_LatLng_UPRN = (?)