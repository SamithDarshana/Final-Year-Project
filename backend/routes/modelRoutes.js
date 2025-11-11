const express = require("express");
const router = express.Router();

const {
  start,
  stop,
  setMode,
  getMode,
} = require("../controllers/modelController");

router.post("/start", start);

router.post("/stop", stop);

router.post("/set_mode", setMode);

router.get("/get_mode", getMode);

module.exports = router;
