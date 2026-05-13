// Register both shards with the mongos router
sh.addShard("shard1rs/shard1:27017");
sh.addShard("shard2rs/shard2:27017");

// Enable sharding on the AIS database
sh.enableSharding("ais_db");

// Shard the raw vessels collection by hashed MMSI
// Hashed sharding ensures even data distribution across shards
sh.shardCollection("ais_db.vessels_raw", { MMSI: "hashed" });
