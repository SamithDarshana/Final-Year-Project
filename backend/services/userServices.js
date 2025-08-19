const User = require("../models/User");
const bcrypt = require("bcryptjs");

async function registerUser(name, email, password, role) {
  // Check if email already exists
  const existingUser = await User.findOne({ email });
  if (existingUser) throw new Error("Email already registered");

  // Hash password
  const salt = await bcrypt.genSalt(10);
  const hashedPassword = await bcrypt.hash(password, salt);

  // Save user
  const user = new User({
    name,
    email,
    password: hashedPassword,
    role,
  });

  await user.save();
  return user;
}

async function loginUser(email, password) {
  const user = await User.findOne({ email });
  if (!user) return null;

  const isMatch = await bcrypt.compare(password, user.password);
  if (!isMatch) return null;

  return user;
}

async function getAllUsers() {
  return await User.find();
}

module.exports = { registerUser, loginUser, getAllUsers };
