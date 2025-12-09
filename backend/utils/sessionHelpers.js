function getParticipantList(session) {
  if (!session) return [];

  return Array.from(session.participants.entries()).map(([socketId, name]) => ({
    name,
    cameraOn: session.cameraStatus.get(name)?.active || false,
  }));
}

module.exports = { getParticipantList };
