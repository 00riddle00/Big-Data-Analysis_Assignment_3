// Initialize shard1 as a single-node replica set
// Must be run on shard1 container
rs.initiate({
  _id: "shard1rs",
  members: [{ _id: 0, host: "shard1:27017" }]
});
