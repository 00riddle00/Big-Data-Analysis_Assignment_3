// Initialize shard2 as a single-node replica set
// Must be run on shard2 container
rs.initiate({
  _id: "shard2rs",
  members: [{ _id: 0, host: "shard2:27017" }]
});
