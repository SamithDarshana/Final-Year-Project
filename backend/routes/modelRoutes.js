const express = require("express");
const router = express.Router();

const { start, stop } = require("../controllers/modelController");

router.post("/start", start);

router.post("/stop", stop);

module.exports = router;
