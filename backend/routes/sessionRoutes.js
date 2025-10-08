const router = require("express").Router();

const {
  startSession,
  endSession,
  presenter,
  participant,
} = require("../controllers/sessionController");

router.post("/startSession", startSession);

router.post("/endSession/:code", endSession);

router.get("/presenter", presenter);

router.get("/participant", participant);

module.exports = router;
