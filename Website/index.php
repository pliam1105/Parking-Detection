<?php
$servername = "localhost";

$dbname = "id19492879_pliamdb";
$username = "id19492879_pliam";
$password = "Pli@m12112005";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$result_last_update = $conn->query("select max(datetime) as datetime from parking_spaces");
$row_upd = $result_last_update->fetch_assoc();
$last_update = strtotime($row_upd['datetime']);
$cur_time = strtotime(gmdate("Y-m-d H:i:s"));
$dif_upd = intval(($cur_time-$last_update)/60);//in minutes
if($dif_upd <= 15){
    $color = "green";
    $time_text = "Last updated ".$dif_upd." min ago";
}else{
    $color = "red";
    $time_text = "Not updated in the last 15 minutes </br> Please refresh shortly";
}
$result_ids = $conn->query("select * from parking_ids");
$info_ids = array();
$park_data = array();
$glob_cnt = 0;
while ($row_id = $result_ids->fetch_assoc()) {
    $row_id['cnt'] = 0;
    $result_park = $conn->query("select * from parking_info where parking_id=" . $row_id['parking_id'] . " order by space_id asc");
    $loc_cnt = 0;
    while ($row = $result_park->fetch_assoc()) {
        $row2 = array_map('doubleval', $row);
        $row2['is_empty'] = false;
        $row2['id'] = $glob_cnt + $loc_cnt;
        array_push($park_data, $row2);
        $loc_cnt++;
    }
    $result = $conn->query("select * from parking_spaces where parking_id=" . $row_id['parking_id'] . " and (entry_id = (select max(entry_id) from parking_spaces where parking_id=" . $row_id['parking_id'] . ")) order by space_id asc");
    $data = array();
    $cnt1 = 0;
    while ($row = $result->fetch_assoc()) {
        if ($row['is_empty'] == '1') {
            $row_id['cnt']++;
            $park_data[$glob_cnt + $cnt1]['is_empty'] = true;
        }
        $cnt1++;
    }
    $glob_cnt += $loc_cnt;
    array_push($info_ids, $row_id);
    //echo json_encode($park_data);
}
$conn->close();
?>
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title>View Parking Spaces</title>
    <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css" rel="stylesheet">
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
        }

        #map {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 100%;
            height: auto;
        }

        .mapboxgl-popup-content {
            text-align: center;
            font-family: 'Open Sans', sans-serif;
        }

        .marker {
            background-size: cover;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
        }

        .last_updated {
            position: absolute;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 18px;
            right: 0;
            top: 0;
            padding-right: 8px;
            padding-top: 8px;
            padding-bottom: 8px;
            padding-left: 8px;
            color: white;
            border-radius: 10px;
        }
    </style>
</head>

<body>
    <script src="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.2.2/mapbox-gl-draw.js"></script>
    <link rel="stylesheet" href="https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.2.2/mapbox-gl-draw.css" type="text/css">
    <div id="map"></div>
    <?php echo "<div class='last_updated' style='background-color: ".$color."'>".$time_text."</div>" ?>
    <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoicGxpYW1wYXMiLCJhIjoiY2psbWRiczM5MTNneTNwbmprN2FoaG5jNSJ9.wNg62r6BQDH0TCEGwdPJJw';
        const map = new mapboxgl.Map({
            container: 'map', // container ID
            style: 'mapbox://styles/mapbox/satellite-v9', // style URL
            center: [22.9510848,40.652398], // starting position [lng, lat]
            zoom: 19 // starting zoom
        });
        map.on('load', () => {
            // Add a data source containing GeoJSON data.
            map.addSource('spaces', {
                'type': 'geojson',
                'data': {
                    "type": "FeatureCollection",
                    "features": [
                        <?php
                        foreach ($park_data as $data_cur) {
                            echo "{'type': 'Feature',
                        'id': " . $data_cur['id'] . ",
                        'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[
                        [" . $data_cur['point1lng'] . "," . $data_cur['point1lat'] . "],
                        [" . $data_cur['point2lng'] . "," . $data_cur['point2lat'] . "],
                        [" . $data_cur['point3lng'] . "," . $data_cur['point3lat'] . "],
                        [" . $data_cur['point4lng'] . "," . $data_cur['point4lat'] . "],
                        [" . $data_cur['point1lng'] . "," . $data_cur['point1lat'] . "]
                        ]]
                        }},";
                        }
                        ?>
                    ]
                }
            });
            // Add a new layer to visualize the parking
            map.addLayer({
                'id': 'spaces_fill',
                'type': 'fill',
                'minzoom': 15,
                'source': 'spaces',
                'layout': {},
                'paint': {
                    'fill-color': [
                        'case',
                        ['boolean', ['feature-state', 'empty'], false],
                        '#00ff00', // if selected true, paint in blue
                        '#ff0000' // else paint in gray
                    ],
                    'fill-opacity': 0.7
                }
            });
            <?php
            foreach ($park_data as $data_cur) {
                echo "map.setFeatureState({
                    source: 'spaces',
                    id: " . $data_cur['id'] . ",
                    }, {
                        empty: " . ($data_cur['is_empty'] ? "true" : "false") . "
                    });";
            }
            ?>
            //Add a new layer for the parking itself
            map.addSource('circles', {
                'type': 'geojson',
                'data': {
                    "type": "FeatureCollection",
                    "features": [
                        <?php
                        foreach ($info_ids as $info_id) {
                            echo "{'type': 'Feature',
                            'id': ".$info_id['parking_id'].",
                            'geometry': {
                            'type': 'Point',
                            'coordinates': [" . $info_id['centerlng'] . "," . $info_id['centerlat'] . "]}
                            },";
                        }
                        ?>
                    ]
                }
            });
            // Add a new layer to visualize the overview of the parkings
            map.addLayer({
                id: "fill_circles",
                // type: "symbol",
                type: "circle",
                source: "circles",
                maxzoom: 15,
                // layout: { 
                //   "icon-image": "custom-marker"
                // },
                paint: {
                    'circle-radius': 10,
                    'circle-color':[
                        'case',
                        ['boolean', ['feature-state', 'has_spaces'], false],
                        '#00ff00', 
                        '#ff0000' 
                    ]
                }
            });
            <?php
            foreach ($info_ids as $info_id) {
                echo "map.setFeatureState({
                    source: 'circles',
                    id: " . $info_id['parking_id'] . ",
                    }, {
                        has_spaces: " . ($info_id['cnt']==0 ? "false" : "true") . "
                    });";
                echo "// create a HTML element for each feature
                el = document . createElement('div');
                el . className = 'marker';";
                echo "new mapboxgl.Marker(el)
                  .setLngLat([" . $info_id['centerlng'] . "," . $info_id['centerlat'] . "])
                  .addTo(map);";
                echo "new mapboxgl.Marker(el)
                .setLngLat([" . $info_id['centerlng'] . "," . $info_id['centerlat'] . "])
                .setPopup(new mapboxgl.Popup({ offset: 0 }) // add popups
                    .setHTML('<h1>Empty spaces: " . $info_id['cnt'] . "</h1>'))
                .addTo(map);";
            }
            ?>
        });
    </script>
</body>

</html>